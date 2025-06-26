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

import logging

logger = logging.getLogger(__name__)


from django.shortcuts import render
from django.http import HttpResponse
import xlwt
from django.db import connection
from .models import User

from django.shortcuts import render
from .models import UserActivityLog


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .serializers import UserSerializer

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime



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
        # Use filter instead of get, since there might be multiple student records
        levels = Student.objects.filter(student__pk=request.user.id)
        
        # Select the first student from the queryset
        if levels.exists():
            level = levels.first()  # Choose the first record or adjust based on your logic
        else:
            level = None
        try:
            departmentHead = DepartmentHead.objects.get(department=level.department) if level else "No DepartmentHead set"
        except DepartmentHead.DoesNotExist:
            departmentHead = "No DepartmentHead set"

        courses = TakenCourse.objects.filter(
            student__student__id=request.user.id, course__level=level.level
        ) if level else []

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
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage



@login_required
def profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            if 'picture' in request.FILES:
                picture = request.FILES['picture']
                fs = FileSystemStorage(location='/var/www/gyandhara/media/profile_pictures/')
                filename = fs.save(picture.name, picture)
                uploaded_file_url = fs.url(filename)
                print(f"Uploaded File URL: {uploaded_file_url}")
                request.user.picture = f"profile_pictures/{filename}"
            
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect(reverse("profile"))
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
        form = PasswordChangeForm(request.POST, request.FILES, instance=request.user)
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
        print(request.POST)  # Debugging request data
        
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    "Account for {} {} has been created.".format(
                        form.cleaned_data.get('first_name'), 
                        form.cleaned_data.get('last_name'),
                        form.cleaned_data.get('department')
                    )
                )
                return redirect("student_list")
            except Exception as e:
                logger.error(f"Error while saving student data: {e}")  # Log error
                messages.error(request, "An error occurred while saving the student data.")
        else:
            logger.error(f"Form errors: {form.errors}")  # Log form errors
            print(form.errors)  # Also print the form errors for debugging
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
    paginate_by = 1000  # if pagination is desired

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

from django.db.models import Q

@method_decorator([login_required, admin_required], name="dispatch")
class hodListView(ListView):
    model = User
    template_name = "accounts/hod_list.html"
    paginate_by = 1000  # Adjust as needed

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_dep_head=True)

        # Retrieve filter parameters
        query = self.request.GET.get("name", "").strip()
        email = self.request.GET.get("email", "").strip()
        user_id = self.request.GET.get("id", "").strip()  # Using 'id' instead of 'id_no'

        # Apply filters dynamically
        if query or email or user_id:
            filters = Q()
            if query:
                filters |= Q(first_name__icontains=query) | Q(last_name__icontains=query)
            if email:
                filters |= Q(email__icontains=email)
            if user_id:
                filters |= Q(id=user_id)  # Filter using the correct field
            queryset = queryset.filter(filters)

        return queryset

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



# @login_required
# def hod_team_list(request):
#     hod = request.user.username

#     # Fetch members who report to the HOD (only usernames)
#     members = User.objects.filter(reporting_to=hod)

#     # Extract usernames from the queryset
#     member_usernames = [member.username for member in members]

#     # Print the usernames
#     print(member_usernames)  # This will print ['KKOL1948', ...]

#     # Loop through each member and get sittings for each
#     sittings_data = []
#     for member in members:
#         sittings = Sitting.objects.filter(user=member.id)
#         sittings_data.append({
#             'member_fullname': member.get_full_name,
#             'member_user': member.username,
#             'sittings': sittings
#         })

#     # Pass the usernames and sittings in the context
#     context = {
#         'sittings_data': sittings_data,
#         'title': 'Team List'
#     }

#     return render(request, 'team_list.html', context)

