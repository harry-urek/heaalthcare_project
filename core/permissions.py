from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a patient to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsPatientOwner(permissions.BasePermission):
    """
    Permission to only allow owners of a patient to manage its mappings.
    """

    def has_object_permission(self, request, view, obj):
        return obj.patient.user == request.user
