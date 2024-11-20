from django.contrib import admin
from django.urls import path
from main import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/psychologist/', views.register_psychologist, name='register_psychologist'),
    path('register/student/', views.register_student, name='register_student'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('psychologist_home/', views.psychologist_home, name='psychologist_home'),
    path('student_home/', views.student_home, name='student_home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('calendar/', views.calendar_view, name='psychologist_calendar'),
    path('appointments-data/', views.appointments_data, name='appointments_data'),
    path('students/manage/', views.manage_students, name='manage_students'),
    path('student/<int:student_id>/assign/', views.assign_psychologist, name='assign_psychologist'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('student/<int:student_id>/view/', views.view_student_profile, name='view_student_profile'),
    path('student/<int:student_id>/remove_psychologist/', views.remove_psychologist, name='remove_psychologist'),
    path('explore_psychologists/', views.explore_psychologists, name='explore_psychologists'),
    path('psychologist/<int:psychologist_id>/schedule/', views.psychologist_schedule, name='psychologist_schedule'),
    path('student/view_assigned_psychologist/', views.view_assigned_psychologist, name='view_assigned_psychologist'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('appointment/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('psychologist/manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('schedule_appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('note/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('appointment/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
]

# Configuración para servir archivos estáticos y multimedia en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)