"""Service layer for grammar app."""
from datetime import date, timedelta
from collections import defaultdict
from django.db.models import Count


def log_correction(student, mistake, correct, rule="", category="other"):
    """Log a grammar correction entry."""
    from .models import Correction
    return Correction.objects.create(
        student=student,
        date=date.today(),
        student_mistake=mistake,
        correct_version=correct,
        grammar_rule=rule,
        category=category,
    )


def get_common_mistakes(student, period_days=30):
    """
    Return categories ranked by frequency of mistakes.
    Returns list of dicts: {category, count, percentage, example}
    """
    from datetime import timedelta
    from .models import Correction

    cutoff = date.today() - timedelta(days=period_days)
    corrections = Correction.objects.filter(
        student=student, date__gte=cutoff
    ).values("category").annotate(count=Count("id"))

    total = sum(c["count"] for c in corrections)
    if total == 0:
        return []

    # Get one example per category
    examples = {}
    for corr in Correction.objects.filter(student=student, date__gte=cutoff).order_by("category", "-date"):
        if corr.category not in examples:
            examples[corr.category] = corr.student_mistake

    result = []
    for item in sorted(corrections, key=lambda x: -x["count"]):
        result.append({
            "category": item["category"],
            "count": item["count"],
            "percentage": round(100 * item["count"] / total, 1),
            "example": examples.get(item["category"], ""),
        })
    return result


def get_mistake_trend(student, category, weeks=8):
    """
    Return frequency of mistakes per week for a given category.
    Returns list of dicts: {week_start, count}
    """
    from datetime import timedelta
    from django.db.models.functions import TruncWeek
    from .models import Correction

    cutoff = date.today() - timedelta(weeks=weeks)
    corrections = (
        Correction.objects
        .filter(student=student, category=category, date__gte=cutoff)
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )
    return [
        {"week_start": str(c["week"].strftime("%Y-%m-%d")), "count": c["count"]}
        for c in corrections
    ]