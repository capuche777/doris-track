"""Selectors for quiz app."""
from .models import Quiz, QuizQuestion


def get_quizzes(student):
    """Return all quizzes for a student, ordered by most recent first."""
    return Quiz.objects.filter(student=student).order_by("-week_start_date")


def get_quiz_detail(quiz_id, student):
    """Return a quiz with all its questions for a given student."""
    return Quiz.objects.filter(id=quiz_id, student=student).prefetch_related("questions").first()


def get_quiz_by_week(student, week_start_date):
    return Quiz.objects.filter(student=student, week_start_date=week_start_date).first()


def get_quiz_results(quiz):
    """Return results summary for a quiz."""
    questions = quiz.questions.all()
    total = questions.count()
    correct = questions.filter(is_correct=True).count()
    return {
        "total": total,
        "correct": correct,
        "score": round(correct / total * 100) if total > 0 else 0,
        "questions": [
            {
                "id": q.id,
                "type": q.question_type,
                "prompt": q.prompt,
                "correct_answer": q.correct_answer,
                "student_answer": q.student_answer,
                "is_correct": q.is_correct,
            }
            for q in questions
        ],
    }