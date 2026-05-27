"""API URL configuration for the quiz app."""
from django.urls import path

from .views import QuizAnswerView, QuizGenerateView, QuizListView, QuizResultsView

app_name = "quiz_api"

urlpatterns = [
    path(
        "students/<int:student_id>/quiz/generate/",
        QuizGenerateView.as_view(),
        name="quiz_generate",
    ),
    path(
        "students/<int:student_id>/quizzes/",
        QuizListView.as_view(),
        name="quiz_list",
    ),
    path(
        "questions/<int:question_id>/answer/",
        QuizAnswerView.as_view(),
        name="quiz_answer",
    ),
    path(
        "quizzes/<int:quiz_id>/results/",
        QuizResultsView.as_view(),
        name="quiz_results",
    ),
]
