"""API URL configuration for the dashboard app."""
from django.urls import path

from .views import DashboardView

app_name = "dashboard_api"

urlpatterns = [
    path(
        "students/<int:student_id>/dashboard/",
        DashboardView.as_view(),
        name="dashboard",
    ),
]
