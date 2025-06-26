from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator  # Import Paginator
from django.conf import settings  # Import settings
from django.http import Http404


from accounts.models import User, Student,Department,LEVEL
from app.models import Session, Semester
from result.models import TakenCourse
from accounts.decorators import lecturer_required, student_required
from .forms import (
    ProgramForm, CourseAddForm, CourseAllocationForm,
    EditCourseAllocationForm, UploadFormFile, UploadFormVideo, CourseAllocationLearnerForm,CourseRequestForm,AdminApprovalForm
)
from .models import Program, Course, CourseAllocation, Upload, UploadVideo, CourseAllocationLearner,CourseRequest
from django.urls import reverse_lazy
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.decorators import user_passes_test



@login_required
def course_allocation_learner_list(request):
    user = request.user

    # Admin sees all data, HOD sees only students reporting to them
    if user.is_superuser or user.is_lecturer:
        students = User.objects.filter(is_student=True)  # Assuming `is_student` field exists in User model
    elif user.is_dep_head:
        # Fetch students that report to the HOD (user)
        students = User.objects.filter(reporting_to=user.username)  # Assuming `reporting_to` field
    else:
        students = User.objects.none()  # Empty for other users

    # Fetch course allocations based on user role
    if user.is_superuser or user.is_lecturer:
        course_allocations = CourseAllocationLearner.objects.all()
    elif user.is_dep_head:
        # Assuming `student_reporting_to` exists to filter students under a HOD
        course_allocations = CourseAllocationLearner.objects.filter(student__reporting_to=user.username)
    else:
        course_allocations = CourseAllocationLearner.objects.none()

    # All courses for the dropdown
    courses = Course.objects.all()

    context = {
        'course_allocations': course_allocations,
        'students': students,
        'courses': courses,
        'title': 'Course Allocations | LMS',
    }
    return render(request, 'course/course_allocation_learner_list.html', context)


