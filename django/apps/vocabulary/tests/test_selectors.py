"""Tests for vocabulary selectors. DT-11."""
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.vocabulary.selectors import (
    get_word_failure_rate,
    get_difficult_words_detailed,
    get_difficult_words,
)
from apps.vocabulary.models import Word
from apps.profiles.models import Student


class TestGetWordFailureRate(TestCase):
    """Test get_word_failure_rate selector. DT-11."""

    def test_failure_rate_zero_reviews(self):
        """No reviews = 0% failure rate."""
        word = MagicMock(spec=Word, review_count=0, times_wrong=0)
        # Mock the queryset get
        with patch('apps.vocabulary.selectors.Word.objects.get') as mock_get:
            mock_get.return_value = word
            rate = get_word_failure_rate(1)
        self.assertEqual(rate, 0)

    def test_failure_rate_50_percent(self):
        """3 wrong out of 6 total = 50%."""
        word = MagicMock(spec=Word, review_count=3, times_wrong=3)
        with patch('apps.vocabulary.selectors.Word.objects.get') as mock_get:
            mock_get.return_value = word
            rate = get_word_failure_rate(1)
        self.assertEqual(rate, 50)

    def test_failure_rate_100_percent(self):
        """All wrong = 100%."""
        word = MagicMock(spec=Word, review_count=0, times_wrong=5)
        with patch('apps.vocabulary.selectors.Word.objects.get') as mock_get:
            mock_get.return_value = word
            rate = get_word_failure_rate(1)
        self.assertEqual(rate, 100)

    def test_failure_rate_nonexistent_word(self):
        """Non-existent word returns 0."""
        with patch('apps.vocabulary.selectors.Word.objects.get') as mock_get:
            mock_get.side_effect = Word.DoesNotExist
            rate = get_word_failure_rate(999)
        self.assertEqual(rate, 0)


class TestGetDifficultWordsDetailed(TestCase):
    """Test get_difficult_words_detailed selector. DT-11."""

    def test_returns_words_sorted_by_times_wrong(self):
        """Words should be sorted by times_wrong descending."""
        student = MagicMock(spec=Student)
        word1 = MagicMock()
        word1.times_wrong = 5
        word1.review_count = 10
        word1.mastery = "learning"

        word2 = MagicMock()
        word2.times_wrong = 2
        word2.review_count = 8
        word2.mastery = "learning"

        with patch('apps.vocabulary.selectors.Word.objects.filter') as mock_filter:
            mock_qs = MagicMock()
            mock_qs.exclude.return_value.order_by.return_value.__getitem__ = MagicMock(return_value=[word1, word2])
            mock_filter.return_value = mock_qs

            result = get_difficult_words_detailed(student, limit=10)

        # Verify ordering
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["times_wrong"], 5)
        self.assertEqual(result[1]["times_wrong"], 2)

    def test_excludes_mastered_words(self):
        """Mastered words should be excluded."""
        student = MagicMock(spec=Student)
        with patch('apps.vocabulary.selectors.Word.objects.filter') as mock_filter:
            mock_qs = MagicMock()
            mock_qs.exclude.return_value.order_by.return_value.__getitem__ = MagicMock(return_value=[])
            mock_filter.return_value = mock_qs

            get_difficult_words_detailed(student)

            # Verify exclude was called with mastery="mastered"
            mock_qs.exclude.assert_called_once_with(mastery="mastered")

    def test_failure_rate_calculation_in_result(self):
        """Each result item should include failure_rate."""
        student = MagicMock(spec=Student)
        word = MagicMock()
        word.times_wrong = 3
        word.review_count = 7
        word.mastery = "learning"

        with patch('apps.vocabulary.selectors.Word.objects.filter') as mock_filter:
            mock_qs = MagicMock()
            mock_qs.exclude.return_value.order_by.return_value.__getitem__ = MagicMock(return_value=[word])
            mock_filter.return_value = mock_qs

            result = get_difficult_words_detailed(student, limit=10)

        self.assertIn("failure_rate", result[0])
        # 3 / (7 + 3) = 30%
        self.assertEqual(result[0]["failure_rate"], 30)


class TestGetDifficultWords(TestCase):
    """Test get_difficult_words base selector. DT-06."""

    def test_filters_by_threshold(self):
        """Should filter words with times_wrong >= threshold."""
        student = MagicMock(spec=Student)
        with patch('apps.vocabulary.selectors.Word.objects.filter') as mock_filter:
            mock_qs = MagicMock()
            mock_filter.return_value = mock_qs

            get_difficult_words(student, threshold=3)

            mock_filter.assert_called_once_with(
                student=student,
                times_wrong__gte=3
            )