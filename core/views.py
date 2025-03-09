from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db import transaction
from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    UserSerializer,
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsPatientOwner
from django.core.exceptions import ObjectDoesNotExist


# The `RegisterView` class in Python is a view that allows user registration with validation and
# response handling.
class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        # Only return patients that belong to the current user
        return Patient.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {
                        "status": "success",
                        "message": "User registered successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
        return Response(
            {
                "status": "error",
                "message": "Registration failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# The `PatientListCreateView` class in Python defines a view for listing and creating patient objects,
# with permission restrictions to only allow access to patients belonging to the current user.
class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Only return patients that belong to the current user
        return Patient.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {
                        "status": "success",
                        "message": "Patient created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
        return Response(
            {
                "status": "error",
                "message": "Failed to create patient",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# The `PatientDetailView` class in Python defines API views for retrieving, updating, and deleting
# patient objects belonging to the current user with appropriate error handling.
class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Only return patients that belong to the current user
        return Patient.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": "success", "data": serializer.data})
        except ObjectDoesNotExist:
            return Response(
                {"status": "error", "message": "Patient not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            with transaction.atomic():
                self.perform_update(serializer)
                return Response(
                    {
                        "status": "success",
                        "message": "Patient updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {
                "status": "error",
                "message": "Patient update failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"status": "success", "message": "Patient deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": "Patient delete failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# The `DoctorListView` class is a Django REST framework view that lists and creates Doctor objects
# with authentication and validation handling.
class DoctorListView(generics.ListCreateAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(
                    {
                        "status": "success",
                        "message": "Doctor created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers,
                )
        return Response(
            {
                "status": "error",
                "message": "Doctor creation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# The `DoctorDetailView` class is a Django REST framework view that allows retrieving, updating, and
# deleting instances of the `Doctor` model with authentication permissions.
class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": "success", "data": serializer.data})
        except ObjectDoesNotExist:
            return Response(
                {"status": "error", "message": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            with transaction.atomic():
                self.perform_update(serializer)
                return Response(
                    {
                        "status": "success",
                        "message": "Doctor updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {
                "status": "error",
                "message": "Doctor update failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):

        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"status": "success", "message": "Doctor deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": f"Failed to delete doctor: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# The class MappingListView is a generic view in Django REST framework for listing and creating
# objects.
class MappingListView(generics.ListCreateAPIView):

    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(patient__user=self.request.user)

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
                return PatientDoctorMapping.objects.none()
            return PatientDoctorMapping.objects.filter(patient_id=patient_id)
        except Patient.DoesNotExist:
            return PatientDoctorMapping.objects.none()

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
        return PatientDoctorMapping.objects.filter(patient__user=self.request.user)

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