@login_required
def course_allocation_learner_create(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_ids = request.POST.getlist('courses')

        if student_id and course_ids:
            student = get_object_or_404(User, id=student_id, is_student=True)
            courses = Course.objects.filter(id__in=course_ids)

            # Create a new allocation
            allocation = CourseAllocationLearner.objects.create(student=student)
            allocation.courses.set(courses)
            allocation.save()

            messages.success(request, "Course allocation added successfully!")
        else:
            messages.error(request, "Please select a student and courses.")

        return redirect('course_allocation_learner_list')

    return redirect('course_allocation_learner_list')



@method_decorator([login_required], name='dispatch')
class CourseAllocationLearnerUpdateView(UpdateView):
    model = CourseAllocationLearner
    form_class = CourseAllocationLearnerForm
    template_name = 'course/course_allocation_learner_form.html'
    success_url = reverse_lazy('course_allocation_learner_list')

    def get_form_kwargs(self):
        # Pass the request.user to the form
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        student = form.cleaned_data['student']
        messages.success(self.request, f"Course Allocation for {student.get_full_name()} updated successfully.")
        return super().form_valid(form)

    
def get_full_name(self):
    return f"{self.first_name} {self.last_name}"

@login_required
def course_allocation_learner_delete(request, pk):
    course_allocation = get_object_or_404(CourseAllocationLearner, pk=pk)
    # course_allocation.delete()
    # messages.success(request, f"Course Allocation for {course_allocation.student.get_full_name()} deleted successfully.")
    # return redirect('course_allocation_learner_list')

    # course_allocation = get_object_or_404(CourseAllocationLearner, pk=pk)
    course_allocation.delete()

    # Ensure the `get_full_name()` method is used correctly.
    if hasattr(course_allocation.student, 'get_full_name') and callable(course_allocation.student.get_full_name):
        full_name = course_allocation.student.get_full_name()
    else:
        full_name = f"{course_allocation.student.first_name} {course_allocation.student.last_name}"

    messages.success(request, f"Course Allocation for {full_name} deleted successfully.")
    return redirect('course_allocation_learner_list')



@method_decorator([login_required], name='dispatch')
class CourseAllocationLearnerCreateView(CreateView):
    model = CourseAllocationLearner
    form_class = CourseAllocationLearnerForm
    template_name = 'course/course_allocation_learner_form.html'
    success_url = reverse_lazy('course_allocation_learner_list')

    def get_form_kwargs(self):
        # Pass the request.user to the form
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        student = form.cleaned_data['student']
        selected_courses = form.cleaned_data['courses']
        
        # Handle case where CourseAllocationLearner does not exist for the student
        try:
            allocation = CourseAllocationLearner.objects.get(student=student)
            allocation.courses.set(selected_courses)
            allocation.save()
            message = f"Course Allocation for {student.get_full_name()} updated successfully."
        except CourseAllocationLearner.DoesNotExist:
            allocation = CourseAllocationLearner.objects.create(student=student)
            allocation.courses.set(selected_courses)
            allocation.save()
            message = f"Course Allocation for {student.first_name} {student.last_name} created successfully."


        messages.success(self.request, message)
        return super().form_valid(form)



# ########################################################
# Program views
# ########################################################
@login_required
def program_view(request):
    programs = Program.objects.all()

    program_filter = request.GET.get('program_filter')
    if program_filter:
        programs = Program.objects.filter(title__icontains=program_filter)

    return render(request, 'course/program_list.html', {
        'title': "Programs | LMS",
        'programs': programs,
    })





@login_required
@lecturer_required
def program_add(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, request.POST.get('title') + ' program has been created.')
            return redirect('programs')
        else:
            messages.error(request, 'Correct the error(S) below.')
    else:
        form = ProgramForm()

    return render(request, 'course/program_add.html', {
        'title': "Add Program | LMS",
        'form': form,
    })


@login_required
def program_detail(request, pk):
    program = Program.objects.get(pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by('-level')
    credits = Course.objects.aggregate(Sum('credit'))

    paginator = Paginator(courses, 10)
    page = request.GET.get('page')

    courses = paginator.get_page(page)

    return render(request, 'course/program_single.html', {
        'title': program.title,
        'program': program, 'courses': courses, 'credits': credits
    }, )


@login_required
@lecturer_required
def program_edit(request, pk):
    program = Program.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, str(request.POST.get('title')) + ' program has been updated.')
            return redirect('programs')
    else:
        form = ProgramForm(instance=program)

    return render(request, 'course/program_add.html', {
        'title': "Edit Program | lms",
        'form': form
    })


@login_required
@lecturer_required
def program_delete(request, pk):
    program = Program.objects.get(pk=pk)
    title = program.title
    program.delete()
    messages.success(request, 'Program ' + title + ' has been deleted.')

    return redirect('programs')
# ########################################################

# ########################################################
# Course views
# ########################################################
@login_required
def course_single(request, slug):
    course = Course.objects.get(slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)

    # lecturers = User.objects.filter(allocated_lecturer__pk=course.id)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    return render(request, 'course/course_single.html', {
        'title': course.title,
        'course': course,
        'files': files,
        'videos': videos,
        'lecturers': lecturers,
        'media_url': settings.MEDIA_ROOT,
    }, )


@login_required
@lecturer_required
def course_add(request, pk):
    users = User.objects.all()
    if request.method == 'POST':
        form = CourseAddForm(request.POST)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_name + '(' + course_code + ')' + ' has been created.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(initial={'program': Program.objects.get(pk=pk)})

    return render(request, 'course/course_add.html', {
        'title': "Add Course | LMS",
        'form': form, 'program': pk, 'users': users
    }, )


@login_required
@lecturer_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        form = CourseAddForm(request.POST, instance=course)
        course_name = request.POST.get('title')
        course_code = request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_name + '(' + course_code + ')' + ' has been updated.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) below.')
    else:
        form = CourseAddForm(instance=course)

    return render(request, 'course/course_add.html', {
        'title': "Edit Course | LMS",
        # 'form': form, 'program': pk, 'course': pk
        'form': form
    }, )


@login_required
@lecturer_required
def course_delete(request, slug):
    course = Course.objects.get(slug=slug)
    # course_name = course.title
    course.delete()
    messages.success(request, 'Course ' + course.title + ' has been deleted.')

    return redirect('program_detail', pk=course.program.id)
# ########################################################


