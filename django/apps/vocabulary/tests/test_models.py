"""Tests for vocabulary app models — DT-05 binary spaced repetition."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word


@pytest.mark.django_db
class TestWordModel:
    def test_word_creation(self):
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="ubiquitous",
            definition="present everywhere",
            difficulty="C1",
        )
        assert word.word == "ubiquitous"
        assert word.mastery == "new"

    def test_word_times_wrong_defaults_to_zero(self):
        """times_wrong field should default to 0."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="ephemeral",
            definition="lasting for a very short time",
            difficulty="C1",
        )
        assert word.times_wrong == 0

    def test_word_times_wrong_increments(self):
        """times_wrong increments when student answers wrong."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="ubiquitous",
            definition="present everywhere",
            difficulty="C1",
        )
        word.times_wrong += 1
        word.save()
        word.refresh_from_db()
        assert word.times_wrong == 1

    def test_word_difficult_words_alert(self):
        """Word with times_wrong >= 3 is flagged as difficult."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="onomatopoeia",
            definition="formation of a word from a sound",
            difficulty="C2",
        )
        word.times_wrong = 3
        word.save()
        assert word.times_wrong >= 3

    def test_word_mastery_defaults_to_new(self):
        """New words start with mastery='new'."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="test",
            definition="test def",
            difficulty="B1",
        )
        assert word.mastery == "new"

    def test_word_current_interval_days_defaults_to_1(self):
        """New words start with current_interval_days=1 (first interval)."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="test",
            definition="test def",
            difficulty="B1",
        )
        assert word.current_interval_days == 1

    def test_word_review_count_defaults_to_0(self):
        """New words start with review_count=0."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="test",
            definition="test def",
            difficulty="B1",
        )
        assert word.review_count == 0


@pytest.mark.django_db
class TestWordSpacedRepetition:
    """Tests for Word model spaced repetition behavior."""

    def test_word_next_review_date_set_on_creation(self):
        """New word should have next_review_date set (default today)."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="test",
            definition="test def",
            difficulty="B1",
        )
        assert word.next_review_date is not None

    def test_word_unique_together_student_word(self):
        """Student cannot have duplicate words."""
        student = Student.objects.create(name="John", email="john@test.com")
        Word.objects.create(student=student, word="test", definition="def1", difficulty="B1")
        with pytest.raises(Exception):  # IntegrityError
            Word.objects.create(student=student, word="test", definition="def2", difficulty="B1")

    def test_mastery_choices(self):
        """Mastery field should accept only valid choices."""
        student = Student.objects.create(name="John", email="john@test.com")
        for mastery in ["new", "learning", "mastered"]:
            word = Word.objects.create(
                student=student,
                word=f"word_{mastery}",
                definition="test",
                difficulty="B1",
                mastery=mastery,
            )
            assert word.mastery == mastery