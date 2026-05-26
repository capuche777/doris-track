"""Tests for vocabulary services — DT-06."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word
from apps.vocabulary.services import calculate_sm2, update_word_after_review, check_review_answer


@pytest.mark.django_db
class TestCheckReviewAnswer:
    """Tests for check_review_answer service function. DT-06."""

    def setup_method(self):
        """Create a student and word for testing."""
        self.student = Student.objects.create(name="Test Student", email="test@test.com")
        self.word = Word.objects.create(
            student=self.student,
            word="ephemeral",
            definition="lasting for a very short time",
            difficulty="C1",
            next_review_date=date.today(),
            mastery="learning",
        )

    def test_correct_answer_returns_correct_true(self):
        """Case-insensitive exact match should return correct=True."""
        result = check_review_answer(self.word.id, "ephemeral")
        assert result["correct"] is True

    def test_correct_answer_case_insensitive(self):
        """Comparison should be case-insensitive."""
        result = check_review_answer(self.word.id, "EPHEMERAL")
        assert result["correct"] is True
        result2 = check_review_answer(self.word.id, "Ephemeral")
        assert result2["correct"] is True

    def test_correct_answer_strips_whitespace(self):
        """Leading/trailing whitespace should be stripped before comparison."""
        result = check_review_answer(self.word.id, "  ephemeral  ")
        assert result["correct"] is True

    def test_incorrect_answer_returns_correct_false(self):
        """Wrong answer should return correct=False."""
        result = check_review_answer(self.word.id, "permanent")
        assert result["correct"] is False

    def test_incorrect_answer_returns_correct_answer(self):
        """Response should include the correct answer."""
        result = check_review_answer(self.word.id, "wrong")
        assert result["correct"] is False
        assert result["correct_answer"] == "ephemeral"

    def test_incorrect_answer_increments_times_wrong(self):
        """DT-06: wrong answer should increment word's times_wrong counter."""
        initial = self.word.times_wrong
        check_review_answer(self.word.id, "wrong")
        self.word.refresh_from_db()
        assert self.word.times_wrong == initial + 1

    def test_correct_answer_does_not_increment_times_wrong(self):
        """Correct answer should NOT increment times_wrong."""
        self.word.times_wrong = 0
        self.word.save()
        check_review_answer(self.word.id, "ephemeral")
        self.word.refresh_from_db()
        assert self.word.times_wrong == 0

    def test_returns_next_review_date(self):
        """Response should include the updated next_review_date."""
        result = check_review_answer(self.word.id, "ephemeral")
        assert "next_review" in result
        assert result["next_review"] is not None
