from django.urls import path
from .views import *
from . import views



urlpatterns = [
    # Program URLs
    path('', program_view, name='programs'),
    path('<int:pk>/detail/', program_detail, name='program_detail'),
    path('add/', program_add, name='add_program'),
    path('<int:pk>/edit/', program_edit, name='edit_program'),
    path('<int:pk>/delete/', program_delete, name='program_delete'),

    # Course URLs
    path('course/<slug>/detail/', course_single, name='course_detail'),
    path('<int:pk>/course/add/', course_add, name='course_add'),
    path('course/<slug>/edit/', course_edit, name='edit_course'),
    path('course/delete/<slug>/', course_delete, name='delete_course'),

    # Course Allocation for Lecturers URLs
    path('course/assign/', CourseAllocationFormView.as_view(), name='course_allocation'),
    path('course/allocated/', course_allocation_view, name='course_allocation_view'),
    path('allocated_course/<int:pk>/edit/', edit_allocated_course, name='edit_allocated_course'),
    path('course/<int:pk>/deallocate/', deallocate_course, name='course_deallocate'),

    path('request/', course_request_view, name='create_course_request'),
    # path('course-allocations/approval/', approve_course_allocation_list, name='approve_course_allocation_list'),
    path('course-allocations/approval/', views.course_allocation_approval_list, name='course_allocation_approval_list'),


    # path('approval/', approve_course_request, name='approve_course_request'),
    # path('course-allocations/approve/<int:pk>/', approve_course_allocation, name='approve_course_allocation'),

    # Course Allocation for Learners URLs
    # path('learners/', CourseAllocationLearnerListView.as_view(), name='course_allocation_learner_list'),
    # path('learners/<int:pk>/', CourseAllocationLearnerDetailView.as_view(), name='course_allocation_learner_detail'),
    # path('learners/create/', CourseAllocationLearnerCreateView.as_view(), name='course_allocation_learner_create'),
    # path('learners/<int:pk>/edit/', CourseAllocationLearnerUpdateView.as_view(), name='course_allocation_learner_edit'),
    # path('learners/<int:pk>/delete/', course_allocation_learner_delete, name='course_allocation_learner_delete'),

    path('course-allocations/', views.course_allocation_learner_list, name='course_allocation_learner_list'),
    path('course-allocations/update/<int:pk>/', views.CourseAllocationLearnerUpdateView.as_view(), name='course_allocation_learner_update'),
    path('course-allocations/create/', views.CourseAllocationLearnerCreateView.as_view(), name='course_allocation_learner_create'),
    path('course-allocations/delete/<int:pk>/', views.course_allocation_learner_delete, name='course_allocation_learner_delete'),
path('course-allocations/delete/<int:pk>/', views.deallocate_course_student, name='course_allocation_learner_delete'),

    # File Upload URLs
    path('course/<slug>/documentations/upload/', handle_file_upload, name='upload_file_view'),
    path('course/<slug>/documentations/<int:file_id>/edit/', handle_file_edit, name='upload_file_edit'),
    path('course/<slug>/documentations/<int:file_id>/delete/', handle_file_delete, name='upload_file_delete'),

    # Video Upload URLs
    path('course/<slug>/video_tutorials/upload/', handle_video_upload, name='upload_video'),
    path('course/<slug>/video_tutorials/<video_slug>/detail/', handle_video_single, name='video_single'),
    path('course/<slug>/video_tutorials/<video_slug>/edit/', handle_video_edit, name='upload_video_edit'),
    path('course/<slug>/video_tutorials/<video_slug>/delete/', handle_video_delete, name='upload_video_delete'),

    # Course Registration URLs
    path('course/registration/', course_registration, name='course_registration'),
    path('course/drop/', course_drop, name='course_drop'),

    # User Courses URLs
    path('my_courses/', user_course_list, name="user_course_list"),
    path('course/<int:course_id>/deallocate/', views.deallocate_course, name='deallocate_course')

]
