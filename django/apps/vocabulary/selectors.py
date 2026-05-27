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


def get_difficult_words(student, threshold: int = 3):
    """Get words student keeps getting wrong (times_wrong >= threshold). DT-06."""
    return Word.objects.filter(student=student, times_wrong__gte=threshold)


def get_difficult_words_detailed(student, limit: int = 10, threshold: int = 1):
    """
    Get top most-missed words for a student (DT-11).
    Returns words sorted by times_wrong descending, excluding mastered.
    Each word annotated with failure_rate percentage.

    `threshold` is the minimum `times_wrong` to qualify (default 1, i.e. any
    word missed at least once).
    """
    words = Word.objects.filter(
        student=student,
        times_wrong__gte=threshold,
    ).exclude(mastery="mastered").order_by("-times_wrong")[:limit]

    result = []
    for word in words:
        total = word.review_count + word.times_wrong
        failure_rate = round((word.times_wrong / total * 100) if total > 0 else 0)
        result.append({
            "word": word,
            "times_wrong": word.times_wrong,
            "review_count": word.review_count,
            "failure_rate": failure_rate,
        })
    return result


def get_word_failure_rate(word_id: int) -> int:
    """
    Calculate failure rate for a word: times_wrong / (review_count + times_wrong) as percentage.
    DT-11.
    """
    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist:
        return 0
    total = word.review_count + word.times_wrong
    if total == 0:
        return 0
    return round((word.times_wrong / total) * 100)