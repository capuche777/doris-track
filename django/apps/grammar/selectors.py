"""Selectors for grammar app."""
from .models import Correction


def get_corrections_by_category(student, category):
    return Correction.objects.filter(student=student, category=category)


def get_recent_corrections(student, limit=20):
    return Correction.objects.filter(student=student)[:limit]
