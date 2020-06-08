from django.urls import path

from .views import * 

app_name = 'course'
urlpatterns = [
        path('', course, name='course'),
        path('instructor/quiz/', InstructorQuizListView.as_view(), name='quiz_change_list'),
        path('instructor/quiz/add/', QuizCreateView.as_view(), name='quiz_add'),
        path('instructor/quiz/<int:pk>/', QuizUpdateView.as_view(), name='quiz_change'),
        path('instructor/quiz/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz_delete'),
        path('instructor/quiz/<int:pk>/results/', QuizResultsView.as_view(), name='quiz_results'),
        path('instructor/quiz/<int:pk>/question/add/', question_add, name='question_add'),
        path('instructor/quiz/<int:quiz_pk>/question/<int:question_pk>/', question_change, name='question_change'),
        path('instructor/quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', QuestionDeleteView.as_view(), name='question_delete'),
        path('student/quiz/', StudentQuizListView.as_view(), name='quiz_list'),
        path('student/taken/', TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('student/quiz/<int:pk>/', take_quiz, name='take_quiz'),
    
]