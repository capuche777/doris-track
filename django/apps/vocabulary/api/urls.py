"""API URL configuration for the vocabulary app."""
from django.urls import path

from .views import (
    AddWordView,
    DifficultWordsView,
    WordReviewView,
    WordsByMasteryView,
    WordsDueView,
    WordUpdateView,
)

app_name = "vocabulary_api"

urlpatterns = [
    path(
        "students/<int:student_id>/words/",
        AddWordView.as_view(),
        name="word_add",
    ),
    path(
        "students/<int:student_id>/words/due/",
        WordsDueView.as_view(),
        name="words_due",
    ),
    path(
        "students/<int:student_id>/words/difficult/",
        DifficultWordsView.as_view(),
        name="words_difficult",
    ),
    path(
        "students/<int:student_id>/words/by-mastery/<str:mastery>/",
        WordsByMasteryView.as_view(),
        name="words_by_mastery",
    ),
    path(
        "words/<int:word_id>/review/",
        WordReviewView.as_view(),
        name="word_review",
    ),
    path(
        "words/<int:word_id>/",
        WordUpdateView.as_view(),
        name="word_detail",
    ),
]
