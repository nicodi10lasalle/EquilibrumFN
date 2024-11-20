from django.shortcuts import render, get_object_or_404, redirect
from .forms import PsychologistRegistrationForm, StudentRegistrationForm, PsychologistEditForm, StudentEditForm
from django.contrib.auth import authenticate, login, logout
from .models import Psychologist, Student, Appointment, PrivateNote
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from google.generativeai import GenerativeModel
import json
import google.generativeai as genai
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .forms import ProfilePhotoForm




# Configuración de la API
def model_configai():
    genai.configure(api_key="AIzaSyA8DYgUKemH6H1fRGnZwtrF6Bid85xK_tM")

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }

    model = GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
    return model

def llm_prompt_engineering(model, phrase):
    chat = model.start_chat(
        history=[
            {"role": "user",
             "parts": '''
             Actúa como un psicólogo clínico. Analiza la siguiente nota y proporciona:
             1. Un diagnóstico numérico entre 1 y 9 basado en la gravedad (1 siendo muy crítico y 9 estable).
             2. Un estado asociado al diagnóstico:
                - [1-3] Crítico, Atención Inmediata.
                - [4-6] Moderado, Agendar en una o dos semanas.
                - [7-9] Estable, Monitoreo regular.
             3. Una recomendación para el tiempo de la cita basado en el diagnóstico:
                - [1-3] En estos días.
                - [4-6] En una o dos semanas.
                - [7-9] En el próximo mes.
             Devuelve un JSON en este formato:
             {"diagnosis": <número>, "state": "<estado>", "recommendation": "<recomendación>"}
             '''
             }
        ]
    )
    response = chat.send_message(phrase)
    return response.text


def register_psychologist(request):
    if request.method == 'POST':
        form = PsychologistRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el usuario y crea la instancia de Psychologist
            return redirect('login')
    else:
        form = PsychologistRegistrationForm()

    return render(request, 'register_psychologist.html', {'form': form})

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el usuario y crea la instancia de Student
            return redirect('login')
    else:
        form = StudentRegistrationForm()

    return render(request, 'register_student.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Verificar si el usuario es psicólogo o estudiante
            if hasattr(user, 'psychologist_profile'):
                return redirect('psychologist_home')  # Redirige a la página de psicólogo
            elif hasattr(user, 'student_profile'):
                return redirect('student_home')  # Redirige a la página de estudiante
            else:
                return redirect('home')  # Si no tiene tipo, redirige a la home por defecto
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def psychologist_home(request):
    return render(request, 'psychologist_home.html')

@login_required
def student_home(request):
    return render(request, 'student_home.html')

def home(request):
    return render(request, 'home.html')

@login_required
def profile(request, user_id=None):
    # Si no se proporciona un user_id, usar el del usuario autenticado
    user = get_object_or_404(User, id=user_id) if user_id else request.user

    # Determinar si el usuario es estudiante o psicólogo
    profile_data = (
        user.student_profile if hasattr(user, 'student_profile') else
        user.psychologist_profile if hasattr(user, 'psychologist_profile') else
        None
    )

    if not profile_data:  # Si no hay perfil asociado, redirigir al inicio
        messages.error(request, "Perfil no encontrado.")
        return redirect('home')

    # Procesar la carga de la foto de perfil
    if request.method == 'POST':
        profile_form = ProfilePhotoForm(request.POST, request.FILES, instance=profile_data)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Foto de perfil actualizada correctamente.')
            return redirect('profile', user_id=user.id)
        else:
            messages.error(request, 'Ocurrió un error al actualizar la foto.')
    else:
        profile_form = ProfilePhotoForm(instance=profile_data)

    return render(request, 'profile.html', {
        'profile_data': profile_data,
        'profile_form': profile_form,
        'is_student': hasattr(user, 'student_profile'),
    })

@login_required
def edit_profile(request):
    # Verifica si el usuario es psicólogo o estudiante y asigna el form_class y profile_data
    if hasattr(request.user, 'psychologist_profile'):
        profile_data = request.user.psychologist_profile
        form_class = PsychologistEditForm
    elif hasattr(request.user, 'student_profile'):
        profile_data = request.user.student_profile
        form_class = StudentEditForm
    else:
        # Si el usuario no tiene perfil de psicólogo o estudiante, redirigirlo o manejar el error
        return redirect('home')

    if request.method == 'POST':
        form = form_class(request.POST, instance=profile_data)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=request.user.id)
    else:
        form = form_class(instance=profile_data)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def calendar_view(request):
    return render(request, 'psychologist_calendar.html')

