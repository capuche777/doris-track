"""API URL configuration for the profiles app."""
from django.urls import path

from .views import StudentByEmailView

app_name = "profiles_api"

urlpatterns = [
    path("students/by-email/", StudentByEmailView.as_view(), name="student_by_email"),
]
