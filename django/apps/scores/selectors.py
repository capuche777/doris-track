"""Selector layer for scores app."""
from django.db.models import Avg

from .models import Assessment, Score


def get_assessments(student_id: int, limit: int = None):
    """Return all assessments for a student, newest first."""
    qs = Assessment.objects.filter(student_id=student_id).order_by("-date")
    if limit:
        qs = qs[:limit]
    return qs


def get_score_history(student_id: int, skill: str = None):
    """
    Return all scores for a student.
    If skill is specified, filter to that skill only.
    """
    qs = Score.objects.filter(assessment__student_id=student_id)
    if skill:
        qs = qs.filter(skill=skill)
    return qs.select_related("assessment").order_by("assessment__date")


def get_latest_scores(student_id: int) -> dict:
    """
    Return the most recent score value per skill for a student.
    Returns {"pronunciation": 85, "fluency": 78, ...}
    """
    latest_per_skill = {}
    for skill, _ in Score.SKILL_CHOICES:
        score = (
            Score.objects
            .filter(assessment__student_id=student_id, skill=skill)
            .order_by("-assessment__date")
            .first()
        )
        if score:
            latest_per_skill[skill] = score.value
    return latest_per_skill