"""Tests for vocabulary services — DT-05 binary spaced repetition."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word
from apps.vocabulary.services import (
    update_word_after_review,
    check_review_answer,
    calculate_next_interval,
    create_word,
    update_word,
)


@pytest.mark.django_db
class TestCalculateNextInterval:
    """Tests for calculate_next_interval — DT-05 binary system."""

    def test_correct_advances_to_next_interval(self):
        """Correct answer advances interval index."""
        assert calculate_next_interval(0, True) == 2   # 1→2
        assert calculate_next_interval(1, True) == 4   # 2→4
        assert calculate_next_interval(2, True) == 7   # 4→7

    def test_wrong_resets_to_first_interval(self):
        """Wrong answer resets to 1 day (index 0)."""
        assert calculate_next_interval(3, False) == 1  # 7→1
        assert calculate_next_interval(5, False) == 1  # 30→1

    def test_correct_at_last_interval_stays_at_max(self):
        """Correct at max interval (30) stays at 30."""
        assert calculate_next_interval(5, True) == 30  # stays at max


@pytest.mark.django_db
class TestUpdateWordAfterReview:
    """Tests for update_word_after_review — DT-05 binary system."""

    def setup_method(self):
        """Create a student and word for testing."""
        self.student = Student.objects.create(name="Test Student", email="test@test.com")

    def test_correct_increments_review_count(self):
        """Correct answer increments review_count."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="new", current_interval_days=1,
        )
        update_word_after_review(word, True)
        assert word.review_count == 1

    def test_wrong_increments_review_count_and_times_wrong(self):
        """Wrong answer increments both review_count and times_wrong."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="learning", current_interval_days=2, times_wrong=0,
        )
        update_word_after_review(word, False)
        assert word.review_count == 1
        assert word.times_wrong == 1

    def test_wrong_resets_interval_to_one_day(self):
        """Wrong answer resets current_interval_days to 1."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="learning", current_interval_days=7,
        )
        update_word_after_review(word, False)
        assert word.current_interval_days == 1

    def test_correct_advances_interval(self):
        """Correct answer advances interval."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="learning", current_interval_days=2,
        )
        update_word_after_review(word, True)
        assert word.current_interval_days == 4

    def test_new_to_learning_transition(self):
        """After 2 correct reviews, mastery goes new→learning."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="new", current_interval_days=1, review_count=0,
        )
        update_word_after_review(word, True)   # review 1
        assert word.mastery == "new"
        update_word_after_review(word, True)   # review 2
        assert word.mastery == "learning"

    def test_learning_to_mastered_transition(self):
        """At interval index >=4 (15 days), mastery goes learning→mastered."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="learning", current_interval_days=7, review_count=5,
        )
        update_word_after_review(word, True)
        assert word.current_interval_days == 15
        # current_interval_idx for 15 is 4, so mastery transitions
        update_word_after_review(word, True)
        assert word.mastery == "mastered"

    def test_mastered_on_wrong_resets_to_learning(self):
        """Wrong answer on mastered word resets mastery to learning."""
        word = Word.objects.create(
            student=self.student, word="test", definition="test def",
            mastery="mastered", current_interval_days=30, times_wrong=0,
        )
        update_word_after_review(word, False)
        assert word.mastery == "learning"
        assert word.times_wrong == 1


@pytest.mark.django_db
class TestCheckReviewAnswer:
    """Tests for check_review_answer service function. DT-05."""

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
        """Wrong answer should increment word's times_wrong counter."""
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


@pytest.mark.django_db
class TestAcceptedAnswers:
    """check_review_answer should honour the word's accepted_answers list."""

    def setup_method(self):
        self.student = Student.objects.create(
            name="Accepted Tester", email="accepted@test.com"
        )
        self.word = Word.objects.create(
            student=self.student,
            word="to shut down",
            definition="to stop operating",
            accepted_answers=["shut down"],
            next_review_date=date.today(),
        )

    def test_accepted_answer_is_correct(self):
        assert check_review_answer(self.word.id, "shut down")["correct"] is True

    def test_accepted_answer_is_case_insensitive(self):
        assert check_review_answer(self.word.id, "  SHUT DOWN ")["correct"] is True

    def test_main_word_still_matches(self):
        assert check_review_answer(self.word.id, "to shut down")["correct"] is True

    def test_unlisted_answer_is_wrong(self):
        assert check_review_answer(self.word.id, "power off")["correct"] is False

    def test_correct_answer_is_always_the_main_word(self):
        """Matching an accepted answer still reports the main word as correct."""
        result = check_review_answer(self.word.id, "shut down")
        assert result["correct_answer"] == "to shut down"

    def test_empty_accepted_answers_behaves_as_before(self):
        word = Word.objects.create(
            student=self.student, word="vow", definition="a promise",
            next_review_date=date.today(),
        )
        assert check_review_answer(word.id, "vow")["correct"] is True
        assert check_review_answer(word.id, "promise")["correct"] is False


@pytest.mark.django_db
class TestCreateAndUpdateWord:
    """create_word / update_word handle accepted_answers."""

    def setup_method(self):
        self.student = Student.objects.create(
            name="CRUD Tester", email="crud@test.com"
        )

    def test_create_word_defaults_to_empty_accepted_answers(self):
        word = create_word(self.student, word="vow", definition="a promise")
        assert word.accepted_answers == []

    def test_create_word_stores_accepted_answers(self):
        word = create_word(
            self.student, word="to choke", definition="to be unable to breathe",
            accepted_answers=["choke"],
        )
        assert word.accepted_answers == ["choke"]

    def test_update_word_sets_accepted_answers(self):
        word = create_word(self.student, word="to strike", definition="to hit")
        updated = update_word(word.id, accepted_answers=["strike"])
        updated.refresh_from_db()
        assert updated.accepted_answers == ["strike"]

    def test_update_word_ignores_non_editable_fields(self):
        word = create_word(self.student, word="to dot", definition="d")
        update_word(word.id, mastery="mastered", review_count=99)
        word.refresh_from_db()
        assert word.mastery == "new"
        assert word.review_count == 0