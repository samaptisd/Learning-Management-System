from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.urls import reverse

from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)

from .decorators import lecturer_required, student_required, admin_required, hod_required
from course.models import Course
from result.models import TakenCourse
from app.models import Session, Semester
from .forms import StaffAddForm, StudentAddForm, ProfileUpdateForm,PasswordResetForm
from .models import User, Student, DepartmentHead

from django.shortcuts import render, redirect
from .models import DepartmentHead
from django.shortcuts import render, redirect
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView, LoginView, LogoutView
)

from quiz.models import Sitting
from django.urls import reverse_lazy

def home(request):
    # Your custom home view logic here
    return render(request, 'home.html')

def custom_view(request):
    # Your custom view logic here
    return render(request, 'custom_template.html', context={})

# Use authentication views
password_reset_view = PasswordResetView.as_view(template_name='registration/password_reset_form.html')
password_reset_done_view = PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html')
password_reset_confirm_view = PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html')
password_reset_complete_view = PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html')
def validate_username(request):
    username = request.GET.get("username", None)
    data = {"is_taken": User.objects.filter(username__iexact=username).exists()}
    return JsonResponse(data)


def register(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Account created successfuly.")
        else:
            messages.error(
                request, f"Somthing is not correct, please fill all fields correctly."
            )
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {"form": form})


@login_required(login_url='/accounts/login/')

def profile(request):
    """Show profile of any user that fire out the request"""
    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    if request.user.is_lecturer:
        courses = Course.objects.filter(
            allocated_course__lecturer__pk=request.user.id
        ).filter(vertical=current_semester)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "courses": courses,
                "current_session": current_session,
                "current_semester": current_semester,
             },
        )
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        try:
            departmentHead = DepartmentHead.objects.get(student=level)
        except:
            departmentHead = "no DepartmentHead set"
        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=level.level
        )
        context = {
            "title": request.user.get_full_name,
            "departmentHead": departmentHead,
            "courses": courses,
            "level": level,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile.html", context)
    else:
        staff = User.objects.filter(is_lecturer=True)
        return render(
            request,
            "accounts/profile.html",
            {
                "title": request.user.get_full_name,
                "staff": staff,
                "current_session": current_session,
                "current_semester": current_semester,
            },
        )


@login_required(login_url='/accounts/login/')

def profile_single(request, id):
    """Show profile of any selected user"""
    if request.user.id == id:
        return redirect("SMS:profile")


    current_session = Session.objects.filter(is_current_session=True).first()
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(
            vertical=current_semester)

        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "Lecturer",
            "courses": courses,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = TakenCourse.objects.filter(
            student__student__id=id, course__level=student.level
        )
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "student",
            "courses": courses,
            "student": student,
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)
    else:
        context = {
            "title": user.get_full_name,
            "user": user,
            "user_type": "superuser",
            "current_session": current_session,
            "current_semester": current_semester,
        }
        return render(request, "accounts/profile_single.html", context)


@login_required
@admin_required
def admin_panel(request):
    return render(request, "setting/admin_panel.html", {})


# ########################################################


# ########################################################
# Setting views
# ########################################################
@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect(reverse("SMS:profile"))

        else:
            messages.error(request, "Please correct the error(s) below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(
        request,
        "setting/profile_info_change.html",
        {
            "title": "Setting | LMS",
            "form": form,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the error(s) below. ")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "setting/password_change.html",
        {
            "form": form,
        },
    )


#########################################################


@login_required(login_url='/accounts/login/')
@admin_required
def staff_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Account for lecturer {first_name} {last_name} has been created."
            )
            return redirect("lecturer_list")
        else:
            messages.error(request, "Please correct the error(s) below.")
            return render(request, "accounts/add_staff.html", {"form": form})
    else:
        form = StaffAddForm()
        context = {
            "title": "Lecturer Add | LMS",
            "form": form,
        }
        return render(request, "accounts/add_staff.html", context)



