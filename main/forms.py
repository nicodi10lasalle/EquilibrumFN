from django.core.validators import RegexValidator
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Psychologist, Student

# Validaciones comunes
phone_number_validator = RegexValidator(r'^\d{10}$', 'El número de teléfono debe contener exactamente 10 dígitos.')
age_validator = RegexValidator(r'^\d{1,2}$', 'La edad debe contener máximo 2 dígitos y solo números.')
specialty_validator = RegexValidator(r'^[a-zA-Z]{3,20}$', 'La especialidad debe contener solo letras y tener entre 3 y 20 caracteres.')
student_number_validator = RegexValidator(r'^\d{5,10}$', 'El número de estudiante debe contener entre 5 y 10 dígitos y solo números.')
reason_validator = RegexValidator(r'^[a-zA-Z\s]+$', 'La razón debe contener solo letras y un máximo de 50 caracteres.')
name_validator = RegexValidator(r'^[a-zA-Z\s]{3,20}$', 'El nombre debe contener solo letras y tener entre 3 y 20 caracteres.')

# Formulario de registro para psicólogos
class PsychologistRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=12,
        required=True,
        label='Nombre de usuario',
        help_text="12 caracteres como máximo 3 como mínimo. Solo letras o números. No se aceptan caracteres especiales.",
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'El nombre de usuario solo puede contener letras y números.')],
        error_messages={
            'max_length': 'El nombre de usuario no puede tener más de 12 caracteres.',
            'required': 'Este campo es obligatorio.',
        }
    )
    name = forms.CharField(max_length=20, label='Nombre', validators=[name_validator])
    age = forms.IntegerField(
        label='Edad',
        validators=[age_validator],
        error_messages={
            'invalid': 'Por favor, introduce una edad válida con máximo 2 dígitos.',
        }
    )
    email = forms.EmailField(required=True, label='Correo electrónico')
    specialty = forms.CharField(max_length=20, label='Especialidad', validators=[specialty_validator])
    phone_number = forms.CharField(max_length=10, label='Número de teléfono', validators=[phone_number_validator])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            psychologist = Psychologist(
                user=user,
                name=self.cleaned_data['name'],
                age=self.cleaned_data['age'],
                email=self.cleaned_data['email'],
                specialty=self.cleaned_data['specialty'],
                phone_number=self.cleaned_data['phone_number'],
            )
            psychologist.save()
        return user

# Formulario de registro para estudiantes
class StudentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=12,
        required=True,
        label='Nombre de usuario',
        help_text="12 caracteres como máximo 3 como mínimo. Solo letras o números. No se aceptan caracteres especiales.",
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'El nombre de usuario solo puede contener letras y números.')],
        error_messages={
            'max_length': 'El nombre de usuario no puede tener más de 12 caracteres.',
            'required': 'Este campo es obligatorio.',
        }
    )
    name = forms.CharField(max_length=20, label='Nombre', validators=[name_validator])
    age = forms.IntegerField(
        label='Edad',
        validators=[age_validator],
        error_messages={
            'invalid': 'Por favor, introduce una edad válida con máximo 2 dígitos.',
        }
    )
    email = forms.EmailField(required=True, label='Correo electrónico')
    student_number = forms.CharField(max_length=10, label='Número de estudiante', validators=[student_number_validator])
    location = forms.CharField(max_length=100, label='Lugar de residencia')
    feelings = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)], label='¿Cómo te sientes en general?')
    reason = forms.CharField(widget=forms.Textarea, label='Razón para agendar una sesión', validators=[reason_validator])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            student = Student(
                user=user,
                name=self.cleaned_data['name'],
                age=self.cleaned_data['age'],
                email=self.cleaned_data['email'],
                student_number=self.cleaned_data['student_number'],
                location=self.cleaned_data['location'],
                feelings=self.cleaned_data['feelings'],
                reason=self.cleaned_data['reason'],
            )
            student.save()
        return user

# Formularios para editar psicólogos
class PsychologistEditForm(forms.ModelForm):
    name = forms.CharField(max_length=20, label='Nombre', validators=[name_validator])
    age = forms.IntegerField(
        label='Edad',
        validators=[age_validator],
        error_messages={
            'invalid': 'Por favor, introduce una edad válida con máximo 2 dígitos.',
        }
    )
    email = forms.EmailField(required=True, label='Correo electrónico')
    specialty = forms.CharField(max_length=20, label='Especialidad', validators=[specialty_validator])
    phone_number = forms.CharField(max_length=10, label='Número de teléfono', validators=[phone_number_validator])

    class Meta:
        model = Psychologist
        fields = ['name', 'age', 'email', 'specialty', 'phone_number']
        labels = {
            'name': 'Nombre',
            'age': 'Edad',
            'email': 'Correo electrónico',
            'specialty': 'Especialidad',
            'phone_number': 'Número de teléfono',
        }

# Formularios para editar estudiantes
class StudentEditForm(forms.ModelForm):
    name = forms.CharField(max_length=20, label='Nombre', validators=[name_validator])
    age = forms.IntegerField(
        label='Edad',
        validators=[age_validator],
        error_messages={
            'invalid': 'Por favor, introduce una edad válida con máximo 2 dígitos.',
        }
    )
    email = forms.EmailField(required=True, label='Correo electrónico')
    student_number = forms.CharField(max_length=10, label='Número de estudiante', validators=[student_number_validator])
    location = forms.CharField(max_length=100, label='Lugar de residencia')
    feelings = forms.ChoiceField(choices=[(i, i) for i in range(1, 6)], label='¿Cómo te sientes en general?')
    reason = forms.CharField(widget=forms.Textarea, label='Razón para agendar una sesión', validators=[reason_validator])

    class Meta:
        model = Student
        fields = ['name', 'age', 'email', 'student_number', 'location', 'feelings', 'reason']
        labels = {
            'name': 'Nombre',
            'age': 'Edad',
            'email': 'Correo electrónico',
            'student_number': 'Número de estudiante',
            'location': 'Lugar de residencia',
            'feelings': '¿Cómo te sientes en general?',
            'reason': 'Razón para agendar una sesión',
        }

