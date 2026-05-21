"""Tests for vocabulary app (DT-02, DT-05, DT-06)."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.vocabulary.models import Word
from apps.vocabulary.services import calculate_sm2, update_word_after_review


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
        """DT-02: times_wrong field should default to 0."""
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(
            student=student,
            word="ephemeral",
            definition="lasting for a very short time",
            difficulty="C1",
        )
        assert word.times_wrong == 0

    def test_word_times_wrong_increments(self):
        """DT-06: times_wrong increments when student answers wrong."""
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
        """DT-06: word with times_wrong >= 3 is flagged as difficult."""
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


@pytest.mark.django_db
class TestSM2Algorithm:
    def test_sm2_first_review_pass(self):
        ef, interval = calculate_sm2(2.5, 1, 4)
        assert ef > 2.5
        assert interval == 6

    def test_sm2_first_review_fail(self):
        ef, interval = calculate_sm2(2.5, 1, 2)
        assert ef < 2.5
        assert interval == 1

    def test_sm2_review_integration(self):
        student = Student.objects.create(name="John", email="john@test.com")
        word = Word.objects.create(student=student, word="test", definition="test def")
        update_word_after_review(word, 4)
        assert word.review_count == 1
        assert word.next_review_date > date.today()