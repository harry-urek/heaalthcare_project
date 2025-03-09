from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from ..models import Patient, PatientDoctorTable
from ..serializers import (
    PatientDoctorMappingSerializer,
)
from ..permissions import IsOwnerOrReadOnly, IsPatientOwner
from django.core.exceptions import ObjectDoesNotExist


class MappingListCreateView(generics.ListCreateAPIView):

    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorTable.objects.filter(patient__user=self.request.user)

    def create(self, request, *args, **kwargs):
        if "patient" in request.data:
            try:
                patient_id = request.data["patient"]
                if not Patient.objects.filter(
                    id=patient_id, user=request.user
                ).exists():
                    return Response(
                        {
                            "status": "error",
                            "message": "You can only create mappings for your own patients",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except (ValueError, TypeError):
                return Response(
                    {"status": "error", "message": "Invalid patient ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {
                        "status": "success",
                        "message": "Doctor-patient mapping created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
        return Response(
            {
                "status": "error",
                "message": "Failed to create mapping",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# This class is a view in a Django REST framework API that lists doctors assigned to a specific
# patient, with permission checks.
class PatientDoctorsView(generics.ListAPIView):

    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs["patient_id"]

        try:
            patient = Patient.objects.get(id=patient_id)
            if patient.user != self.request.user:
                return PatientDoctorTable.objects.none()
            return PatientDoctorTable.objects.filter(patient_id=patient_id)
        except Patient.DoesNotExist:
            return PatientDoctorTable.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            patient_id = self.kwargs["patient_id"]
            if Patient.objects.filter(id=patient_id).exists():
                if not Patient.objects.filter(
                    id=patient_id, user=request.user
                ).exists():
                    return Response(
                        {
                            "status": "error",
                            "message": "You don't have permission to view this patient's doctors",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                return Response(
                    {
                        "status": "success",
                        "message": "No doctors assigned to this patient",
                        "data": [],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "message": "Patient not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})


# The `MappingDetailView` class retrieves and serializes a specific `PatientDoctorMapping` instance
# based on the authenticated user's ownership.
class MappingDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = (permissions.IsAuthenticated, IsPatientOwner)

    def get_queryset(self):
        return PatientDoctorTable.objects.filter(patient__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": "success", "data": serializer.data})
        except ObjectDoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Mapping not found or you don't have permission to view it",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    """
    This Python function deletes a doctor-patient mapping and returns a success message or an error
    message if deletion fails.
    
    :param request: The `request` parameter in the `destroy` method is typically an object that contains
    information about the incoming HTTP request, such as headers, user authentication details, and
    request data. It is commonly used in Django REST framework views to access information about the
    request being made to the API endpoint
    :return: The `destroy` method is returning a Response object with a JSON payload containing the
    status and message of the operation. If the deletion is successful, it returns a success message
    with a status code of 204 (NO CONTENT). If an exception occurs during the deletion process, it
    returns an error message with a status code of 400 (BAD REQUEST) along with the details of the
    exception.
    """

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            with transaction.atomic():
                self.perform_destroy(instance)
                return Response(
                    {
                        "status": "success",
                        "message": "Doctor-patient mapping deleted successfully",
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Failed to delete mapping: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
