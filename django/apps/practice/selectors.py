"""Selectors for practice app."""
from .models import PracticeSession


def get_sessions_by_type(student, practice_type):
    return PracticeSession.objects.filter(student=student, practice_type=practice_type)


def get_total_practice_minutes(student, days=30):
    from datetime import date, timedelta
    start = date.today() - timedelta(days=days)
    return sum(
        s.duration_minutes
        for s in PracticeSession.objects.filter(student=student, date__gte=start)
    )
