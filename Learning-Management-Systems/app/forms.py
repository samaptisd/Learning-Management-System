from django import forms
from django.db import transaction

from .models import NewsAndEvents, Session, Semester, SEMESTER


# news and events
class NewsAndEventsForm(forms.ModelForm):
    class Meta:
        model = NewsAndEvents
        fields = ('title', 'summary', 'posted_as',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})
        self.fields['posted_as'].widget.attrs.update({'class': 'form-control'})


class SessionForm(forms.ModelForm):
    next_session_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                'type': 'date',
            }
        ),
        required=True)

    class Meta:
        model = Session
        fields = ['session', 'is_current_session', 'next_session_begins']


class SemesterForm(forms.ModelForm):
    semester = forms.ChoiceField(
        choices=(
            ('Open', 'Open'),
            ('Basic', 'Basic'),
            ('Intermediate', 'Intermediate'),
            ('Advance', 'Advance'),
        ),
        widget=forms.Select(
            attrs={
                'class': 'browser-default custom-select',
            }
        ),
        label="Level",
    )

    is_current_semester = forms.ChoiceField(
        choices=(
            ('Yes', 'Yes'),
            ('No', 'No'),
        ),
        widget=forms.Select(
            attrs={
                'class': 'browser-default custom-select',
            }
        ),
        label="Is Current Level?",
    )

    next_level_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
        required=True,
        label="Next Level Begins",
    )

    class Meta:
        model = Semester
        fields = ['semester', 'is_current_semester', 'session', 'next_level_begins']
        labels = {
            'semester': 'Level',
            'is_current_semester': 'Is Current Level?',
            'next_level_begins': 'Next Level Begins',
        }
