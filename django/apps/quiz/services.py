"""Service layer for quiz app."""


def generate_weekly_quiz(student):
    """Generate a quiz with questions from vocabulary words due for review."""
    from datetime import date, timedelta
    from apps.vocabulary.models import Word
    from apps.vocabulary.selectors import get_words_for_review
    from .models import Quiz, QuizQuestion

    # Get start of current week (Monday)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Check if quiz already exists
    quiz, created = Quiz.objects.get_or_create(
        student=student, week_start_date=week_start
    )
    if not created:
        return quiz  # Already generated

    # Get words due for review
    words = list(get_words_for_review(student)[:10])

    for word in words:
        if len(word.definition) > 5:
            q = QuizQuestion.objects.create(
                quiz=quiz,
                question_type="definition_to_word",
                prompt=f"Definition: {word.definition[:100]}",
                correct_answer=word.word,
            )

    return quiz
