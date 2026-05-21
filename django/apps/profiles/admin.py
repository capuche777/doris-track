"""Admin configuration for profiles app."""
from django.contrib import admin
from .models import Student, Tutor


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "created_at"]
    search_fields = ["name", "email"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "current_level", "target_level", "tutor", "created_at"]
    list_filter = ["current_level", "target_level", "tutor"]
    search_fields = ["name", "email"]
