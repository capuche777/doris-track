"""Views for vocabulary app."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from apps.profiles.models import Student
from .models import Word
from .selectors import get_difficult_words_detailed, get_word_failure_rate, get_words_for_review
from .services import update_word_after_review, check_review_answer


def review_session_view(request):
    """
    Flashcard-style vocabulary review session.
    Shows definition as prompt; student types the word.
    DT-06.
    """
    student = Student.objects.first()
    if not student:
        return render(request, "vocabulary/review_session.html", {
            "words": [],
            "session_stats": {"total": 0, "correct": 0, "wrong": 0},
            "student": None,
        })

    # Initialize or resume session
    session_key = "review_word_ids"
    if session_key not in request.session:
        words_due = list(get_words_for_review(student))
        request.session[session_key] = [w.id for w in words_due]
        request.session["review_stats"] = {"correct": 0, "wrong": 0}
        request.session.modified = True

    word_ids = request.session.get(session_key, [])
    stats = request.session.get("review_stats", {"correct": 0, "wrong": 0})

    # POST: process answer and advance
    if request.method == "POST":
        word_id = request.POST.get("word_id")
        student_answer = request.POST.get("answer", "").strip()
        if word_id and student_answer:
            result = check_review_answer(int(word_id), student_answer)
            if result["correct"]:
                stats["correct"] += 1
            else:
                stats["wrong"] += 1
            request.session["review_stats"] = stats
            request.session.modified = True

        # Advance to next word
        current_idx = int(request.POST.get("current_index", 0))
        next_idx = current_idx + 1
        remaining = len(word_ids)

        if next_idx >= remaining:
            return redirect("vocabulary:review_complete")
        return redirect(f"{request.path}?index={next_idx}")

    # GET: show word at index
    current_index = int(request.GET.get("index", 0))
    remaining_ids = word_ids[current_index:]
    words = list(Word.objects.filter(id__in=remaining_ids).exclude(mastery="mastered"))

    # If no words left, go to complete
    if not words:
        return redirect("vocabulary:review_complete")

    current_word = words[0]  # first remaining word
    total = stats["correct"] + stats["wrong"]

    return render(request, "vocabulary/review_session.html", {
        "current_word": current_word,
        "current_index": current_index,
        "total": total,
        "correct": stats["correct"],
        "wrong": stats["wrong"],
        "student": student,
    })


def review_complete_view(request):
    """Session summary shown after completing all words. DT-06."""
    session_key = "review_word_ids"
    stats = request.session.get("review_stats", {"correct": 0, "wrong": 0})
    total = stats["correct"] + stats["wrong"]

    # Clear session
    for key in [session_key, "review_stats"]:
        if key in request.session:
            del request.session[key]
    request.session.modified = True

    return render(request, "vocabulary/review_complete.html", {
        "total": total,
        "correct": stats["correct"],
        "wrong": stats["wrong"],
    })


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
