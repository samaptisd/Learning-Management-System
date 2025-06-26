from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm

from course.models import Program
from .models import *


# Zone Choices
ZONE = (
    ("Corporate", "Corporate"),
    ("Haridwar", "Haridwar"),
    ("East", "East"),
    ("North", "North"),
    ("South", "South"),
    ("West", "West"),
    ("South & West", "South & West"),
    ("Upper_North", "Upper_North"),
)


# Branch Choices
BRANCH = (
    ("Head Office", "Head Office"),
    ("Unit-I", "Unit-I"),
    ("Unit-I&II&III", "Unit-I&II&III"),
    ("CMDO", "CMDO"),
    ("Unit-II", "Unit-II"),
    ("Unit-III", "Unit-III"),
    ("Kolkata", "Kolkata"),
    ("Delhi", "Delhi"),
    ("Chennai", "Chennai"),
    ("Mumbai", "Mumbai"),
    ("Ahmedabad", "Ahmedabad"),
    ("Hyderabad", "Hyderabad"),
    ("Bangalore", "Bangalore"),
    ("Cochin", "Cochin"),
    ("Unit-I & II", "Unit-I & II"),
    ("MDO", "MDO"),
    ("Pune", "Pune"),
    ("Jaipur", "Jaipur"),
    ("Indore", "Indore"),
    ("Lucknow", "Lucknow"),
    ("Bhiwandi", "Bhiwandi"),
    ("head Office", "head Office"),
    ("Calicut", "Calicut"),
)

class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Username", )

    first_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="First Name", )

    last_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Last Name", )

    zone = forms.ChoiceField(
        choices=ZONE, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Zone", )

    branch = forms.ChoiceField(
        choices=BRANCH, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Branch", )

    department = forms.ChoiceField(
        choices=DEPARTMENT, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Department", )

    course_program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Course Program", )

    date_of_join_in_aludecor = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date of Join in Aludecor", )
    
    reporting_to = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="reporting_to", ) 
        

    phone = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Mobile No.", )

    email = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
        label="Email", )

    password1 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password", )

    password2 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password Confirmation", )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone = self.cleaned_data.get('phone')
        user.zone = self.cleaned_data.get('zone')
        user.branch = self.cleaned_data.get('branch')
        user.department = self.cleaned_data.get('department')
        user.course_program = self.cleaned_data.get('course_program')
        user.date_of_join_in_aludecor = self.cleaned_data.get('date_of_join_in_aludecor')
        user.reporting_to = self.cleaned_data.get('reporting_to')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):

    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'id': 'username_id'
            }
        ),
        label="Username",
    )

    zone = forms.ChoiceField(
        choices=ZONE, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Zone", )

    branch = forms.ChoiceField(
        choices=BRANCH, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Branch", )

    department = forms.ChoiceField(
        choices=DEPARTMENT, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Department", )

    course_program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Course Program", )

    date_of_join_in_aludecor = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date of Join in Aludecor", )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Mobile No.",
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Last name",
    )

    level = forms.CharField(
        widget=forms.Select(
            choices=(
                ('Open', 'Open'),
                ('Basic', 'Basic'),
                ('Intermediate', 'Intermediate'),
                ('Advance', 'Advance'),
            ),
            attrs={
                'class': 'browser-default custom-select form-control',
            }
        ),
    )

    # course = forms.ModelChoiceField(
    #     queryset=Program.objects.all(),
    #     widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
    #     label="Course",
    # )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'type': 'email',
                'class': 'form-control',
            }
        ),
        label="Email Address",
    )

    password1 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password", )

    password2 = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
        label="Password Confirmation", )
    
    reporting_to = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Reporting To",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.zone = self.cleaned_data.get('zone')
        user.branch = self.cleaned_data.get('branch')
        user.department = self.cleaned_data.get('department')
        user.course_program = self.cleaned_data.get('course_program')
        user.date_of_join_in_aludecor = self.cleaned_data.get('date_of_join_in_aludecor')
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        user.reporting_to = self.cleaned_data.get('reporting_to')
        user.save()
        department_instance = Department.objects.get(name=self.cleaned_data.get('department'))

        student = Student.objects.create(
            student=user,
            level=self.cleaned_data.get('level'),
            department=department_instance
        )
        student.save()
        return user


def validate_file_size(value):
    max_size_mb = 3  # Maximum file size in MB
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if value.size > max_size_bytes:
        raise forms.ValidationError(f"The maximum file size that can be uploaded is {max_size_mb} MB.")


class ProfileUpdateForm(UserChangeForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'type': 'email', 'class': 'form-control', 'readonly': 'readonly'}),
        label="Email Address",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'}),
        label="First Name",
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'readonly': 'readonly'}),
        label="Last Name",
    )
    picture = forms.ImageField(
        required=False,
        validators=[validate_file_size],  # Ensure size validation is applied
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Profile Picture",
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'picture'] 


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address. "
            self.add_error('email', msg)
            return email


class ParentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'autocomplete': 'username'
            }
        ),
        label="Username",
    )

    zone = forms.ChoiceField(
        choices=ZONE, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Zone", )

    branch = forms.ChoiceField(
        choices=BRANCH, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Branch", )

    department = forms.ChoiceField(
        choices=DEPARTMENT, widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Department", )

    course_program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Course Program", )

    date_of_join_in_aludecor = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date of Join in Aludecor", )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Mobile No.",
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
            }
        ),
        label="Last name",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'type': 'email',
                'class': 'form-control',
            }
        ),
        label="Email Address",
    )

    aludecorian = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
        label="Aludecorian",
    )

    password1 = forms.CharField(
    max_length=30, 
    widget=forms.TextInput(
        attrs={
            'type': 'password',
            'class': 'form-control',
            'autocomplete': 'new-password',  # Correct for new password
        }
    ),
    label="Password",
)

    password2 = forms.CharField(
    max_length=30, 
    widget=forms.TextInput(
        attrs={
            'type': 'password',
            'class': 'form-control',
            'autocomplete': 'new-password',  # Change this to new-password
        }
    ),
    label="Password Confirmation",
)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.zone = self.cleaned_data.get('zone')
        user.branch = self.cleaned_data.get('branch')
        user.department = self.cleaned_data.get('department')
        user.course_program = self.cleaned_data.get('course_program')
        user.date_of_join_in_aludecor = self.cleaned_data.get('date_of_join_in_aludecor')
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        user.reporting_to = self.cleaned_data.get('reporting_to')
        user.picture = self.cleaned_data.get('picture')

        user.save()
        
        return user
