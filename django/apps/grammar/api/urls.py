"""API URL configuration for the grammar app."""
from django.urls import path

from .views import CorrectionCreateView

app_name = "grammar_api"

urlpatterns = [
    path(
        "students/<int:student_id>/corrections/",
        CorrectionCreateView.as_view(),
        name="correction_create",
    ),
]
