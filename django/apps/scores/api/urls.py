"""API URL configuration for the scores app."""
from django.urls import path

from .views import (
    AssessmentCreateView,
    DecliningScoresView,
    LatestScoresView,
    ScoreHistoryView,
)

app_name = "scores_api"

urlpatterns = [
    path(
        "students/<int:student_id>/assessments/",
        AssessmentCreateView.as_view(),
        name="assessment_create",
    ),
    path(
        "students/<int:student_id>/scores/",
        ScoreHistoryView.as_view(),
        name="score_history",
    ),
    path(
        "students/<int:student_id>/scores/latest/",
        LatestScoresView.as_view(),
        name="scores_latest",
    ),
    path(
        "students/<int:student_id>/scores/declining/",
        DecliningScoresView.as_view(),
        name="scores_declining",
    ),
]
