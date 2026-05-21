from django.urls import path
from apps.profiles import views

app_name = "profiles"

urlpatterns = [
    path("profile/", views.student_profile_view, name="student_profile"),
]