@login_required
def hod_team_list(request):
    hod_username = request.user.username  # logged-in user

    with connection.cursor() as cursor:
        # Team course detail query
        cursor.execute("""
            SELECT 
                ru.username AS reporting_to_id,
                CONCAT(ru.first_name, ' ', ru.last_name) AS reporting_to_name,
                u.username AS user_id,
                CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                cp.title AS program_name,
                cc.title AS course_name,
                cc.code AS code
            FROM 
                elearn.accounts_student s
            JOIN 
                elearn.accounts_user u ON u.id = s.student_id
            JOIN 
                elearn.accounts_user ru ON u.reporting_to = ru.username
            JOIN 
                elearn.course_course cc ON s.course_id = cc.id
            JOIN 
                elearn.course_program cp ON s.program_id = cp.id
            WHERE 
                ru.username = %s
        """, [hod_username])

        team_columns = [col[0] for col in cursor.description]
        team_data = [dict(zip(team_columns, row)) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        # Team summary query
        cursor.execute("""
            SELECT 
                u.username AS user_id,
                CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                COUNT(*) AS total_courses,
                SUM(CASE WHEN cc.code LIKE 'OP%%' THEN 1 ELSE 0 END) AS op_courses,
                SUM(CASE WHEN cc.code NOT LIKE 'OP%%' THEN 1 ELSE 0 END) AS other_courses
            FROM 
                elearn.accounts_student s
            JOIN 
                elearn.accounts_user u ON u.id = s.student_id
            JOIN 
                elearn.accounts_user ru ON u.reporting_to = ru.username
            JOIN 
                elearn.course_course cc ON s.course_id = cc.id
            WHERE 
                ru.username = %s
            GROUP BY 
                u.id, u.username, u.first_name, u.last_name;
        """, [hod_username])

        summary_columns = [col[0] for col in cursor.description]
        summary_data = [dict(zip(summary_columns, row)) for row in cursor.fetchall()]

    return render(request, 'team_list.html', {
        'title': 'Team Summary',
        'team_data': team_data,
        'summary_data': summary_data
    })




@login_required
def admin_team_list(request):
    with connection.cursor() as cursor:
        # Summary query
        cursor.execute("""
            SELECT 
                ru.username AS reporting_to_id,
                CONCAT(ru.first_name, ' ', ru.last_name) AS reporting_to_name,
                COUNT(DISTINCT u.id) AS total_team,
                COUNT(*) AS total_courses,
                SUM(CASE WHEN cc.code LIKE 'OP%%' THEN 1 ELSE 0 END) AS op_courses,
                SUM(CASE WHEN cc.code NOT LIKE 'OP%%' THEN 1 ELSE 0 END) AS other_courses
            FROM 
                elearn.accounts_student s
            JOIN 
                elearn.accounts_user u ON u.id = s.student_id
            JOIN 
                elearn.accounts_user ru ON u.reporting_to = ru.username
            JOIN 
                elearn.course_course cc ON s.course_id = cc.id
            GROUP BY 
                ru.username, ru.first_name, ru.last_name;
        """)
        summary_columns = [col[0] for col in cursor.description]
        summary_data = [dict(zip(summary_columns, row)) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        # Detail table query
        cursor.execute("""
            SELECT 
                ru.username AS reporting_to_id,
                CONCAT(ru.first_name, ' ', ru.last_name) AS reporting_to_name,
                u.username AS user_id,
                CONCAT(u.first_name, ' ', u.last_name) AS user_name,
                cp.title AS program_name,
                cc.title AS course_name,
                cc.code AS code
            FROM 
                elearn.accounts_student s
            JOIN 
                elearn.accounts_user u ON u.id = s.student_id
            JOIN 
                elearn.accounts_user ru ON u.reporting_to = ru.username
            JOIN 
                elearn.course_course cc ON s.course_id = cc.id
            JOIN 
                elearn.course_program cp ON s.program_id = cp.id;
        """)
        detail_columns = [col[0] for col in cursor.description]
        team_data = [dict(zip(detail_columns, row)) for row in cursor.fetchall()]

    return render(request, 'admin_team_list.html', {
        'title': 'Admin Team Overview',
        'summary_data': summary_data,
        'team_data': team_data
    })



def training_calendar(request):
    return render(request, 'training_calendar.html')

def custom_logout_view(request):
    if request.method == 'POST':
        LogoutView(request)
        
        return redirect('home')
    else:
        return redirect('login') 
    

from django.shortcuts import render
from django.http import HttpResponse
import xlwt
from django.db import connection
from .models import User
from datetime import datetime

def download_report(request):
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        report_type = request.POST.get("report_type")

        quiz_report_query = ""
        columns = []

        if report_type == "zone_wise":
            zone = request.POST.get("zone")
            if zone:
                quiz_report_query = f"""
                
                
                    SELECT 
                      u.date_joined AS Date_joined,
    u.zone AS Zone, 
    u.username AS User_Name, 
    CONCAT(u.first_name, ' ', u.last_name) AS Fullname, 
    u.phone AS Phone, 
    u.email AS Email, 
    u.department AS Designation, 
    u.branch AS Branch, 
    CONCAT(r.first_name, ' ', r.last_name) AS Reporting_To, 
    cp.title AS Program_Title, 
    c.title AS Course_Title, 
    COUNT(qs.id) AS No_of_Attempt, 
    MAX(qs.current_score) AS Score_Received, 
    CONCAT(
        ROUND(
            MAX(qs.current_score) / (
                MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1)
            ) * 100, 
            2
        ), '%'
    ) AS Score, 
    CASE 
        WHEN MAX(qs.current_score) >= (
            MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 0.95
        ) THEN 'Pass'
        ELSE 'Fail'
    END AS Assessment_Status_Pass_or_Fail
FROM 
    elearn.accounts_user AS u
JOIN 
    elearn.accounts_student AS s ON u.id = s.student_id
JOIN 
    elearn.course_program AS cp ON s.program_id = cp.id
JOIN 
    elearn.course_course AS c ON s.course_id = c.id
JOIN 
    elearn.quiz_sitting AS qs ON u.id = qs.user_id
LEFT JOIN 
    elearn.accounts_user AS r ON u.reporting_to = r.username
WHERE 
    u.zone = '{zone}' 
    AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'
GROUP BY 
    u.zone, u.username, u.first_name, u.last_name, u.phone, u.email, 
    u.department, u.branch, r.first_name, r.last_name, cp.title, c.title
ORDER BY 
     Fullname, Program_Title, Course_Title;

                """
                columns = ['Month of Couse Assignment', 'Zone', 'User Name', 'Fullname', 'Phone', 'Email', 'Designation', 'Branch',  'Reporting To', 'Program Title','Course Title','No. of Attempt','Score Received','Score %','Assessment Status(Pass/Fail)']

                if from_date and to_date:
                    # quiz_report_query += f" AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'"
                    quiz_report_query = quiz_report_query.replace('\n', ' ').strip()




        elif report_type == "branch_wise":
            branch = request.POST.get("branch")
            if branch:
                quiz_report_query = f"""
               SELECT 
                      u.date_joined AS Date_joined,
    u.zone AS Zone, 
    u.username AS User_Name, 
    CONCAT(u.first_name, ' ', u.last_name) AS Fullname, 
    u.phone AS Phone, 
    u.email AS Email, 
    u.department AS Designation, 
    u.zone AS zone, 
    CONCAT(r.first_name, ' ', r.last_name) AS Reporting_To, 
    cp.title AS Program_Title, 
    c.title AS Course_Title, 
    COUNT(qs.id) AS No_of_Attempt, 
    MAX(qs.current_score) AS Score_Received, 
    CONCAT(
        ROUND(
            MAX(qs.current_score) / (
                MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1)
            ) * 100, 
            2
        ), '%'
    ) AS Score, 
    CASE 
        WHEN MAX(qs.current_score) >= (
            MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 0.95
        ) THEN 'Pass'
        ELSE 'Fail'
    END AS Assessment_Status_Pass_or_Fail
FROM 
    elearn.accounts_user AS u
JOIN 
    elearn.accounts_student AS s ON u.id = s.student_id
JOIN 
    elearn.course_program AS cp ON s.program_id = cp.id
JOIN 
    elearn.course_course AS c ON s.course_id = c.id
JOIN 
    elearn.quiz_sitting AS qs ON u.id = qs.user_id
LEFT JOIN 
    elearn.accounts_user AS r ON u.reporting_to = r.username
WHERE 
    u.branch = '{branch}' 
    AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'
GROUP BY 
    u.branch, u.username, u.first_name, u.last_name, u.phone, u.email, 
    u.department, r.first_name, r.last_name, cp.title, c.title
ORDER BY 
     Fullname, Program_Title, Course_Title;
                """
                columns = ['Month of Couse Assignment', 'Branch', 'User Name', 'Fullname', 'Phone', 'Email', 'Designation', 'Branch',  'Reporting To', 'Program Title','Course Title','No. of Attempt','Score Received','Score %','Assessment Status(Pass/Fail)']

                if from_date and to_date:
                    # quiz_report_query += f" AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'"
                    quiz_report_query = quiz_report_query.replace('\n', ' ').strip()
                    

        elif report_type == "department_wise":
            department = request.POST.get("department")
            if department:
                quiz_report_query = f"""
                SELECT 
                      u.date_joined AS Date_joined,
    u.zone AS Zone, 
    u.username AS User_Name, 
    CONCAT(u.first_name, ' ', u.last_name) AS Fullname, 
    u.phone AS Phone, 
    u.email AS Email, 
    u.branch AS Branch, 
    u.zone AS Zone, 
    CONCAT(r.first_name, ' ', r.last_name) AS Reporting_To, 
    cp.title AS Program_Title, 
    c.title AS Course_Title, 
    COUNT(qs.id) AS No_of_Attempt, 
    MAX(qs.current_score) AS Score_Received, 
    CONCAT(
        ROUND(
            MAX(qs.current_score) / (
                MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1)
            ) * 100, 
            2
        ), '%'
    ) AS Score, 
    CASE 
        WHEN MAX(qs.current_score) >= (
            MAX(LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 0.95
        ) THEN 'Pass'
        ELSE 'Fail'
    END AS Assessment_Status_Pass_or_Fail
FROM 
    elearn.accounts_user AS u
JOIN 
    elearn.accounts_student AS s ON u.id = s.student_id
JOIN 
    elearn.course_program AS cp ON s.program_id = cp.id
JOIN 
    elearn.course_course AS c ON s.course_id = c.id
JOIN 
    elearn.quiz_sitting AS qs ON u.id = qs.user_id
LEFT JOIN 
    elearn.accounts_user AS r ON u.reporting_to = r.username
WHERE 
    u.department = '{department}' 
    AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'
GROUP BY 
    u.username, u.first_name, u.last_name, u.phone, u.email, 
    u.department, u.branch, r.first_name, r.last_name, cp.title, c.title
ORDER BY 
     Fullname, Program_Title, Course_Title;
                """
                columns = ['Month of Couse Assignment', 'Zone', 'User Name', 'Fullname', 'Phone', 'Email', 'Designation', 'Branch',  'Reporting To', 'Program Title','Course Title','No. of Attempt','Score Received','Score %','Assessment Status(Pass/Fail)']

                if from_date and to_date:
                    # quiz_report_query += f" AND u.date_joined BETWEEN '{from_date}' AND '{to_date}'"
                     quiz_report_query = quiz_report_query.replace('\n', ' ').strip()

        elif report_type == "quiz_report":
            quiz_report_query = """
             SELECT 
                q.content AS question_content,
                qc.choice AS user_answer,
                (SELECT choice FROM elearn.quiz_choice WHERE question_id = q.id AND correct = 1 LIMIT 1) AS correct_answer, 
                u.username AS username,
                CONCAT(u.first_name, ' ', u.last_name) AS full_name,
                qs.start AS date
             FROM 
                elearn.quiz_sitting qs
             JOIN 
                elearn.quiz_question q ON FIND_IN_SET(q.id, qs.incorrect_questions)
             JOIN 
                elearn.quiz_choice qc ON qc.question_id = q.id 
             JOIN 
                elearn.accounts_user u ON qs.user_id = u.id 
             WHERE 
                qs.complete = 1
            """
            columns = ['Question', 'User Answer', 'Correct Answer', 'Username', 'Full Name', 'Date']

            if from_date and to_date:
                quiz_report_query += f" AND qs.start BETWEEN '{from_date}' AND '{to_date}'"

        elif report_type == "score_board":
            quiz_report_query = f"""
             SELECT 
                u.username AS Username,                                                   
                CONCAT(u.first_name, ' ', u.last_name) AS Fullname,   
                u.phone AS Phone, 
				u.email AS Email, 
				u.department AS Department, 
				u.branch AS Branch, 
                u.zone As Zone,                    
                LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1  AS Total_Questions,
                LENGTH(qs.user_answers) - LENGTH(REPLACE(qs.user_answers, ',', '')) + 1  AS Attempted,      
                LENGTH(qs.incorrect_questions) - LENGTH(REPLACE(qs.incorrect_questions, ',', '')) + 1 AS Incorrect_Questions,
                (LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) - (LENGTH(qs.incorrect_questions) - LENGTH(REPLACE(qs.incorrect_questions, ',', '')) + 1) AS Correct_Questions, 
                qs.current_score AS Total_Score,                                         
                CONCAT(ROUND(qs.current_score / (LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 100, 2), '%') AS Score, 
                CONCAT(ROUND((LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 0.95, 2)) AS Passing_Score, 
                CONCAT(95, '%') AS Passing_Percentage,                                    
                
                CASE 
                    WHEN qs.current_score >= (LENGTH(qs.question_order) - LENGTH(REPLACE(qs.question_order, ',', '')) + 1) * 0.95 THEN 'Pass'
                    ELSE 'Fail'
                END AS Pass_Fail                                                          
            FROM 
                elearn.accounts_user u
            JOIN 
                elearn.quiz_sitting qs ON u.id = qs.user_id
            WHERE
                qs.start BETWEEN '{from_date}' AND '{to_date}'                            
            GROUP BY 
                u.username, u.first_name, u.last_name, qs.current_score, qs.question_order, qs.user_answers, qs.incorrect_questions, qs.complete
            """
            columns = ['Username', 'Fullname', 'Department','Department','Mobile Number', 'E-Mail','Zone','Branch','Attempted', 'Incorrect_Questions', 'Correct_Questions', 'Total_Score', 'Score(%)', 'Passing_Score', 'Passing_Percentage', 'Pass_Fail']

        if quiz_report_query:
            with connection.cursor() as cursor:
                cursor.execute(quiz_report_query)
                results = cursor.fetchall()

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Report')

            for col_num, column in enumerate(columns):
                ws.write(0, col_num, column)

            date_style = xlwt.XFStyle()
            date_style.num_format_str = 'DD/MM/YYYY'

            number_style = xlwt.XFStyle()
            number_style.num_format_str = '#,##0'

            for row_num, row_data in enumerate(results, start=1):
                for col_num, data in enumerate(row_data):
                    # Apply date formatting if the data is of type `datetime`
                    if isinstance(data, datetime):
                        ws.write(row_num, col_num, data.strftime('%d/%m/%Y'), date_style)
                    elif isinstance(data, int) and col_num in [2, 3, 4, 5, 6]:  # Number columns for Total_Questions, Attempted, Incorrect, etc.
                        ws.write(row_num, col_num, data, number_style)
                    else:
                        ws.write(row_num, col_num, data)

            wb.save(response)
            return response

    else:
        departments = User.objects.values_list('department', flat=True).distinct()
        zones = User.objects.values_list('zone', flat=True).distinct()
        branches = User.objects.values_list('branch', flat=True).distinct()

        context = {
            'departments': departments,
            'zones': zones,
            'branches': branches,
        }

        return render(request, 'download_report.html', context)
    



from django.contrib.auth import logout
from .models import UserActivityLog
import re
from django.utils.timezone import now

def log_user_activity(user, action, url_path, method):
    """
    Logs user activity only for video tutorial detail pages:
    /programs/course/<id>/video_tutorials/<id>/detail/
    """

    if not user.is_authenticated:
        return None

    # Ensure only video detail pages are logged
    video_page_pattern = r"^/programs/course/\d+/video_tutorials/\d+/detail/?$"
    if not re.match(video_page_pattern, url_path):
        return None

    # Close the previous activity if still open and URL has changed
    last_log = UserActivityLog.objects.filter(user=user, end_time__isnull=True).order_by('-start_time').first()

    if last_log and last_log.url != url_path:
        last_log.end_time = now()
        last_log.duration = last_log.end_time - last_log.start_time
        last_log.save()

    # Log new page session
    return UserActivityLog.objects.create(
        user=user,
        username=user.get_full_name(),
        action=action,
        url=url_path,
        method=method,
        start_time=now()
    )


@login_required
def video_detail_view(request, course_id, video_id):
    # This is the correct place to add the logging call
    log_user_activity(
        user=request.user,
        action='view_video',
        url_path=request.path,
        method=request.method
    )

    video = get_object_or_404(video_detail_view, id=video_id, course_id=course_id)
    return render(request, 'video_detail.html', {'video': video})


def update_end_time_and_duration(log_entry):
    """ Update end time and calculate duration. """
    if log_entry and not log_entry.end_time:
        log_entry.end_time = now()
        log_entry.duration = log_entry.end_time - log_entry.start_time
        log_entry.save()
        print(f"Updated log for {log_entry.user.username}: End Time - {log_entry.end_time}, Duration - {log_entry.duration}")


# User login view (assuming login is handled elsewhere)
def user_login(request):
    if request.method == 'POST':
        # After successful login
        log_user_activity(request.user, "Logged In", request.get_full_path(), request.method)
        return redirect('home')

# User logout view
def user_logout(request):
    """ Logout user and update activity log. """
    if request.user.is_authenticated:
        last_log = UserActivityLog.objects.filter(user=request.user, end_time__isnull=True).order_by('-start_time').first()
        
        if last_log:
            update_end_time_and_duration(last_log)  # Update before logout
        
        logout(request)

    return redirect('home')

# View for displaying the user activity log
# def user_activity_log_view(request):
#     logs = UserActivityLog.objects.all().order_by('-start_time')
#     return render(request, 'user_activity_log.html', {'logs': logs})


def user_activity_log_view(request):
    # Ensure all logs are updated before rendering
    logs = UserActivityLog.objects.all().order_by('-start_time')

    # Debugging: Print logs with missing end_time
    for log in logs:
        if log.end_time is None:
            print(f"Missing end_time for {log.user.username}: Log started at {log.start_time}")

    return render(request, 'user_activity_log.html', {'logs': logs})

import xlwt
from django.http import HttpResponse
from .models import UserActivityLog

def export_to_excel(request):
    # Create a new workbook and sheet
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('User Activity Logs')

    # Define font style for the header
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # Write the header row
    columns = ['User', 'Name','Action', 'URL', 'Method', 'Start Time', 'End Time', 'Duration']
    
    for col_num, column in enumerate(columns):
        ws.write(0, col_num, column, font_style)

    # Fetch logs from the database
    logs = UserActivityLog.objects.all()

    # Write data rows
    for row_num, log in enumerate(logs, start=1):
        ws.write(row_num, 0, log.user.username)
        ws.write(row_num, 1, log.user.get_full_name)
        ws.write(row_num, 2, log.action)
        ws.write(row_num, 3, log.url)
        ws.write(row_num, 4, log.method)
        ws.write(row_num, 5, log.start_time.strftime('%Y-%m-%d %H:%M:%S') if log.start_time else '')
        ws.write(row_num, 6, log.end_time.strftime('%Y-%m-%d %H:%M:%S') if log.end_time else '')
        ws.write(row_num, 7, str(log.duration) if log.duration else '')

    # Create an HTTP response with Excel content
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=user_activity_logs.xls'

    # Save the workbook to the response
    wb.save(response)

    return response



class SyncUserView(APIView):
    def post(self, request):
        try:
            data = request.data
            # Hash the password if provided
            if 'password' in data:
                data['password'] = make_password(data['password'])
            
            user, created = User.objects.update_or_create(
                id=data['id'],  # Use 'id' as the unique identifier
                defaults=data
            )
            return Response({'message': 'User synced successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        





class ExportDataToSheet(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch data from the database
        query = """
        SELECT 
    u.username AS username,
    u.first_name AS student_first_name,
    u.last_name AS student_last_name,
    u.email AS student_email,
    u.zone AS zone,
    u.branch AS branch,
    u.department AS department,
    c.program_id AS program_id,
    p.title AS program_name,
    c.id AS course_id,
    c.title AS course_name,
    c.timestamp AS assign_date
FROM 
    elearn.accounts_student s
JOIN 
    elearn.accounts_user u ON s.student_id = u.id
JOIN 
    elearn.course_program p ON s.program_id = p.id
JOIN 
    elearn.course_course c ON p.id = c.program_id
ORDER BY 
    u.first_name, u.last_name, p.title, c.title;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        # Convert datetime objects to string
        processed_rows = []
        for row in rows:
            processed_row = []
            for value in row:
                if isinstance(value, datetime):
                    processed_row.append(value.strftime('%Y-%m-%d %H:%M:%S'))  # Format datetime as a string
                else:
                    processed_row.append(value)
            processed_rows.append(processed_row)

        # Google Sheets API setup
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('/var/www/gyandhara/credentials.json', scope)
        client = gspread.authorize(credentials)

        # Open the Google Sheet
        sheet = client.open("Programs & Course").sheet1

        # Write header to Google Sheet
        sheet.clear()
        sheet.append_row(columns)

        # Write data to Google Sheet
        for row in processed_rows:
            sheet.append_row(row)

        return Response({"message": "Data exported successfully to Google Sheet!"})
    



# Google Sheets API setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_PATH = "/var/www/gyandhara/credentials.json"  # Update with actual path

class ImportCourse(APIView):
    def post(self, request):
        try:
            data = request.data

            # Check if 'id' exists
            if "id" not in data or not isinstance(data["id"], (int, str)):
                return Response({"error": "Missing or invalid 'id' field"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if student_id exists in accounts_user
            student_id = data.get("student_id", None)
            if not Student.objects.filter(id=student_id).exists():
                return Response({"error": f"Student ID {student_id} does not exist in accounts_user"}, status=status.HTTP_400_BAD_REQUEST)

            # Convert timestamp if present
            timestamp = None
            if "timestamp" in data and data["timestamp"]:
                try:
                    timestamp = datetime.strptime(str(data["timestamp"]), "%H:%M:%S.%f")  # Adjust format if needed
                except ValueError:
                    timestamp = None  # Handle incorrect timestamps

            # Insert or update data
            student, created = Student.objects.update_or_create(
                id=data["id"],
                defaults={
                    "level": data.get("level", None),
                    "department_id": data.get("department_id", None),
                    "student_id": student_id,
                    "id_number": data.get("id_number", None),
                    "course_id": data.get("course_id", None),
                    "program_id": data.get("program_id", None),
                    "timestamp": timestamp
                }
            )

            return Response({"message": "Data successfully imported from Google Sheets to MySQL"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



from collections import Counter, defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import localtime
from django.contrib.auth import get_user_model
from .models import UserActivityLog  # Ensure your model is imported

User = get_user_model()

@login_required
def user_activity_log_view(request):
    logs = UserActivityLog.objects.select_related('user').filter(
        url__startswith="https://aluedge.aludecor.co.in/programs/course/"
    ).exclude(
        url__startswith="https://aluedge.aludecor.co.in/programs/course/assign"
    ).exclude(
        url__startswith="https://aluedge.aludecor.co.in/programs/course/allocated"
    ).order_by('-start_time')

    # Totals
    total_logs = logs.count()
    total_users = logs.values('user').distinct().count()
    total_duration_sec = sum((log.duration.total_seconds() for log in logs if log.duration), 0)

    # Chart data collections
    action_user_count = Counter()
    user_duration_data = defaultdict(float)
    month_user_count = defaultdict(set)
    hours = int(total_duration_sec // 3600)
    minutes = int((total_duration_sec % 3600) // 60)
    seconds = int(total_duration_sec % 60)
    for log in logs:
        if log.user and log.action:
            # Action-wise counter
            action_user_count[log.action] += 1

            # Full name fallback
            full_name = f"{log.user.first_name} {log.user.last_name}".strip()
            if not full_name:
                full_name = log.user.username

            # User-wise duration
            if log.duration:
                user_duration_data[full_name] += log.duration.total_seconds()

            # Month-wise count
            if log.start_time:
                month = localtime(log.start_time).strftime("%b %Y")
                month_user_count[month].add(log.user.username)

    # Top 5 values
    top_actions = action_user_count.most_common(5)
    top_users = sorted(user_duration_data.items(), key=lambda x: x[1], reverse=True)[:5]
    top_months = sorted(month_user_count.items())  # Already trimmed in chart
    
    context = {
        'logs': logs,
        'total_reports': total_logs,
        'total_users': total_users,
        'total_spent_time': f"{hours} hr {minutes} min {seconds} sec",


        # For 3D charts
        'action_3d_data': [[label, count] for label, count in top_actions],
        'user_labels': [user for user, _ in top_users],
        'user_durations': [duration for _, duration in top_users],
        'month_labels': [month for month, _ in top_months],
        'month_user_counts': [len(users) for _, users in top_months],
    }

    return render(request, 'user_activity_log.html', context)


























 















