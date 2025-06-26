import random

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView, CreateView, FormView, DeleteView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.utils.html import escape

from accounts.decorators import student_required, lecturer_required
from .models import *
from .forms import *
from accounts.models import Student

from django.http import HttpResponse

import xlwt
from .models import Sitting

from django.core.files.storage import FileSystemStorage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
import os
from reportlab.lib.units import inch

from PIL import Image


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os
from django.conf import settings
from django.db import connection
from django.shortcuts import render
from reportlab.lib.pagesizes import landscape, A4



@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizAddForm

    def get_context_data(self, *args, **kwargs):
        context = super(QuizCreateView, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        if self.request.POST:
            context['form'] = QuizAddForm(self.request.POST)
            # context['quiz'] = self.request.POST.get('quiz')
        else:
            context['form'] = QuizAddForm(initial={'course': Course.objects.get(slug=self.kwargs['slug'])})
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data()
        form = context['form']
        with transaction.atomic():
            self.object = form.save()
            if form.is_valid():
                form.instance = self.object
                form.save()
                return redirect('mc_create', slug=self.kwargs['slug'], quiz_id=form.instance.id)
        return super(QuizCreateView, self).form_invalid(form)


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizAddForm

    def get_context_data(self, *args, **kwargs):
        context = super(QuizUpdateView, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        quiz = Quiz.objects.get(pk=self.kwargs['pk'])
        if self.request.POST:
            context['form'] = QuizAddForm(self.request.POST, instance=quiz)
        else:
            context['form'] = QuizAddForm(instance=quiz)
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data()
        course = context['course']
        form = context['form']
        with transaction.atomic():
            self.object = form.save()
            if form.is_valid():
                form.instance = self.object
                form.save()
                return redirect('quiz_index', course.slug)
        return super(QuizUpdateView, self).form_invalid(form)


@login_required
@lecturer_required
def quiz_delete(request, slug, pk):
    quiz = Quiz.objects.get(pk=pk)
    course = Course.objects.get(slug=slug)
    quiz.delete()
    messages.success(request, f'successfuly deleted.')
    return redirect('quiz_index', quiz.course.slug)


@method_decorator([login_required, lecturer_required], name='dispatch')
class MCQuestionCreate(CreateView):
    model = MCQuestion
    form_class = MCQuestionForm

    def get_context_data(self, **kwargs):
        context = super(MCQuestionCreate, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        context['quiz_obj'] = Quiz.objects.get(id=self.kwargs['quiz_id'])
        context['quizQuestions'] = Question.objects.filter(quiz=self.kwargs['quiz_id']).count()
        if self.request.POST:
            context['form'] = MCQuestionForm(self.request.POST)
            context['formset'] = MCQuestionFormSet(self.request.POST)
        else:
            context['form'] = MCQuestionForm(initial={'quiz': self.kwargs['quiz_id']})
            context['formset'] = MCQuestionFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        course = context['course']
        with transaction.atomic():
            form.instance.question = self.request.POST.get('content')
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                if "another" in self.request.POST:
                    return redirect('mc_create', slug=self.kwargs['slug'], quiz_id=self.kwargs['quiz_id'])
                return redirect('quiz_index', course.slug)
        return super(MCQuestionCreate, self).form_invalid(form)


@login_required
def quiz_list(request, slug):
    quizzes = Quiz.objects.filter(course__slug = slug).order_by('-id')
    course = Course.objects.get(slug = slug)
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes, 'course': course})
    # return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


@method_decorator([login_required, lecturer_required, student_required], name='dispatch')
class QuizMarkerMixin(object):
    @method_decorator(login_required)
    # @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


# @method_decorator([login_required, lecturer_required], name='get_queryset')
class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


@method_decorator([login_required], name='dispatch')
class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        context['exams_counter'] = progress.show_exams().count()
        return context

from result.models import TakenCourse

@method_decorator([login_required], name='dispatch')
class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = super(QuizMarkingList, self).get_queryset().filter(complete=True)

        # Lecturers can view all completed quizzes like admins
        elif self.request.user.is_lecturer:
            queryset = super(QuizMarkingList, self).get_queryset().filter(complete=True)

        # Students can view all completed quizzes
        elif self.request.user.is_student:
            queryset = super(QuizMarkingList, self).get_queryset().filter(complete=True)

        # Handle users who are neither superusers, lecturers, nor students
        else:
            raise PermissionDenied("You do not have permission to view this page.")

        # Apply user filtering if provided in GET request
        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset

def get_queryset(self):
    print("User: ", self.request.user)  
    print("Calling queryset filter")

@method_decorator([login_required], name='dispatch')
class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] = context['sitting'].get_questions(with_answers=True)
        return context


