from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    PatientDetailView,
    PatientListCreateView,
    DoctorDetailView,
    DoctorListCreateView,
    MappingListCreateView,
    MappingDetailView,
    PatientDoctorsView,
)


urlpatterns = [
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Patient endpoints
    path("patients/", PatientListCreateView.as_view(), name="patient-list"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patient-detail"),
    # Doctor endpoints
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list"),
    path("doctors/<int:pk>/", DoctorDetailView.as_view(), name="doctor-detail"),
    # Mapping endpoints
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list"),
    path(
        "mappings/patient/<int:patient_id>/",
        PatientDoctorsView.as_view(),
        name="patient-doctors",
    ),
    path("mappings/<int:pk>/", MappingDetailView.as_view(), name="mapping-detail"),
]
