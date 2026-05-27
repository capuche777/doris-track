"""API URL configuration for the grammar app."""
from django.urls import path

from .views import (
    CorrectionAnalyticsView,
    CorrectionListCreateView,
    CorrectionTrendView,
)

app_name = "grammar_api"

urlpatterns = [
    path(
        "students/<int:student_id>/corrections/",
        CorrectionListCreateView.as_view(),
        name="correction_list_create",
    ),
    path(
        "students/<int:student_id>/corrections/analytics/",
        CorrectionAnalyticsView.as_view(),
        name="correction_analytics",
    ),
    path(
        "students/<int:student_id>/corrections/trend/<str:category>/",
        CorrectionTrendView.as_view(),
        name="correction_trend",
    ),
]
