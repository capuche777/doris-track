"""Admin for vocabulary app."""
from django.contrib import admin
from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["word", "student", "difficulty", "mastery", "review_count", "next_review_date"]
    list_filter = ["difficulty", "mastery", "student"]
    search_fields = ["word", "definition"]
