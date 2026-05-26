"""Selectors for grammar app."""
from datetime import date
from django.db.models import Count


def get_corrections(student, category=None, date_from=None, date_to=None):
    """
    Get corrections for a student with optional filters.
    """
    from .models import Correction
    qs = Correction.objects.filter(student=student)
    if category:
        qs = qs.filter(category=category)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs.order_by("-date")


def get_categories(student_id):
    """
    Get distinct categories with correction counts for a student.
    Returns list of dicts: {category, label, count}
    """
    from .models import Correction
    from .models import Correction  # noqa: reimport for clarity

    categories = (
        Correction.objects
        .filter(student_id=student_id)
        .values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Map category key to human-readable label
    label_map = dict(Correction.CATEGORY_CHOICES)

    return [
        {"category": c["category"], "label": label_map.get(c["category"], c["category"]), "count": c["count"]}
        for c in categories
    ]