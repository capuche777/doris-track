"""Selectors for practice app — DT-08."""
from datetime import date, timedelta
from collections import defaultdict
from .models import PracticeSession


def get_sessions(student, date_from=None, date_to=None, practice_type=None):
    """
    Get practice sessions for a student with optional filters. DT-08.
    Returns QuerySet ordered by date descending.
    """
    qs = PracticeSession.objects.filter(student=student)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if practice_type:
        qs = qs.filter(practice_type=practice_type)
    return qs.order_by("-date")


def get_heatmap_data(student, year=None):
    """
    Get heatmap data for a student: {date: minutes} for every day of the year.
    DT-08.
    Returns a dict mapping date strings (YYYY-MM-DD) to total minutes practiced.
    """
    if year is None:
        year = date.today().year

    start = date(year, 1, 1)
    end = date(year, 12, 31)

    sessions = PracticeSession.objects.filter(
        student=student,
        date__gte=start,
        date__lte=end,
    )

    # Aggregate minutes per day
    data = defaultdict(int)
    for s in sessions:
        data[s.date.isoformat()] += s.duration_minutes

    return dict(data)


def get_sessions_by_type(student, practice_type):
    return PracticeSession.objects.filter(student=student, practice_type=practice_type)


def get_total_practice_minutes(student, days=30):
    start = date.today() - timedelta(days=days)
    return sum(
        s.duration_minutes
        for s in PracticeSession.objects.filter(student=student, date__gte=start)
    )
