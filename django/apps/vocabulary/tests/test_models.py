"""Tests for vocabulary app."""
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
