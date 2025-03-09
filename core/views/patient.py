from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from ..models import Patient
from ..serializers import PatientSerializer
from ..permissions import IsOwnerOrReadOnly
from django.core.exceptions import ObjectDoesNotExist


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
