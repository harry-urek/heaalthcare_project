from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    EmailField,
    IntegerField,
    DateField,
    TimeField,
    BooleanField,
    ValidationError,
    ReadOnlyField,
)
from django.contrib.auth.models import User
from .models import Patient, Doctor, PatientDoctorTable
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from datetime import date


# This class is a serializer in Python for creating and validating user data, including fields for
# username, password, email, and name.
class UserSerializer(ModelSerializer):

    password = CharField(write_only=True)
    confirm_password = CharField(write_only=True)
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "email",
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(f"A user with email : {value} already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError(f"A user with username : {value} already exists")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Passwords do not match")

        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )

        return user


# The `PatientSerializer` class in Python defines validation rules and data creation logic for a
# Patient model.
class PatientSerializer(ModelSerializer):

    class Meta:
        model = Patient
        fields = "__all__"
        reads_only_fields = ("user", "created_at", "updated_at")

    def validate_phone(self, value):
        if not re.match(r"^\+?[0-9]{10,15}$", value):
            raise ValidationError(
                "Phone number must be between 10-15 digits and may include a + prefix."
            )
        return value

    def validate_date_of_birth(self, value):
        if value > date.today():
            raise ValidationError("Date of birth cannot be in future")
        return value

    def validate_email(self, value):
        if value and not re.match(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value
        ):
            raise ValidationError("Please enter a valid email address.")
        if Patient.objects.filter(email=value).exists():
            raise ValidationError(f"A patient with email : {value} already exists")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["user"] = request.user
        return super().create(validated_data)


# The `DoctorSerializer` class in Python defines serialization behavior for the Doctor model,
# including validation for phone numbers and emails.
class DoctorSerializer(ModelSerializer):

    class Meta:
        model = Doctor
        fields = "__all__"
        reads_only_fields = ("created_at", "updated_at")

    def validate_phone(self, value):
        if not re.match(r"^\+?[0-9]{10,15}$", value):
            raise ValidationError(
                "Phone number must be between 10-15 digits and may include a + prefix."
            )
        return value

    def validate_email(self, value):
        if Doctor.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise ValidationError(f"A doctor with this email : {value} already exists.")
        return value

    def create(self, validated_data):
        return super().create(validated_data)


# The `PatientDoctorMappingSerializer` class in Python defines serialization logic for mapping
# patients to doctors, including validation rules.


class PatientDoctorMappingSerializer(ModelSerializer):

    patient_name = ReadOnlyField(source="patient.__str__")
    doctor_name = ReadOnlyField(source="doctor.__str__")

    class Meta:
        model = PatientDoctorTable
        fields = "__all__"
        reads_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        patient = data.get("patient")
        doctor = data.get("doctor")

        if (
            self.instance
            and patient == self.instance.patient
            and doctor == self.instance.doctor
        ):
            return data

        if PatientDoctorTable.objects.filter(patient=patient, doctor=doctor).exists():
            raise ValidationError("This patient is already assigned to this doctor.")

        if self.context["request"].method != "GET":
            if patient.user != self.context["request"].user:
                raise ValidationError(
                    "You don't have permission to assign doctors to this patient."
                )

        if data.get("assigned_date", date.today()) > date.today():
            raise ValidationError(
                {"assigned_date": "Assigned date cannot be in the future."}
            )

        return data