# @method_decorator([login_required, student_required], name='dispatch')
@method_decorator([login_required], name='dispatch')
class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'
    result_template_name = 'result.html'
    # single_complete_template_name = 'single_complete.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, slug=self.kwargs['slug'])
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        quizQuestions = Question.objects.filter(quiz=self.quiz).count()
        course = get_object_or_404(Course, pk=self.kwargs['pk'])

        if quizQuestions <= 0:
            messages.warning(request, f'Question set of the quiz is empty. try later!')
            return redirect('quiz_index', self.course.slug)

        # if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
        #     raise PermissionDenied

        self.sitting = Sitting.objects.user_sitting(request.user, self.quiz, self.course)


        if self.sitting is False:
            # return render(request, self.single_complete_template_name)
            messages.info(request, f'You have already sat this exam and only one sitting is permitted')
            return redirect('quiz_index', self.course.slug)

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()

        if self.question.__class__ is Essay_Question:
            form_class = EssayForm
        else:
            form_class = self.form_class

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        user_answers = escape(form.cleaned_data.get('user_answers', ''))
        print("User's answers (escaped):", user_answers)


        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            return self.final_result_user()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'])
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {
                'previous_answer': guess,
                'previous_outcome': is_correct,
                'previous_question': self.question,
                'answers': self.question.get_choices(),
                'question_type': {self.question.__class__.__name__: True}
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

        # print("User's answers:", guess)
    def final_result_user(self):
        results = {
            'course': get_object_or_404(Course, pk=self.kwargs['pk']),
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
            'course': get_object_or_404(Course, pk=self.kwargs['pk'])
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] = self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] = self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False or self.request.user.is_superuser or self.request.user.is_lecturer :
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)
    

    

