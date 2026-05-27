"""API URL configuration for the vocabulary app."""
from django.urls import path

from .views import WordReviewView, WordsDueView

app_name = "vocabulary_api"

urlpatterns = [
    path(
        "students/<int:student_id>/words/due/",
        WordsDueView.as_view(),
        name="words_due",
    ),
    path(
        "words/<int:word_id>/review/",
        WordReviewView.as_view(),
        name="word_review",
    ),
]
