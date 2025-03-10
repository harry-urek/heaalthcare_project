from .patient import PatientListCreateView, PatientDetailView
from .doctor import DoctorListCreateView, DoctorDetailView
from .auth import RegisterView
from .patient_doctor import MappingListCreateView, MappingDetailView, PatientDoctorsView


__all__ = [
    PatientDetailView,
    PatientListCreateView,
    MappingListCreateView,
    MappingDetailView,
    PatientDoctorsView,
    DoctorListCreateView,
    DoctorDetailView,
    RegisterView,
]