@login_required
def appointments_data(request):
    # Verificar que el usuario es un psicólogo
    if request.user.is_authenticated and hasattr(request.user, 'psychologist_profile'):
        appointments = Appointment.objects.filter(psychologist=request.user.psychologist_profile)
        events = [
            {
                'title': f"Cita con {appointment.student.name}",
                'start': appointment.start_time.isoformat(),
                'end': appointment.end_time.isoformat(),
            }
            for appointment in appointments
        ]
        return JsonResponse(events, safe=False)
    else:
        return JsonResponse([], safe=False)

@login_required
def manage_students(request):
    students = Student.objects.all()
    psychologist = request.user.psychologist_profile if hasattr(request.user, 'psychologist_profile') else None

    # Filtro de búsqueda por nombre
    if 'search' in request.GET:
        query = request.GET['search']
        students = students.filter(name__icontains=query)
    
    # Filtro para mostrar solo estudiantes asignados al psicólogo logueado
    if 'assigned_only' in request.GET and psychologist:
        students = students.filter(psychologist=psychologist)

    return render(request, 'manage_students.html', {
        'students': students,
        'psychologist': psychologist
    })

@login_required
def assign_psychologist(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if hasattr(request.user, 'psychologist_profile'):
        psychologist = request.user.psychologist_profile  # Obtener la instancia de Psychologist
        student.psychologist = psychologist  # Asignar la instancia de Psychologist
        student.save()
        return redirect('manage_students')
    return redirect('manage_students')

@login_required
def view_student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    current_user = request.user
    can_edit = student.psychologist == current_user.psychologist_profile

    if request.method == 'POST' and 'private_notes' in request.POST:
        note_id = request.POST.get('note_id', None)
        content = request.POST.get('private_notes')
        model = model_configai()  # Inicializa el modelo para análisis de notas
        sentiment_result = llm_prompt_engineering(model, content)

        try:
            sentiment_json = json.loads(sentiment_result)
            diagnosis = sentiment_json.get('diagnosis', None)
            state = sentiment_json.get('state', 'No definido')
            recommendation = sentiment_json.get('recommendation', 'No definido')
        except json.JSONDecodeError:
            messages.error(request, "Error al analizar la nota. Inténtalo de nuevo.")
            return redirect('view_student_profile', student_id=student_id)

        if note_id:
            note = get_object_or_404(PrivateNote, id=note_id)
            if note.created_by == current_user:
                note.content = content
                note.sentiment = diagnosis  # Almacena el diagnóstico como parte del contenido
                note.state = state
                note.recommendation = recommendation
                note.save()
        else:
            if can_edit:
                PrivateNote.objects.create(
                    student=student,
                    content=content,
                    created_by=current_user,
                    sentiment=f"Diagnóstico: {diagnosis}",
                    state=state,
                    recommendation=recommendation
                )

    notes = PrivateNote.objects.filter(student=student).order_by('-created_at')

    return render(request, 'view_student_profile.html', {
        'student': student,
        'can_edit': can_edit,
        'notes': notes,
    })

@login_required
def remove_psychologist(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Verifica si el usuario es un psicólogo
    if hasattr(request.user, 'psychologist_profile'):
        # Verificar si el estudiante tiene un psicólogo asignado
        if student.psychologist:
            student.psychologist = None  # Eliminar la asignación del psicólogo
            student.save()
            return redirect('view_student_profile', student_id=student_id)  # Redirigir a la vista de perfil del estudiante
        else:
            return redirect('manage_students')  # Si no hay psicólogo asignado, redirigir a gestionar estudiantes
    else:
        return redirect('manage_students')  # Si no es un psicólogo, redirigir a gestionar estudiantes

@login_required
def explore_psychologists(request):
    psychologists = Psychologist.objects.all()
    return render(request, 'explore_psychologists.html', {'psychologists': psychologists})

@login_required
def psychologist_schedule(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    appointments = Appointment.objects.filter(psychologist=psychologist)

    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        return render(request, 'psychologist_schedule.html', {
            'psychologist': psychologist,
            'appointments': appointments,
            'error': 'Solo los estudiantes pueden agendar citas.'
        })

    if request.method == 'POST':
        if 'date' in request.POST:
            date_str = request.POST.get('date')
            start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            if start_time >= datetime.now():
                Appointment.objects.create(
                    student=student,
                    psychologist=psychologist,
                    start_time=start_time,
                    end_time=start_time
                )
                messages.success(request, 'Cita agendada exitosamente.')
            else:
                messages.error(request, 'No puedes agendar una cita en una fecha pasada.')
        elif 'delete_appointment_id' in request.POST:
            appointment_id = request.POST.get('delete_appointment_id')
            appointment = get_object_or_404(Appointment, id=appointment_id, student=student)
            appointment.delete()
            # Redirección directa después de eliminar una cita
            return redirect('psychologist_schedule', psychologist_id=psychologist.id)

    appointments = Appointment.objects.filter(psychologist=psychologist).order_by('start_time')
    return render(request, 'psychologist_schedule.html', {'psychologist': psychologist, 'appointments': appointments})

@login_required
def view_assigned_psychologist(request):
    student = request.user.student_profile  # Obtener el perfil del estudiante
    psychologist = student.psychologist  # Psicólogo asignado al estudiante

    if psychologist is None:
        return render(request, 'view_assigned_psychologist.html', {
            'error': 'No tienes un psicólogo asignado actualmente.'
        })

    return render(request, 'view_assigned_psychologist.html', {
        'psychologist': psychologist
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Appointment


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Verificar permisos
    if not (
        (hasattr(request.user, 'psychologist_profile') and appointment.psychologist.user == request.user) or
        (hasattr(request.user, 'student_profile') and appointment.student.user == request.user)
    ):
        return redirect('home')  # Redirigir si el usuario no está autorizado

    # Captura de la URL previa (default a una página segura si no existe)
    prev_url = request.POST.get('prev_url', reverse('home'))

    if request.method == 'POST':
        date_str = request.POST.get('date')
        if date_str:
            try:
                # Actualización de la cita
                start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
                appointment.start_time = start_time
                appointment.end_time = start_time
                appointment.save()
                messages.success(request, 'La cita se ha actualizado correctamente.')

                # Redirige a la URL previa
                return redirect(prev_url)
            except ValueError:
                messages.error(request, 'Formato de fecha inválido.')
        else:
            messages.error(request, 'La fecha de la cita es requerida.')

    return render(request, 'edit_appointment.html', {'appointment': appointment})

@login_required
def manage_appointments(request):
    # Verificar si el usuario es un psicólogo
    if not hasattr(request.user, 'psychologist_profile'):
        return redirect('home')  # Redirige a la página principal si no es psicólogo

    psychologist = request.user.psychologist_profile
    # Obtener todas las citas asignadas al psicólogo
    appointments = Appointment.objects.filter(psychologist=psychologist).order_by('start_time')

    if request.method == 'POST' and 'delete_appointment_id' in request.POST:
        appointment_id = request.POST['delete_appointment_id']
        appointment = get_object_or_404(Appointment, id=appointment_id, psychologist=psychologist)
        appointment.delete()
        messages.success(request, 'La cita ha sido eliminada exitosamente.')
        return redirect('manage_appointments')

    return render(request, 'manage_appointments.html', {
        'appointments': appointments,
    })

@login_required
def schedule_appointment(request):
    # Verifica si el usuario actual es un estudiante
    if hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        if student.psychologist:
            # Redirige a la agenda del psicólogo asignado
            return redirect('psychologist_schedule', psychologist_id=student.psychologist.id)
        else:
            # Redirige a la página para explorar psicólogos
            return redirect('explore_psychologists')
    else:
        return redirect('student_home')  # Redirige al inicio del estudiante si no es un estudiante
    

@login_required
def delete_note(request, note_id):
    # Obtener la nota
    note = get_object_or_404(PrivateNote, id=note_id)
    
    # Verificar que el usuario actual sea el creador de la nota o el psicólogo asignado al estudiante
    if note.created_by == request.user or (
        hasattr(request.user, 'psychologist_profile') and 
        note.student.psychologist == request.user.psychologist_profile
    ):
        note.delete()
        messages.success(request, "Nota eliminada correctamente.")
    else:
        messages.error(request, "No tienes permiso para eliminar esta nota.")
    
    # Redirigir al perfil del estudiante
    return redirect('view_student_profile', student_id=note.student.id)