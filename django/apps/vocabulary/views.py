"""Views for vocabulary app."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.profiles.models import Student
from .models import Word
from .selectors import get_difficult_words_detailed, get_word_failure_rate
from .services import update_word_after_review


def difficult_words_view(request):
    """Show top 10 most-missed words for the student. DT-11."""
    student = Student.objects.first()
    if not student:
        return render(request, "vocabulary/difficult_words.html", {
            "student": None,
            "difficult_words": [],
        })

    difficult_words = get_difficult_words_detailed(student, limit=10)

    return render(request, "vocabulary/difficult_words.html", {
        "student": student,
        "difficult_words": difficult_words,
    })


def word_detail_view(request, word_id):
    """Show detail for a single word. DT-11."""
    word = get_object_or_404(Word, id=word_id)
    failure_rate = get_word_failure_rate(word_id)

    return render(request, "vocabulary/word_detail.html", {
        "word": word,
        "failure_rate": failure_rate,
    })


def review_single_word_view(request, word_id):
    """Quick review for a single word. DT-11."""
    word = get_object_or_404(Word, id=word_id)

    if request.method == "POST":
        student_answer = request.POST.get("answer", "").strip()
        correct_answer = word.word.strip()

        # Case-insensitive comparison
        is_correct = student_answer.lower() == correct_answer.lower()

        if is_correct:
            messages.success(request, "Correct!")
        else:
            messages.error(request, f"Wrong! The correct answer is: {correct_answer}")

        # Update word stats
        quality = 5 if is_correct else 1
        update_word_after_review(word, quality)

        return redirect("vocabulary:difficult_words")

    return render(request, "vocabulary/review_single.html", {
        "word": word,
    })