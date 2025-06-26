from django import forms
from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User

from accounts.models import User
from .models import Program, Course, CourseAllocation, Upload, UploadVideo,CourseAllocationLearner,CourseRequest




# User = settings.AUTH_USER_MODEL

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})


class CourseAddForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['code'].widget.attrs.update({'class': 'form-control'})
        # self.fields['courseUnit'].widget.attrs.update({'class': 'form-control'})
        self.fields['credit'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})
        self.fields['program'].widget.attrs.update({'class': 'form-control'})
        self.fields['level'].widget.attrs.update({'class': 'form-control'})
        self.fields['vertical'].widget.attrs.update({'class': 'form-control'})
        self.fields['language'].widget.attrs.update({'class': 'form-control'})


class CourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by('level'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'browser-default checkbox'}),
        required=True
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={'class': 'browser-default custom-select'}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ['lecturer', 'courses']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(is_lecturer=True)


class EditCourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by('level'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(attrs={'class': 'browser-default custom-select'}),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ['lecturer', 'courses']

    def __init__(self, *args, **kwargs):
        #    user = kwargs.pop('user')
        super(EditCourseAllocationForm, self).__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(is_lecturer=True)


# Upload files to specific course
class UploadFormFile(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ('title', 'file', 'course',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})


# Upload video to specific course
class UploadFormVideo(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = ('title', 'video', 'course',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['video'].widget.attrs.update({'class': 'form-control'})


class CourseAllocationLearnerForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(is_student=True),
        label="Student",
        widget=forms.Select
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Courses"
    )

    class Meta:
        model = CourseAllocationLearner
        fields = ['student', 'courses']

    def __init__(self, *args, **kwargs):
        # Capture the request user passed as an argument
        user = kwargs.pop('user', None)
        super(CourseAllocationLearnerForm, self).__init__(*args, **kwargs)

        if user and user.is_dep_head:  
            self.fields['student'].queryset = User.objects.filter(reporting_to=user.username, is_student=True)
        else:
            self.fields['student'].queryset = User.objects.filter(is_student=True)



class CourseRequestForm(forms.ModelForm):
    class Meta:
        model = CourseRequest
        fields = ['team_member', 'program', 'course', 'level', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program'].queryset = Program.objects.all()
        self.fields['course'].queryset = Course.objects.none()

        # Dynamically filter courses based on program selection
        if 'program' in self.data:
            try:
                program_id = int(self.data.get('program'))
                self.fields['course'].queryset = Course.objects.filter(program_id=program_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['course'].queryset = self.instance.program.courses.all()



class AdminApprovalForm(forms.ModelForm):
    class Meta:
        model = CourseRequest
        fields = ['status']






