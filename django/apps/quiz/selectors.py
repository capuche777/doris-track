"""Selectors for quiz app."""
from .models import Quiz, QuizQuestion


def get_quiz_by_week(student, week_start_date):
    return Quiz.objects.filter(student=student, week_start_date=week_start_date).first()


def get_quiz_results(quiz):
    questions = quiz.questions.all()
    total = questions.count()
    correct = questions.filter(is_correct=True).count()
    return {"total": total, "correct": correct, "score": round(correct / total * 100) if total > 0 else 0}
