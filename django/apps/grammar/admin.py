"""Admin for grammar app."""
from django.contrib import admin
from .models import Correction


@admin.register(Correction)
class CorrectionAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "category", "date", "created_at"]
    list_filter = ["category", "student", "date"]
