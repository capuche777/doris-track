"""Service layer for scores app."""
from datetime import date, timedelta

from django.db import models

from .models import Assessment, Score


def record_assessment(student_id: int, scores_dict: dict, assessment_date: date, notes: str = "") -> Assessment:
    """
    Create a new assessment with scores for a student.

    scores_dict: {"pronunciation": 85, "fluency": 78, ...}
    """
    assessment = Assessment.objects.create(
        student_id=student_id,
        date=assessment_date,
        notes=notes,
    )

    for skill, value in scores_dict.items():
        if skill not in dict(Score.SKILL_CHOICES):
            continue
        Score.objects.create(
            assessment=assessment,
            skill=skill,
            value=max(0, min(100, int(value))),
        )

    return assessment


def detect_declining_skills(student_id: int) -> dict:
    """
    Return skills that declined 3+ points in the last 7 days vs the previous 7 days.
    Returns {"skill": {"current": 80, "previous": 85, "change": -5}, ...}
    """
    today = date.today()
    recent_start = today - timedelta(days=6)
    previous_start = today - timedelta(days=13)
    previous_end = today - timedelta(days=7)

    declines = {}

    for skill, _ in Score.SKILL_CHOICES:
        recent = Score.objects.filter(
            assessment__student_id=student_id,
            skill=skill,
            assessment__date__range=(recent_start, today),
        ).aggregate(avg=models.Avg("value"))["avg"]

        previous = Score.objects.filter(
            assessment__student_id=student_id,
            skill=skill,
            assessment__date__range=(previous_start, previous_end),
        ).aggregate(avg=models.Avg("value"))["avg"]

        if recent is not None and previous is not None:
            change = recent - previous
            if change <= -3:
                declines[skill] = {"current": round(recent, 1), "previous": round(previous, 1), "change": round(change, 1)}

    return declines
