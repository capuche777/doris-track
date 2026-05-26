"""Service layer for vocabulary app — DT-05 simplified spaced repetition.
Binary system: correct → advance to next interval, wrong → reset to 1 day.
Intervals: [1, 2, 4, 7, 15, 30] days.
"""
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from .models import Word


# Fixed intervals as per spec
INTERVALS = [1, 2, 4, 7, 15, 30]

# Index constants
FIRST_INTERVAL_IDX = 0   # 1 day
LAST_INTERVAL_IDX = len(INTERVALS) - 1  # 30 days


def calculate_next_interval(current_interval_idx: int, correct: bool) -> int:
    """
    Binary spaced repetition — DT-05 spec.
    - correct: advance to next interval (max = 30 days)
    - wrong: reset to 1 day
    Returns: interval in days
    """
    if correct:
        next_idx = current_interval_idx + 1
        if next_idx > LAST_INTERVAL_IDX:
            next_idx = LAST_INTERVAL_IDX
    else:
        next_idx = FIRST_INTERVAL_IDX

    return INTERVALS[next_idx]


def check_review_answer(word_id: int, student_answer: str) -> dict:
    """
    Validate a student's answer to a vocabulary review question.
    Returns: {"correct": bool, "correct_answer": str, "next_review": date}
    """
    word = get_object_or_404(Word, id=word_id)
    correct_answer = word.word.strip()
    student_answer = student_answer.strip()

    is_correct = student_answer.lower() == correct_answer.lower()

    update_word_after_review(word, is_correct)

    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "next_review": word.next_review_date,
    }


def update_word_after_review(word, correct: bool) -> None:
    """
    Update word fields after a review — DT-05 binary system.
    - correct: advance interval
    - wrong: reset to 1 day
    Mastery transitions: new→learning when review_count >= 2,
    learning→mastered when current_interval_idx >= 4 (15 days).
    """
    word.review_count += 1

    # Find current interval index
    try:
        current_interval_idx = INTERVALS.index(word.current_interval_days)
    except ValueError:
        current_interval_idx = FIRST_INTERVAL_IDX

    next_interval_days = calculate_next_interval(current_interval_idx, correct)
    word.current_interval_days = next_interval_days
    word.next_review_date = date.today() + timedelta(days=next_interval_days)

    # Update mastery based on progress
    if correct:
        if word.mastery == "new" and word.review_count >= 2:
            word.mastery = "learning"
        elif word.mastery == "learning" and current_interval_idx >= 4:
            word.mastery = "mastered"

    if not correct:
        # Wrong answer — stay at "learning" (not mastered) or reset if was "mastered"
        if word.mastery == "mastered":
            word.mastery = "learning"
        word.times_wrong += 1

    word.save()
