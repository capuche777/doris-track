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


def normalize_answer(text: str) -> str:
    """Normalize an answer for comparison: trim whitespace, lowercase."""
    return text.strip().lower()


def check_review_answer(word_id: int, student_answer: str) -> dict:
    """
    Validate a student's answer to a vocabulary review question.

    The answer matches if it equals the main ``word`` or any entry in the
    word's ``accepted_answers`` (all compared via :func:`normalize_answer`).
    Returns: {"correct": bool, "correct_answer": str, "next_review": date}
    """
    word = get_object_or_404(Word, id=word_id)
    correct_answer = word.word.strip()
    normalized_answer = normalize_answer(student_answer)

    is_correct = normalized_answer == normalize_answer(word.word)
    if not is_correct and word.accepted_answers:
        is_correct = any(
            normalized_answer == normalize_answer(alt)
            for alt in word.accepted_answers
        )

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


def word_exists(student, word: str) -> bool:
    """Return whether the student already has a word with this spelling."""
    return Word.objects.filter(student=student, word=word).exists()


def create_word(
    student,
    word: str,
    definition: str,
    difficulty: str = "B2",
    example_sentence: str = "",
    collocations: str = "",
    accepted_answers: list | None = None,
) -> Word:
    """
    Create a new vocabulary word for a student. DT-05.

    New words start in the "new" mastery state with `next_review_date`
    defaulting to today (set by the model), so they surface in the next
    review session.
    """
    return Word.objects.create(
        student=student,
        word=word,
        definition=definition,
        difficulty=difficulty,
        example_sentence=example_sentence,
        collocations=collocations,
        accepted_answers=accepted_answers or [],
    )


# Word fields a teacher may edit after creation.
EDITABLE_WORD_FIELDS = {
    "word",
    "definition",
    "difficulty",
    "example_sentence",
    "collocations",
    "accepted_answers",
}


def update_word(word_id: int, **fields) -> Word:
    """
    Partially update an existing word's editable content fields.

    Only keys in :data:`EDITABLE_WORD_FIELDS` are applied; unknown keys are
    ignored. Spaced-repetition state (mastery, intervals, counters) is never
    touched here.
    """
    word = get_object_or_404(Word, id=word_id)
    for key, value in fields.items():
        if key in EDITABLE_WORD_FIELDS:
            setattr(word, key, value)
    word.save()
    return word
