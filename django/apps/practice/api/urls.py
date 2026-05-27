"""API URL configuration for the practice app."""
from django.urls import path

from .views import PracticeListCreateView, PracticeStatsView, PracticeStreakView

app_name = "practice_api"

urlpatterns = [
    path(
        "students/<int:student_id>/practice/",
        PracticeListCreateView.as_view(),
        name="practice_list_create",
    ),
    path(
        "students/<int:student_id>/practice/streak/",
        PracticeStreakView.as_view(),
        name="practice_streak",
    ),
    path(
        "students/<int:student_id>/practice/stats/",
        PracticeStatsView.as_view(),
        name="practice_stats",
    ),
]