# ########################################################
# Course Allocation
# ########################################################
@method_decorator([login_required], name='dispatch')
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation_form.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a staff has been allocated a course before update it else create new
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk,)
        # print(courses)

        try:
            a = CourseAllocation.objects.get(lecturer=lecturer)
        except:
            a = CourseAllocation.objects.create(lecturer=lecturer)
        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('course_allocation_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Assign Course | LMS"
        return context


@login_required
def course_allocation_view(request):
    if request.method == "POST":
        form = CourseAllocationForm(request.POST, user=request.user)  # Pass user
        if form.is_valid():
            form.save()
            messages.success(request, "Course allocated successfully.")
            return redirect('course_allocation_view')
        else:
            messages.error(request, "There was an error with your form.")
    else:
        form = CourseAllocationForm(user=request.user)  # Pass user
    return render(request, "course/course_allocation_form.html", {"form": form})



@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    try:
        allocated = get_object_or_404(CourseAllocation, pk=pk)
    except Http404:
        return render(request, 'errors/404.html', {
            'title': "No Allocation Found | LMS",
            'message': "The course allocation you are trying to edit does not exist."
        }, status=404)

    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course assignment has been updated.')
            return redirect('course_allocation_view')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/course_allocation_form.html', {
        'title': "Edit Course Allocated | LMS",
        'form': form, 'allocated': pk
    })

# @login_required
# @lecturer_required
# def deallocate_course(request, pk):
#     course = CourseAllocation.objects.get(pk=pk)
#     course.delete()
#     messages.success(request, 'successfully deallocate!')
#     return redirect("course_allocation_view")

# from django.shortcuts import get_object_or_404
# from django.http import HttpResponse

# def deallocate_course(request, course_id):
#     course_allocation = get_object_or_404(CourseAllocation, id=course_id)
#     # Perform deallocation logic here
#     course_allocation.delete()
#     return HttpResponse("Course successfully deallocated.")

# def deallocate_course(request, pk):
#     course_allocation = get_object_or_404(CourseAllocation, id=pk)
#     course_allocation.delete()
#     return HttpResponse("Course successfully deallocated.")


from django.http import HttpResponseNotFound

def deallocate_course(request, pk):
    try:
        course_allocation = CourseAllocation.objects.get(id=pk)
        course_allocation.delete()
        return HttpResponse("Course successfully deallocated.")
    except CourseAllocation.DoesNotExist:
        return HttpResponseNotFound("No course allocation matches the given ID.")


# ########################################################


