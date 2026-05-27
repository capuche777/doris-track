from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from apps.profiles import views

app_name = "profiles"

urlpatterns = [
    path("profile/", views.student_profile_view, name="student_profile"),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    # Django 5.x requires logout via POST; redirect handled by LOGOUT_REDIRECT_URL.
    path("logout/", LogoutView.as_view(), name="logout"),
]