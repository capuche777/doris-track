"""Views for quiz app."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from apps.profiles.models import Student
from .models import Quiz, QuizQuestion
from .selectors import get_quizzes, get_quiz_detail, get_quiz_results
from .services import submit_quiz_answer, get_quiz_results_summary


def quiz_list_view(request):
    """Show quiz history for a student."""
    student = Student.objects.first()
    if student is None:
        return HttpResponse("No student found. Please create a student first.", status=404)

    quizzes = get_quizzes(student)
    return render(request, "quiz/quiz_list.html", {"quizzes": quizzes, "student": student})


def quiz_take_view(request, quiz_id=None):
    """Show a quiz to take."""
    student = Student.objects.first()
    if student is None:
        return HttpResponse("No student found.", status=404)

    if quiz_id is None:
        # Get the current week's quiz or generate one
        from .services import generate_weekly_quiz
        from datetime import date, timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        quiz = generate_weekly_quiz(student)
    else:
        quiz = get_object_or_404(Quiz, id=quiz_id, student=student)

    questions = quiz.questions.all()
    return render(request, "quiz/quiz_take.html", {"quiz": quiz, "questions": questions})


def quiz_submit_view(request, question_id):
    """Submit an answer to a quiz question (AJAX or form POST)."""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    student_answer = request.POST.get("answer", "").strip()
    if not student_answer:
        return HttpResponse("Answer cannot be empty", status=400)

    try:
        is_correct, feedback = submit_quiz_answer(int(question_id), student_answer)
    except ValueError as e:
        return HttpResponse(str(e), status=404)

    return HttpResponse(feedback)


def quiz_results_view(request, quiz_id):
    """Show quiz results."""
    student = Student.objects.first()
    if student is None:
        return HttpResponse("No student found.", status=404)

    quiz = get_object_or_404(Quiz, id=quiz_id, student=student)
    summary = get_quiz_results_summary(quiz)
    results = get_quiz_results(quiz)

    return render(request, "quiz/quiz_results.html", {
        "quiz": quiz,
        "summary": summary,
        "results": results,
    })