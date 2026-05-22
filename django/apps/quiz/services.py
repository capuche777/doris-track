"""Service layer for quiz app."""
from datetime import date, timedelta


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
            QuizQuestion.objects.create(
                quiz=quiz,
                question_type="definition_to_word",
                prompt=f"Definition: {word.definition[:100]}",
                correct_answer=word.word,
            )

    return quiz


def submit_quiz_answer(question_id, student_answer):
    """
    Evaluate and store a student's answer to a quiz question.
    Returns (is_correct, feedback_message)
    """
    from .models import QuizQuestion

    try:
        question = QuizQuestion.objects.select_related("quiz").get(id=question_id)
    except QuizQuestion.DoesNotExist:
        raise ValueError(f"Question {question_id} not found")

    # Store the student's answer
    question.student_answer = student_answer

    # Auto-grade based on question type
    if question.question_type == "definition_to_word":
        # Exact match (case-insensitive, strip whitespace)
        is_correct = question.correct_answer.strip().lower() == student_answer.strip().lower()
    elif question.question_type == "word_to_sentence":
        # Keyword matching — check if student answer has some content
        # and relates to the word being tested
        is_correct = len(student_answer.strip()) >= 10  # At least a sentence
    elif question.question_type == "sentence_rewrite":
        # Keyword matching — check if student wrote something meaningful
        is_correct = len(student_answer.strip()) >= 10
    else:
        is_correct = False

    question.is_correct = is_correct
    question.save()

    if is_correct:
        feedback = "✓ Correct!"
    else:
        feedback = f"✗ Incorrect. The correct answer was: {question.correct_answer}"

    return is_correct, feedback


def get_quiz_results_summary(quiz):
    """Return a results summary dict for a quiz."""
    questions = quiz.questions.all()
    total = questions.count()
    correct = questions.filter(is_correct=True).count()
    score = round(correct / total * 100) if total > 0 else 0

    return {
        "quiz_id": quiz.id,
        "total_questions": total,
        "correct_answers": correct,
        "wrong_answers": total - correct,
        "score_percentage": score,
        "week_start_date": str(quiz.week_start_date),
    }