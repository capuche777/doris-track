"""Selectors for vocabulary app."""
from datetime import date
from .models import Word


def get_words_for_review(student):
    """Get words due for review today or earlier."""
    return Word.objects.filter(
        student=student,
        next_review_date__lte=date.today(),
    ).exclude(mastery="mastered")


def get_words_by_mastery(student, mastery):
    return Word.objects.filter(student=student, mastery=mastery)


def get_due_words_count(student):
    return get_words_for_review(student).count()
