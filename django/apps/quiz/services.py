"""Service layer for quiz app."""
from datetime import date, timedelta

from apps.vocabulary.selectors import get_words_for_review
from .models import Quiz, QuizQuestion


def generate_weekly_quiz(student):
    """Generate a quiz with questions from vocabulary words due for review.

    Creates three question types per word:
    - definition_to_word: given definition, return the word
    - word_to_sentence: given word, write it in a sentence
    - sentence_rewrite: given original sentence, rewrite it using the word
    """
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
        # Type 1: definition_to_word
        if len(word.definition) > 5:
            QuizQuestion.objects.create(
                quiz=quiz,
                question_type="definition_to_word",
                prompt=f"Definition: {word.definition[:100]}",
                correct_answer=word.word,
            )

        # Type 2: word_to_sentence (only if word has example_sentence)
        if word.example_sentence:
            QuizQuestion.objects.create(
                quiz=quiz,
                question_type="word_to_sentence",
                prompt=f"Use the word '{word.word}' in a sentence. Write a meaningful sentence using this word.",
                correct_answer=word.example_sentence,
            )

        # Type 3: sentence_rewrite (only if word has example_sentence)
        if word.example_sentence:
            QuizQuestion.objects.create(
                quiz=quiz,
                question_type="sentence_rewrite",
                prompt=f"Rewrite this sentence using the word '{word.word}': {word.example_sentence}",
                correct_answer=word.example_sentence,
            )

    return quiz


def submit_quiz_answer(question_id, student_answer):
    """
    Evaluate and store a student's answer to a quiz question.
    Returns (is_correct, feedback_message)
    """
    try:
        question = QuizQuestion.objects.select_related("quiz").get(id=question_id)
    except QuizQuestion.DoesNotExist:
        raise ValueError(f"Question {question_id} not found")

    # Store the student's answer
    question.student_answer = student_answer
    student_answer_lower = student_answer.strip().lower()

    # Auto-grade based on question type
    if question.question_type == "definition_to_word":
        # Exact match (case-insensitive, strip whitespace)
        is_correct = question.correct_answer.strip().lower() == student_answer_lower

    elif question.question_type in ("word_to_sentence", "sentence_rewrite"):
        # Keyword matching: check if the correct answer's key words appear in student answer
        correct_keywords = set(question.correct_answer.strip().lower().split())
        student_words = set(student_answer_lower.split())
        # Remove common short words (stopwords)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "to", "of", "in", "for", "on", "with", "at", "by", "and",
                     "or", "it", "that", "this", "as", "from"}
        keywords = correct_keywords - stopwords
        matched = keywords & student_words
        # Require at least half of the keywords to match
        is_correct = len(matched) >= max(1, len(keywords) // 2)

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
