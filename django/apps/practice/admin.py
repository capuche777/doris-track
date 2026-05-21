"""Admin for practice app."""
from django.contrib import admin
from .models import PracticeSession


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "practice_type", "date", "duration_minutes"]
    list_filter = ["practice_type", "student", "date"]