@login_required
@lecturer_required
def export_quiz_data(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="completed_exams.xls"'
    
    # Logic to create the Excel file
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Completed Exams')

    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['User', 'Mobile', 'Email', 'Zone', 'Branch', 'Department', 'Date of Joining', 'Course', 'Program', 'Completed', 'Score']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    sitting_list = Sitting.objects.filter(complete=True)

    for sitting in sitting_list:
        row_num += 1
        user_name = f"{sitting.user.first_name} {sitting.user.last_name}"
        ws.write(row_num, 0, user_name, font_style)
        ws.write(row_num, 1, sitting.user.phone, font_style)
        ws.write(row_num, 2, sitting.user.email, font_style)
        ws.write(row_num, 3, sitting.user.zone, font_style)
        ws.write(row_num, 4, sitting.user.branch, font_style)
        ws.write(row_num, 5, sitting.user.department, font_style)
        
        # Handle case where date_joined might be None
        if sitting.user.date_joined:
            ws.write(row_num, 6, sitting.user.date_joined.strftime('%Y-%m-%d'), font_style)
        else:
            ws.write(row_num, 6, 'N/A', font_style)  # Write 'N/A' or any placeholder

        ws.write(row_num, 7, sitting.quiz.course.title, font_style)
        ws.write(row_num, 8, sitting.quiz.title, font_style)
        
        # Handle case where sitting.end might be None
        if sitting.end:
            ws.write(row_num, 9, sitting.end.strftime('%Y-%m-%d'), font_style)
        else:
            ws.write(row_num, 9, 'N/A', font_style)  # Write 'N/A' or any placeholder

        ws.write(row_num, 10, f'{sitting.get_percent_correct}%', font_style)

    wb.save(response)
    return response







# @login_required
# def certificate_pdf_view(request, id, code, user_id):
#     # Fetch the course based on the provided ID and code
#     course = get_object_or_404(Course, id=id, code=code)

#     # Fetch the user based on user_id
#     user = get_object_or_404(User, id=user_id)

#     # Filter the Sitting model by the course and user
#     sittings = Sitting.objects.filter(quiz__course=course, user=user)

#     # If no results found, return an error
#     if not sittings.exists():
#         messages.error(request, f"No result found for {user.get_full_name()} in this course.")
#         return redirect('quiz_progress')

#     # Take the first sitting
#     result = sittings.first()

#     # Check if the user is eligible for a certificate
#     is_eligible = result.get_percent_correct >= 95 or request.user.is_lecturer or request.user.is_superuser

#     if not is_eligible:
#         messages.error(request, "This user is not eligible for a certificate.")
#         return redirect('quiz_progress')

#     # Define the file path for the certificate PDF
#     filename = f"certificate_{user.username}_{code}.pdf"
#     file_path = os.path.join(settings.MEDIA_ROOT, 'certificates', filename)

#     # Define the background image path
#     background_path = os.path.join(settings.MEDIA_ROOT, 'img.jpg')  # Ensure correct path

#     # Check if the background image exists
#     if not os.path.exists(background_path):
#         messages.error(request, "Background image not found.")
#         return redirect('quiz_progress')

#     # Create a PDF document using ReportLab with landscape A4 size
#     c = canvas.Canvas(file_path, pagesize=landscape(A4))
#     width, height = landscape(A4)

#     # Try to draw the background image
#     try:
#         c.drawImage(background_path, 0, 0, width=width, height=height)
#     except Exception as e:
#         print(f"Error drawing background image: {e}")
#         messages.error(request, "Failed to draw background image.")
#         return redirect('quiz_progress')

#     # Add the recipient's name in bold, centered
#     c.setFont("Helvetica-Bold", 30)
#     recipient_name = f"{user.first_name} {user.last_name}"
#     c.drawCentredString(width / 2.0, height - 3.0 * inch, recipient_name)

#     # Add course completion text
#     c.setFont("Helvetica", 16)
#     c.drawCentredString(width / 2.0, height - 3.5 * inch, "has successfully completed the course")

#     # Add the course name in italic
#     c.setFont("Helvetica-BoldOblique", 20)
#     course_name = result.quiz.course.title
#     c.drawCentredString(width / 2.0, height - 3.8 * inch, f'"{course_name}"')

#     # Add the score percentage
#     score = result.get_percent_correct
#     c.setFont("Helvetica", 14)
#     c.drawCentredString(width / 2.0, height - 4.2 * inch, f"has achieved an outstanding performance of {score}%.")

#     # Add final acknowledgment text
#     c.drawCentredString(width / 2.0, height - 4.8 * inch, "This accomplishment reflects dedication and hard work.")

#     # Add instructor's name and date
#     c.setFont("Helvetica", 14)
#     c.drawString(1 * inch, 2.0 * inch, "Course Instructor: Aludecor")

#     # Check if the result has an end date and display it
#     if result.end:
#         c.drawString(width - 3.3 * inch, 2.0 * inch, f"Date: {result.end.strftime('%B %d, %Y')}")
#     else:
#         c.drawString(width - 3.3 * inch, 2.0 * inch, "Date: Not Available")

#     # Save the PDF file
#     c.showPage()
#     c.save()

#     # Serve the PDF as a downloadable file
#     fs = FileSystemStorage(os.path.join(settings.MEDIA_ROOT, 'certificates'))
#     with fs.open(filename) as pdf:
#         response = HttpResponse(pdf, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename={filename}'
#         return response


from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
import os

@login_required
def certificate_pdf_view(request, id, code, user_id):
    import logging
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.pdfgen import canvas
    import os
    from django.conf import settings

    # Enable detailed logging
    logging.basicConfig(level=logging.DEBUG)

    # Fetch the course and user
    try:
        course = get_object_or_404(Course, id=id, code=code)
        user = get_object_or_404(User, id=user_id)
        logging.debug(f"Fetched course: {course.title}, user: {user.username}")
    except Exception as e:
        logging.error(f"Error fetching course or user: {e}")
        messages.error(request, "Invalid course or user.")
        return redirect('quiz_progress')

    # Filter sittings
    sittings = Sitting.objects.filter(quiz__course=course, user=user)
    if not sittings.exists():
        logging.error(f"No result found for user {user.get_full_name()} in course {course.title}")
        messages.error(request, f"No result found for {user.get_full_name()} in this course.")
        return redirect('quiz_progress')

    result = sittings.first()

    # Achievement condition: 95% or more
    if result.get_percent_correct < 95:
        logging.info(f"User {user.username} did not achieve 95%.")
        messages.error(request, "Certificate can only be issued for scores above 95%.")
        return redirect('quiz_progress')

    # Define certificate templates based on course level
    certificate_template = {
        "basic": os.path.join(settings.MEDIA_ROOT, 'certificate template', 'Basic- Bronze.jpg'),
        "open": os.path.join(settings.MEDIA_ROOT, 'certificate template', 'Basic- Bronze.jpg'),  # Same as basic
        "intermediate": os.path.join(settings.MEDIA_ROOT, 'certificate template', 'intermediate- Silver.jpg'),
        "advance": os.path.join(settings.MEDIA_ROOT, 'certificate template', 'Advanced- Gold.jpg'),
    }

    course_level = course.level.lower()
    background_path = certificate_template.get(course_level)

    # Validate the background image path
    logging.debug(f"Checking template path: {background_path}")
    if not background_path or not os.path.exists(background_path):
        logging.error(f"Template path checked: {background_path}, Exists: {os.path.exists(background_path)}")
        messages.error(request, "Certificate template not found. Please check template paths and permissions.")
        return redirect('quiz_progress')

    # Define the file path for the PDF
    filename = f"certificate_{user.username}_{code}_{course_level}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'certificates', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Generate the PDF
    try:
        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Add the background image
        logging.debug(f"Drawing background image from path: {background_path}")
        c.drawImage(background_path, 0, 0, width=width, height=height)

        # Add recipient's name
        recipient_name = f"{user.first_name} {user.last_name}"
        font_path = os.path.join(settings.MEDIA_ROOT, 'fonts', 'CustomFont.ttf')
        if os.path.exists(font_path):
          pdfmetrics.registerFont(TTFont('CustomFont', font_path))
        else:
          raise FileNotFoundError(f"Custom font not found at {font_path}")
        c.setFont("CustomFont", 40)  # Set the custom font and size
        # c.drawCentredString(width / 2, height - 3.0 * inch, recipient_name)
        achievement_y =  height - 3.5 * inch  # Adjust this value to match the position of "Achievement"
        recipient_name_y = achievement_y - 0.7* inch  # Move recipient name 0.5 inch below "Achievement"

# Draw recipient's name below "Achievement"
        x_offset = 0.7 * inch  # Adjust the offset value for more/less right alignment
        c.drawCentredString((width / 2) + x_offset, recipient_name_y, recipient_name)

#Allign the designation
        c.setFont("Helvetica", 16)
        designation = f"{user.designation} "
        designation_y =  height - 3.9 * inch  
        des_name_y = designation_y - 0.8* inch 

        x_offset = 0.7 * inch  
        c.drawCentredString((width / 2) + x_offset, des_name_y, designation) 

#Allign the location
        c.setFont("Helvetica", 16)
        location = f"{user.zone}, {user.branch}"
        location_y =  height - 4.5 * inch  
        loc_name_y = location_y - 0.8* inch 

        x_offset = 0.7 * inch  
        c.drawCentredString((width / 2) + x_offset, loc_name_y, location) 
       

        # Add course completion text
        c.setFont("Helvetica", 14)
        # c.drawCentredString(width / 2, height - 3.5 * inch, "has successfully completed the course")

        # Add course name
        course_name_upper = course.title.upper()
        certified_text_x = 2.6 * inch 
        certified_text_y = 2.6 * inch
        c.setFont("Helvetica-Bold", 12)
        course_name_x = certified_text_x + 2.4 * inch 
        c.drawString(course_name_x, certified_text_y, f"{course_name_upper}")
        # c.drawCentredString(width / 2, height - 2.7 * inch, f'"{course_name}"')

        # Add score details
        c.setFont("Helvetica", 14)
        score = result.get_percent_correct
        # c.drawCentredString(width / 2, height - 4.2 * inch, f"with an achievement of {score}%.")

        # Add acknowledgment text
        # c.drawCentredString(width / 2, height - 4.8 * inch, f"This certificate is awarded at the {course_level.capitalize()} level.")

        # Add instructor and date
        c.setFont("Helvetica", 14)
        # c.drawString(1 * inch, 2.0 * inch, "Course Instructor: Aludecor")
        if result.end:
            c.drawString(width - 2.5 * inch, 2.6 * inch, f"{result.end.strftime('%d/%m/%Y')}")
        else:
            c.drawString(width - 1.0 * inch, 2.6 * inch, "Date: Not Available")

        c.showPage()
        c.save()

        logging.debug(f"PDF saved at: {file_path}")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        messages.error(request, "Error creating the certificate. Please try again.")
        return redirect('quiz_progress')

    # Serve the PDF for download
    try:
        with open(file_path, 'rb') as pdf_file:
            logging.debug(f"Serving PDF: {file_path}")
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except Exception as e:
        logging.error(f"Error serving PDF: {e}")
        messages.error(request, "Error downloading certificate. Please try again.")
        return redirect('quiz_progress')















def quiz_result_view(request, quiz_sitting_id):
    with connection.cursor() as cursor:
        # Execute the raw SQL query to fetch the quiz results with answer choices
        cursor.execute("""
            SELECT 
                qs.id AS quiz_sitting_id,
                q.id AS question_id,
                q.content AS question_content,
                qc.choice AS user_answer, -- Fetch the user answer choice text
                (SELECT choice 
                 FROM elearn.quiz_choice 
                 WHERE question_id = q.id 
                 AND correct = 1 
                 LIMIT 1) AS correct_answer, -- Fetch the correct answer choice text
                u.id AS user_id,
                u.username AS username,
                CONCAT(u.first_name, ' ', u.last_name) AS full_name 
            FROM 
                elearn.quiz_sitting qs
            JOIN 
                elearn.quiz_question q ON FIND_IN_SET(q.id, qs.incorrect_questions)
            JOIN 
                elearn.quiz_choice qc ON qc.id = JSON_UNQUOTE(JSON_EXTRACT(qs.user_answers, CONCAT('$.', q.id))) -- Extract user's choice from the JSON
            JOIN 
                elearn.accounts_user u ON qs.user_id = u.id 
            WHERE 
                qs.complete = 1
            AND qs.id = %s
        """, [quiz_sitting_id])  # Pass the quiz_sitting_id as a parameter

        # Fetch all results
        results = cursor.fetchall()

    # Pass the results and quiz_sitting_id to the template
    context = {
        'results': results,
        'quiz_sitting_id': quiz_sitting_id,  # Make sure quiz_sitting_id is passed to the context
    }

    return render(request, 'quiz/sitting_detail.html', context)




    

@method_decorator(login_required, name='dispatch')
class UserProgressView(TemplateView):
    template_name = 'team_quiz_progress.html'  # You can name your template

    def get(self, request):
        hod_username = request.user.username  # e.g., 'KKOL1623'

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    u.username AS Username,
                    q.title AS Quiz_Title,
                    s.current_score AS Current_Score,
                    q.pass_mark AS Possible_Score,
                    ROUND((s.current_score / q.pass_mark) * 100, 0) AS Out_of_100,
                    SEC_TO_TIME(TIMESTAMPDIFF(SECOND, s.start, s.end)) AS Time_Taken
                FROM 
                    elearn.quiz_sitting s
                JOIN 
                    elearn.accounts_user u ON s.user_id = u.id
                JOIN 
                    elearn.quiz_quiz q ON s.quiz_id = q.id
                WHERE 
                    s.complete = 1
                    AND u.reporting_to = %s
            """, [hod_username])

            columns = [col[0] for col in cursor.description]
            team_progress = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(request, self.template_name, {
            'team_progress': team_progress,
            'title': 'Team Quiz Progress'
        })





    

  









    

    