# ########################################################
# File Upload views
# ########################################################
@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, {'course': course})
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile()
    return render(request, 'upload/upload_file_form.html', {
        'title': "File Upload | LMS",
        'form': form, 'course': course
    })


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = Course.objects.get(slug=slug)
    instance = Upload.objects.get(pk=file_id)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        # file_name = request.POST.get('name')
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile(instance=instance)

    return render(request, 'upload/upload_file_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_file_delete(request, slug, file_id):
    file = Upload.objects.get(pk=file_id)
    # file_name = file.name
    file.delete()

    messages.success(request, (file.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)

# ########################################################
# Video Upload views
# ########################################################
@login_required
@lecturer_required
def handle_video_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo()
    return render(request, 'upload/upload_video_form.html', {
        'title': "Video Upload | LMS",
        'form': form, 'course': course
    })


@login_required
# @lecturer_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(request, 'upload/video_single.html', {'video': video})

@login_required
# @lecturer_required
def handle_file_single(request, file_id, file_slug):
    course = get_object_or_404(Course, file_id=file_id)
    file= get_object_or_404(UploadFormFile, file_id=file_id)
    return render(request, 'upload/file_single.html', {'file': file})

@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = Course.objects.get(slug=slug)
    instance = UploadVideo.objects.get(slug=video_slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(request, 'upload/upload_video_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_video_delete(request, slug, video_slug):
    # video = get_object_or_404(UploadVideo, slug=video_slug)
    # video = UploadVideo.objects.get(slug=video_slug)
    # video.delete()
    video = get_object_or_404(UploadVideo, slug=video_slug)  # Ensure this is correct
    video.delete()

    messages.success(request, (video.title + ' has been deleted.'))
    return redirect('course_detail', slug=slug)
# ########################################################


# ########################################################
# Course Registration
# ########################################################
@login_required
def course_registration(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.create(student=student, course=course)
            obj.save()
            messages.success(request, 'Courses Registered Successfully!')
        return redirect('course_registration')
    else:
        student = get_object_or_404(Student, student__id=request.user.id)
        taken_courses = TakenCourse.objects.filter(student__student__id=request.user.id)
        t = ()
        for i in taken_courses:
            t += (i.course.pk,)
        # current_semester = Semester.objects.get(is_current_semester=True)
        courses = Course.objects.filter(program__pk=student.department.id, level=student.level).exclude(id__in=t).order_by('level')
        all_courses = Course.objects.filter(level=student.level, program__pk=student.department.id)

        no_course_is_registered = False
        all_courses_are_registered = False

        registered_courses = Course.objects.filter(level=student.level).filter(id__in=t)
        if registered_courses.count() == 0:
            no_course_is_registered = True

        if registered_courses.count() == all_courses.count():
            all_courses_are_registered = True

        total_first_semester_credit = 0
        total_sec_semester_credit = 0
        total_registered_credit = 0
        # for i in courses:
        #     if i.semester == "First":
        #         total_first_semester_credit += int(i.credit)
        #     if i.semester == "Second":
        #         total_sec_semester_credit += int(i.credit)
        for i in registered_courses:
            total_registered_credit += int(i.credit)
        context = {
            "is_calender_on": True,
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            # "current_level": current_semester,
            "courses": courses,
            "total_first_semester_credit": total_first_semester_credit,
            "total_sec_semester_credit": total_sec_semester_credit,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit,
            "student": student,
        }
        return render(request, 'course/course_registration.html', context)


@login_required
@student_required
def course_drop(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = TakenCourse.objects.get(student=student, course=course)
            obj.delete()
            messages.success(request, 'Successfully Dropped!')
        return redirect('course_registration')
# ########################################################


@login_required
def user_course_list(request):
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer=request.user.id)

        return render(request, 'course/user_course_list.html', {'courses': courses})

    elif request.user.is_student:
        try:
            # Use filter to allow multiple student entries
            students = Student.objects.filter(student__id=request.user.id)

            # Aggregate all taken courses and programs for this student
            taken_courses = TakenCourse.objects.filter(student__student__id__in=[student.student.id for student in students])

            courses = Course.objects.filter(program_id__in=[student.course.program_id for student in students])

            return render(request, 'course/user_course_list.html', {
                'students': students,
                'taken_courses': taken_courses,
                'courses': courses
            })
        except Student.DoesNotExist:
            return render(request, 'course/user_course_list.html', {
                'error': 'Student not found'
            })

    elif request.user.is_dep_head:
        try:
            # Similarly, allow multiple student entries for department head
            students = Student.objects.filter(student__id=request.user.id)

            taken_courses = TakenCourse.objects.filter(student__student__id__in=[student.student.id for student in students])

            courses = Course.objects.filter(allocated_course__lecturer=request.user.id)

            return render(request, 'course/user_course_list.html', {
                'students': students,
                'taken_courses': taken_courses,
                'courses': courses
            })
        except Student.DoesNotExist:
            return render(request, 'course/user_course_list.html', {
                'error': 'Department head information not found'
            })

    else:
        return render(request, 'course/user_course_list.html', {
            'error': 'No valid role found for user'
        })


# ########################################################
# Course Allocation for Students
# ########################################################
@method_decorator([login_required], name='dispatch')
class CourseAllocationFormViewStudent(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/course_allocation_form_student.html'

    def get_form_kwargs(self):
        kwargs = super(CourseAllocationFormViewStudent, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # if a student has been allocated a course before update it else create new
        student = form.cleaned_data['student']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk,)
        # print(courses)

        try:
            a = CourseAllocationLearner.objects.get(student=student)
        except CourseAllocationLearner.DoesNotExist:
            a = CourseAllocationLearner.objects.create(student=student)
        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('course_allocation_view_student')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Assign Course | LMS"
        return context


@login_required
def course_allocation_view_student(request):
    allocated_courses = CourseAllocationLearner.objects.all()
    return render(request, 'course/course_allocation_view_student.html', {
        'title': "Course Allocations | LMS",
        "allocated_courses": allocated_courses
    })


@login_required
def edit_allocated_course_student(request, pk):
    allocated = get_object_or_404(CourseAllocationLearner, pk=pk)
    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course assigned has been updated.')
            return redirect('course_allocation_view_student')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/course_allocation_form_student.html', {
        'title': "Edit Course Allocated | LMS",
        'form': form, 'allocated': pk
    })


@login_required
def deallocate_course_student(request, pk):
    # course_allocation = get_object_or_404(CourseAllocationLearner, pk=pk)
    # course_allocation.delete()

    # # Ensure the `get_full_name()` method is used correctly.
    # if hasattr(course_allocation.student, 'get_full_name') and callable(course_allocation.student.get_full_name):
    #     full_name = course_allocation.student.get_full_name()
    # else:
    #     full_name = f"{course_allocation.student.first_name} {course_allocation.student.last_name}"

    # messages.success(request, f"Course Allocation for {full_name} deleted successfully.")
    # return redirect('course_allocation_learner_list')
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'successfully deallocate!')
    return redirect("course_allocation_view")


@login_required
def course_request_view(request):
    if request.method == "POST":
        # Fetch form data
        user = request.user
        hod = user  # Assigning the User object, not a string
        department = user.department 
        team_members = User.objects.filter(reporting_to=user.id, is_active=True)
        team_member_id = request.POST.get("team_member")
        program_id = request.POST.get("program")
        course_id = request.POST.get("course")
        level = request.POST.get("level")
        department_id = request.POST.get("department")

        try:
            # Fetch related objects
            team_member = User.objects.get(id=team_member_id)
            program = Program.objects.get(id=program_id)
            course = Course.objects.get(id=course_id)
            department = Department.objects.get(id=department_id)

            # Save the request
            CourseRequest.objects.create(
                hod=hod,  # Corrected to store the User object
                team_member=team_member,
                program=program,
                course=course,
                level=level,
                department=department.id,  # Save department ID
                status="Pending",
            )
            messages.success(request, "Course request submitted successfully!")
        except Exception as e:
            messages.error(request, f"Error submitting request: {e}")
            print(e)  # Print error for debugging

        return redirect("create_course_request")

    # Fetch data for dropdowns
    
    team_members = User.objects.filter(reporting_to=request.user.username)
    programs = Program.objects.all()
    courses = Course.objects.all()
    departments = Department.objects.all()
    course_requests = CourseRequest.objects.filter(status="Pending")

    return render(
        request,
        'course/course_request_table.html',
        {
            'team_members': team_members,
            'programs': programs,
            'courses': courses,
            'course_requests': course_requests,
            'departments': departments,
            'LEVEL': LEVEL,
        },
    )




# @login_required
# def course_allocation_approval_list(request):
#     # Fetch all pending course allocations
#     course_allocations = CourseRequest.objects.all()

#     return render(request, 'course/course_approval_table.html', {
#         'course_allocations': course_allocations,
#         'title': "Course Allocation Approval",
#     })

@login_required
def course_allocation_approval_list(request):
    # Fetch all pending course requests
    course_requests = CourseRequest.objects.filter(status="Pending")

    if request.method == "POST":
        request_id = request.POST.get("id")
        new_status = request.POST.get("status")

        try:
            # Fetch the specific course request
            course_request = get_object_or_404(CourseRequest, id=request_id)

            # Update the status
            course_request.status = new_status
            course_request.save()

            # If the status is "Approved," save it to the `accounts_student` table
            if new_status == "Approved":
                Student.objects.create(
                    student_id=course_request.team_member.id,
                    program_id=course_request.program.id,
                    course_id=course_request.course.id,
                    department_id=course_request.id,  # Ensure this exists
                    level=course_request.level,
                )
                messages.success(
                    request,
                    f"Request for {course_request.team_member.get_full_name()} approved successfully!",
                )
            else:
                messages.info(
                    request,
                    f"Request for {course_request.team_member.get_full_name()} updated to {new_status}.",
                )
        except Exception as e:
            print(f"Debug Error: {e}")  # Debugging
            messages.error(request, f"An error occurred: {e}")

    return render(
        request,
        "course/course_approval_table.html",
        {
            "course_requests": course_requests,
            "title": "Pending Course Requests",
        },
    )


    





