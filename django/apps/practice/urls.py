"""URL configuration for practice app — DT-08."""
from django.urls import path
from . import views

app_name = "practice"

urlpatterns = [
    path("", views.practice_list_view, name="list"),
    path("add/", views.practice_add_view, name="add"),
    path("heatmap/", views.practice_heatmap_view, name="heatmap"),
]
