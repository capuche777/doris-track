"""URL configuration for quiz app."""
from django.urls import path
from . import views

app_name = "quiz"
urlpatterns = [
    path("", views.quiz_list_view, name="quiz_list"),
    path("take/", views.quiz_take_view, name="quiz_take"),
    path("take/<int:quiz_id>/", views.quiz_take_view, name="quiz_take_id"),
    path("submit/<int:question_id>/", views.quiz_submit_view, name="quiz_submit"),
    path("results/<int:quiz_id>/", views.quiz_results_view, name="quiz_results"),
]