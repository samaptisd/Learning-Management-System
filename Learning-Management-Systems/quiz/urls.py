from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [

    path('<slug>/quizzes/', quiz_list, name='quiz_index'),

    path('progress/', view=QuizUserProgressView.as_view(), name='quiz_progress'),

    # path('marking/<int:pk>/', view=QuizMarkingList.as_view(), name='quiz_marking'),
    path('marking_list/', view=QuizMarkingList.as_view(), name='quiz_marking'),
    # path('marking/<int:pk>/', view=QuizMarkingDetail.as_view(), name='quiz_marking_detail'),

    # path('marking_list/', QuizMarkingList.as_view(), name='quiz_marking_list'),

    path('export_quiz_data/', views.export_quiz_data, name='export_quiz_data'),

    path('marking/<int:pk>/', view=QuizMarkingDetail.as_view(), name='quiz_marking_detail'),

    path('<int:pk>/<slug>/take/', view=QuizTake.as_view(), name='quiz_take'),

    path('<slug>/quiz_add/', QuizCreateView.as_view(), name='quiz_create'),
    path('<slug>/<int:pk>/add/', QuizUpdateView.as_view(), name='quiz_update'),
    path('<slug>/<int:pk>/delete/', quiz_delete, name='quiz_delete'),
    path('mc-question/add/<slug>/<int:quiz_id>/', MCQuestionCreate.as_view(), name='mc_create'),
    # path('mc-question/add/<int:pk>/<quiz_pk>/', MCQuestionCreate.as_view(), name='mc_create'),
    path('quiz/progress/certificates/<int:id>/<str:code>/', certificate_pdf_view, name='certificate_pdf_view'),
    path('quiz/marking/<int:quiz_sitting_id>/', quiz_result_view, name='quiz_marking'),
    path('quiz/progress/certificates/<int:id>/<str:code>/<int:user_id>/', views.certificate_pdf_view, name='certificate_pdf_view'),
    path('userprogress/', UserProgressView.as_view(), name='course_progress'),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
