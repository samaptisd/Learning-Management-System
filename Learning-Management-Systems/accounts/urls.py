from django.urls import path, include
from .views import (
    profile, profile_single, admin_panel, profile_update, change_password,
    edit_hod, LecturerListView, StudentListView, delete_hod, staff_add_view, 
    edit_staff, hodListView, delete_staff, student_add_view, hod_add_view, 
    edit_student, delete_student, validate_username, register, 
    password_reset_view, password_reset_done_view, password_reset_confirm_view, 
    password_reset_complete_view, hod_team_list, training_calendar, custom_logout_view, 
    download_report, user_activity_log_view, user_login, user_logout, export_to_excel,SyncUserView,ExportDataToSheet,ImportCourse,admin_team_list
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('login/', user_login, name='login'),  # Using custom login view
    path('admin_panel/', admin_panel, name='admin_panel'),
    path('profile/', profile, name="profile"),
    path('profile/<int:id>/detail/', profile_single, name='profile_single'),
    path('setting/', profile_update, name='edit_profile'),
    path('change_password/', change_password, name='change_password'),
    path('lecturers/', LecturerListView.as_view(), name='lecturer_list'),
    path('lecturer/add/', staff_add_view, name='add_lecturer'),
    path('staff/<int:pk>/edit/', edit_staff, name='staff_edit'),
    path('lecturers/<int:pk>/delete/', delete_staff, name='lecturer_delete'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('student/add/', student_add_view, name='add_student'),
    path('student/<int:pk>/edit/', edit_student, name='student_edit'),
    path('students/<int:pk>/delete/', delete_student, name='student_delete'),
    path('ajax/validate-username/', validate_username, name='validate_username'),
    path('register/', register, name='register'),
    path('hods/', hodListView.as_view(), name='hod_list'),
    path('hod/add/', hod_add_view, name='add_hod'),
    path('addhod/<int:pk>/edit/', edit_hod, name='hod_edit'),
    path('hod/<int:pk>/delete/', delete_hod, name='hod_delete'),
    path('hod-team-list/', hod_team_list, name='hod_team_list'),
    path('training_calendar/', training_calendar, name='training_calendar'),
    path('accounts/logout/', user_logout, name='logout'),  # Custom logout view
    path('download_report/', download_report, name='report_download'),
    path('user-activity-log/', user_activity_log_view, name='user-activity-log'),
    path('export-to-excel/', export_to_excel, name='export_to_excel'),
    #  path('accounts/', include('allauth.urls')),
    path('sync-user/', SyncUserView.as_view(), name='sync-user'),
     path('export-data/', ExportDataToSheet.as_view(), name='export-data'),
     path('course-data/', ImportCourse.as_view(), name='course-data'),
     path('admin-team-list/', admin_team_list, name='admin_team_list'),
]
