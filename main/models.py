from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Psychologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='psychologist_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    specialty = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)    
    cover_photo = models.ImageField(upload_to='cover_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    student_number = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)    
    psychologist = models.ForeignKey(
        Psychologist,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )

    def __str__(self):
        return self.name

class Appointment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    psychologist = models.ForeignKey('Psychologist', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Cita con {self.student.name} el {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
class PrivateNote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_private_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment = models.CharField(max_length=255, blank=True, null=True)  # Almacena el diagnóstico como texto
    state = models.CharField(max_length=50, blank=True, null=True)  # Nuevo campo para el estado
    recommendation = models.CharField(max_length=100, blank=True, null=True)  # Nuevo campo para la recomendación

    def __str__(self):
        return f"Nota de {self.created_by} para {self.student.name} el {self.created_at}"