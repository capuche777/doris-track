"""Admin for quiz app."""
from django.contrib import admin
from .models import Quiz, QuizQuestion


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "week_start_date", "created_at"]
    list_filter = ["student", "week_start_date"]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ["id", "quiz", "question_type", "is_correct", "created_at"]
    list_filter = ["question_type", "is_correct"]
