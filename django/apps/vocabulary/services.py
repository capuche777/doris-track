"""Service layer for vocabulary app - SM-2 spaced repetition algorithm."""
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from .models import Word


def calculate_sm2(ease_factor: float, interval: int, quality: int) -> tuple:
    """
    SM-2 algorithm.
    quality: 0-5 (0=complete blackout, 5=perfect response)
    Returns: (new_ease_factor, new_interval)
    """
    if quality < 3:
        # Failed - reset
        return max(1.3, ease_factor - 0.2), 1

    # Passed
    if interval == 1:
        new_interval = 1
    elif interval == 2:
        new_interval = 6
    else:
        new_interval = round(interval * ease_factor)

    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, new_ease)

    return new_ease, new_interval


def check_review_answer(word_id: int, student_answer: str) -> dict:
    """
    Validate a student's answer to a vocabulary review question.
    DT-06: increments times_wrong counter when student answers incorrectly.
    
    Returns: {
        "correct": bool,
        "correct_answer": str,
        "next_review": date,
    }
    """
    word = get_object_or_404(Word, id=word_id)
    correct_answer = word.word.strip()
    student_answer = student_answer.strip()
    
    # Case-insensitive, stripped comparison
    is_correct = student_answer.lower() == correct_answer.lower()
    quality = 5 if is_correct else 1
    
    # Update word after review
    update_word_after_review(word, quality)
    
    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "next_review": word.next_review_date,
    }


def update_word_after_review(word, quality: int) -> None:
    """Update word fields after a review. DT-06: increments times_wrong on wrong answers."""
    word.review_count += 1

    if quality < 3:
        # Wrong answer — increment times_wrong per DT-06 spec
        word.times_wrong = (word.times_wrong or 0) + 1

    word.ease_factor, word.current_interval_days = calculate_sm2(
        word.ease_factor or 2.5, word.current_interval_days or 1, quality
    )
    word.next_review_date = date.today() + timedelta(days=word.current_interval_days)

    if quality >= 4:
        if word.review_count >= 5:
            word.mastery = "mastered"
        else:
            word.mastery = "learning"

    word.save()
