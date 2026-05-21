"""Admin for scores app."""
from django.contrib import admin
from .models import Assessment, Score


class ScoreInline(admin.TabularInline):
    model = Score
    extra = 5
    min_num = 5


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ["student", "date", "created_at"]
    list_filter = ["date", "student"]
    search_fields = ["student__name"]
    inlines = [ScoreInline]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["assessment", "skill", "value"]
    list_filter = ["skill"]