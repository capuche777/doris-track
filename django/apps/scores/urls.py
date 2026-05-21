"""URL configuration for scores app."""
from django.urls import path
from . import views

app_name = "scores"

urlpatterns = [
    path("", views.score_list_view, name="score_list"),
    path("entry/", views.score_entry_view, name="score_entry"),
    path("charts/", views.score_charts_view, name="score_charts"),
]