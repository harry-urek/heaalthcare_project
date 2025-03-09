from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import ForeignKey, CharField, EmailField, TextField, BooleanField, DateField, IntegerField, TimeField

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Paitent(BaseModel):
    user  = ForeignKey(User, on_delete=models.CASCADE, related_name='paitent')
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    date_of_birth = DateField(blank= False, null=False)
    gender = CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ])
    phone = IntegerField(max_length=13)
    email = EmailField()
    address = TextField()
    medical_history = TextField(blank = True, null = True)
    
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    class Meta:
        ordering = ['created_at']
        
        
class Doctor(BaseModel):
    
    first_name = CharField(max_length=64)
    last_name = CharField(max_length=64)
    specilization = CharField(max_length=128)
    phone = IntegerField(max_length=13)
    email = EmailField()
    license = CharField(max_length=128)
    address = TextField()
    is_active = BooleanField(default=True)  
    
    def __str__(self):
        return f'Dr. {self.first_name} {self.last_name}'
    
    class Meta: 
        ordering = ['last_name', 'first_name']
        
        
class PaitentDoctorTable(BaseModel):
    paitent = ForeignKey(Paitent, on_delete=models.CASCADE, related_name='doctor_paitent')
    doctor = ForeignKey(Doctor, on_delete=models.CASCADE, related_name='paitent_doctor')
    appointment_date = DateField(blank=False, null=False)
    appointment_time = TimeField(blank=False, null=False)
    symptoms = TextField()
    diagnosis = TextField()
    prescription = TextField()
    is_active = BooleanField(default=True)
    
    def __str__(self):
        return f'{self.paitent} < ------ > {self.doctor}'
    
    class Meta:
        ordering = ['appointment_date']
        unique_together = ['paitent', 'doctor', 'appointment_date', 'appointment_time']
    
