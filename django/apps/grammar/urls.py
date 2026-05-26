"""URL configuration for grammar app."""
from django.urls import path
from . import views

app_name = "grammar"

urlpatterns = [
    path("", views.correction_list_view, name="correction_list"),
    path("add/", views.correction_add_view, name="correction_add"),
    path("analytics/", views.correction_analytics_view, name="correction_analytics"),
]