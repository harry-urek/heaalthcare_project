from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.db import transaction
from ..models import Doctor
from ..serializers import DoctorSerializer
from django.core.exceptions import ObjectDoesNotExist


class DoctorListCreateView(generics.ListCreateAPIView):

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
