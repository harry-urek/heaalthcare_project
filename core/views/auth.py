from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from ..models import Patient
from ..serializers import UserSerializer

from django.core.exceptions import ObjectDoesNotExist


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
