from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import (
    ForeignKey,
    CharField,
    EmailField,
    TextField,
    BooleanField,
    DateField,
    IntegerField,
    TimeField,
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Patient(BaseModel):
    user = ForeignKey(User, on_delete=models.CASCADE, related_name="patient")
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    date_of_birth = DateField(blank=False, null=False)
    gender = CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
    )
    phone = TextField(max_length=13)
    email = EmailField()
    address = TextField()
    medical_history = TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["created_at"]


class Doctor(BaseModel):

    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    specialization = CharField(max_length=128)
    phone = TextField(max_length=13)
    email = EmailField()
    license = CharField(max_length=128)
    address = TextField()
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]


class PatientDoctorTable(BaseModel):
    patient = ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="doctor_patient"
    )
    doctor = ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_doctor")
    appointment_date = DateField(blank=False, null=False)
    appointment_time = TimeField(blank=False, null=False)
    symptoms = TextField()
    diagnosis = TextField()
    prescription = TextField()
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.patient} < ------ > {self.doctor}"

    class Meta:
        ordering = ["appointment_date"]
        unique_together = ["patient", "doctor", "appointment_date", "appointment_time"]
