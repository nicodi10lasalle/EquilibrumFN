from django.shortcuts import render, get_object_or_404, redirect
from .forms import PsychologistRegistrationForm, StudentRegistrationForm, PsychologistEditForm, StudentEditForm
from django.contrib.auth import authenticate, login, logout
from .models import Psychologist, Student, Appointment, PrivateNote
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Verificar si es estudiante o psicólogo
    if hasattr(user, 'student_profile'):
        profile_data = user.student_profile
    elif hasattr(user, 'psychologist_profile'):
        profile_data = user.psychologist_profile
    else:
        profile_data = None

    return render(request, 'profile.html', {'profile_data': profile_data})

@login_required
def edit_profile(request):
    if hasattr(request.user, 'psychologist'):
        profile_data = request.user.psychologist
        form_class = PsychologistEditForm
    elif hasattr(request.user, 'student'):
        profile_data = request.user.student
        form_class = StudentEditForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=profile_data)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = form_class(instance=profile_data)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def calendar_view(request):
    return render(request, 'psychologist_calendar.html')

@login_required
def appointments_data(request):
    if request.user.is_authenticated and hasattr(request.user, 'psychologist'):
        appointments = Appointment.objects.filter(psychologist=request.user.psychologist)
        events = []
        for appointment in appointments:
            events.append({
                'title': f"Cita con {appointment.student.name}",
                'start': appointment.start_time.isoformat(),
                'end': appointment.end_time.isoformat(),
            })
        return JsonResponse(events, safe=False)
    else:
        return JsonResponse([], safe=False)

@login_required
def manage_students(request):
    students = Student.objects.all()

    if 'search' in request.GET:
        query = request.GET['search']
        students = students.filter(name__icontains=query)

    return render(request, 'manage_students.html', {'students': students})

@login_required
def assign_psychologist(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if hasattr(request.user, 'psychologist_profile'):
        student.psychologist = request.user
        student.save()
        return redirect('manage_students')
    return redirect('manage_students')

@login_required
def view_student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    current_user = request.user

    if request.method == 'POST' and 'private_notes' in request.POST:
        note_id = request.POST.get('note_id', None)
        content = request.POST.get('private_notes')

        if note_id:
            note = get_object_or_404(PrivateNote, id=note_id)
            if note.created_by == current_user:
                note.content = content
                note.save()
        else:
            if student.psychologist == current_user:
                PrivateNote.objects.create(
                    student=student,
                    content=content,
                    created_by=current_user
                )

    notes = PrivateNote.objects.filter(student=student).order_by('-created_at')
    can_edit = (student.psychologist == current_user)

    return render(request, 'view_student_profile.html', {
        'student': student,
        'can_edit': can_edit,
        'notes': notes,
    })

@login_required
def remove_psychologist(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if hasattr(request.user, 'psychologist_profile') and student.psychologist == request.user:
        student.psychologist = None
        student.save()
    return redirect('manage_students')

@login_required
def explore_psychologists(request):
    psychologists = Psychologist.objects.all()
    return render(request, 'explore_psychologists.html', {'psychologists': psychologists})

@login_required
def psychologist_schedule(request, psychologist_id):
    psychologist = get_object_or_404(Psychologist, id=psychologist_id)
    appointments = Appointment.objects.filter(psychologist=psychologist)

    if hasattr(request.user, 'student'):
        student = request.user.student
    else:
        return render(request, 'psychologist_schedule.html', {
            'psychologist': psychologist,
            'appointments': appointments,
            'error': 'Solo los estudiantes pueden agendar citas.'
        })

    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            # Validar y convertir el string a formato datetime
            start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            end_time = start_time  # Ajusta esto según la duración de la cita si es necesario

            # Verificar si la fecha está en el futuro
            if start_time < datetime.now():
                return render(request, 'psychologist_schedule.html', {
                    'psychologist': psychologist,
                    'appointments': appointments,
                    'error': 'No puedes agendar una cita en una fecha pasada.'
                })

            # Guardar la nueva cita
            Appointment.objects.create(
                student=student,
                psychologist=psychologist,
                start_time=start_time,
                end_time=end_time
            )

            # Refrescar citas después de guardar
            appointments = Appointment.objects.filter(psychologist=psychologist)

            return render(request, 'psychologist_schedule.html', {
                'psychologist': psychologist,
                'appointments': appointments,
                'success': 'Cita agendada exitosamente.'
            })

        except ValueError:
            return render(request, 'psychologist_schedule.html', {
                'psychologist': psychologist,
                'appointments': appointments,
                'error': 'Formato de fecha inválido. Usa el formato correcto.'
            })

    return render(request, 'psychologist_schedule.html', {
        'psychologist': psychologist,
        'appointments': appointments
    })