@login_required(login_url='/accounts/login/')
@admin_required
def edit_staff(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Lecturer " + full_name + " has been updated.")
            return redirect("lecturer_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(
        request,
        "accounts/edit_lecturer.html",
        {
            "title": "Edit Lecturer | LMS",
            "form": form,
        },
    )


@method_decorator([login_required, admin_required], name="dispatch")
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lecturers | LMS"
        return context


# @login_required
# @lecturer_required
# def delete_staff(request, pk):
#     staff = get_object_or_404(User, pk=pk)
#     staff.delete()
#     return redirect('lecturer_list')


@login_required(login_url='/accounts/login/')
@admin_required
def delete_staff(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, "Lecturer " + full_name + " has been deleted.")
    return redirect("lecturer_list")


# ########################################################


# ########################################################
# Student views
# ########################################################
@login_required(login_url='/accounts/login/')
def student_add_view(request):
    if request.method == "POST":
        form = StudentAddForm(request.POST)
        
        # Add this to print all the submitted form data
        print(request.POST) 
        
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    "Account for " + form.cleaned_data.get('first_name') + " " + form.cleaned_data.get('last_name') + " has been created."
                )
                return redirect("student_list")
            except Exception as e:
                print(e)  # Print any unexpected exception
                messages.error(request, "An error occurred while saving the student data.")
        else:
            # Add this to print form errors to the console
            print(form.errors)  # This will print the form errors to the console for debugging purposes
            
            messages.error(request, "Correct the error(s) below.")
    else:
        form = StudentAddForm()

    return render(
        request,
        "accounts/add_student.html",
        {"title": "Add Student | LMS", "form": form},
    )








@login_required(login_url='/accounts/login/')
# @method_decorator([hod_required], name="dispatch")

def edit_student(request, pk):
    student = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student)
        full_name = student.get_full_name
        if form.is_valid():
            form.save()
            messages.success(request, "Student " + full_name + " has been updated.")
            return redirect(reverse("student_list"))

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=student)
    return render(
        request,
        "accounts/edit_student.html",
        {
            "title": "Edit Student | LMS",
            "form": form,
        },
    )


@method_decorator([login_required], name="dispatch")
class StudentListView(ListView):
    template_name = "accounts/student_list.html"
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get("student_id")
        if query is not None:
            queryset = queryset.filter(Q(department=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Aludecorian | LMS"
        return context


@login_required(login_url='/accounts/login/')

def delete_student(request, pk):
    student = get_object_or_404(User, id=pk)
    full_name = student.get_full_name
    student.delete()
    messages.success(request, "Student " + full_name + " has been deleted.")
    return redirect(reverse("student_list"))



#########################################################





# Create your views here.
@login_required(login_url='/accounts/login/')
@admin_required
def index(request):
    all_hod = DepartmentHead.objects.all()
    return render(request, 'datatables/hod_table.html', {'all_hod': all_hod})


def add(request):
    if request.method == "POST":
        hod = DepartmentHead(
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            course=request.POST.get('course')
        )
        hod.save()
        print(request.POST)
        return redirect('/')
    else:
        return render(request, 'add_hod.html')



@method_decorator([login_required, admin_required], name="dispatch")
class hodListView(ListView):
    queryset = User.objects.filter(is_dep_head=True)
    template_name = "accounts/hod_list.html"
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Hod | LMS"
        return context



@login_required(login_url='/accounts/login/')
@admin_required
def hod_add_view(request):
    if request.method == "POST":
        form = StaffAddForm(request.POST)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account for Department Head "
                + first_name
                + " "
                + last_name
                + " has been created.",
            )
            return redirect("hod_list")
    else:
        form = StaffAddForm()

    context = {
        "title": "Hod Add | LMS",
        "form": form,
    }

    return render(request, "accounts/add_hod.html", context)


@login_required(login_url='/accounts/login/')
@admin_required
def edit_hod(request, pk):
    instance = get_object_or_404(User, is_dep_head=True, pk=pk)
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, "Department Head " + full_name + " has been updated.")
            return redirect("hod_list")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(
        request,
        "accounts/edit_hod.html",
        {
            "title": "Edit Department Head | LMS",
            "form": form,
        },
    )


@login_required(login_url='/accounts/login/')
@admin_required
def delete_hod(request, pk):
    hod = get_object_or_404(User, pk=pk)
    full_name = hod.get_full_name
    hod.delete()
    messages.success(request, "Department Head" + full_name + " has been deleted.")
    return redirect("hod_list")



@login_required
def hod_team_list(request):
    hod = request.user.username

    # Fetch members who report to the HOD (only usernames)
    members = User.objects.filter(reporting_to=hod)

    # Extract usernames from the queryset
    member_usernames = [member.username for member in members]

    # Print the usernames
    print(member_usernames)  # This will print ['KKOL1948', ...]

    # Loop through each member and get sittings for each
    sittings_data = []
    for member in members:
        sittings = Sitting.objects.filter(user=member.id)
        sittings_data.append({
            'member_fullname': member.get_full_name,
            'member_user': member.username,
            'sittings': sittings
        })

    # Pass the usernames and sittings in the context
    context = {
        'sittings_data': sittings_data,
        'title': 'Team List'
    }

    return render(request, 'team_list.html', context)


def training_calendar(request):
    return render(request, 'training_calendar.html')

def custom_logout_view(request):
    if request.method == 'POST':
        LogoutView(request)
        
        return redirect('home')
    else:
        return redirect('login') 















