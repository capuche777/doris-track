"""URL configuration for vocabulary app."""
from django.urls import path
from . import views

app_name = "vocabulary"

urlpatterns = [
    path("review/", views.review_session_view, name="review_session"),
    path("review/complete/", views.review_complete_view, name="review_complete"),
    path("difficult/", views.difficult_words_view, name="difficult_words"),
    path("word/<int:word_id>/", views.word_detail_view, name="word_detail"),
    path("word/<int:word_id>/review/", views.review_single_word_view, name="review_single"),
]