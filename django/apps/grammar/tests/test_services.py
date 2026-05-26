"""Tests for grammar app services and selectors."""
import pytest
from datetime import date, timedelta
from apps.profiles.models import Student
from apps.grammar.models import Correction
from apps.grammar import services, selectors


@pytest.mark.django_db
class TestCorrectionModel:
    def test_correction_creation(self):
        student = Student.objects.create(name="John", email="john@test.com")
        corr = Correction.objects.create(
            student=student,
            date=date.today(),
            student_mistake="I go yesterday",
            correct_version="I went yesterday",
            grammar_rule="Past simple of go",
            category="verb_tenses",
        )
        assert corr.category == "verb_tenses"

    def test_log_correction_service(self):
        student = Student.objects.create(name="John", email="john2@test.com")
        corr = services.log_correction(student, "mistake", "correct", category="prepositions")
        assert corr.category == "prepositions"


@pytest.mark.django_db
class TestGetCorrections:
    def test_get_all_corrections(self):
        student = Student.objects.create(name="Test", email="test@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        services.log_correction(student, "c", "d", category="articles")

        result = list(selectors.get_corrections(student))
        assert len(result) == 2

    def test_filter_by_category(self):
        student = Student.objects.create(name="Test", email="test2@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        services.log_correction(student, "c", "d", category="articles")

        result = list(selectors.get_corrections(student, category="articles"))
        assert len(result) == 1
        assert result[0].category == "articles"

    def test_filter_by_date_range(self):
        student = Student.objects.create(name="Test", email="test3@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        old = Correction.objects.create(
            student=student, date=date.today() - timedelta(days=60),
            student_mistake="old", correct_version="old corr", category="other"
        )

        result = list(selectors.get_corrections(student, date_from=date.today() - timedelta(days=30)))
        assert len(result) == 1


@pytest.mark.django_db
class TestGetCategories:
    def test_get_categories_with_counts(self):
        student = Student.objects.create(name="Test", email="test4@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        services.log_correction(student, "c", "d", category="verb_tenses")
        services.log_correction(student, "e", "f", category="articles")

        cats = selectors.get_categories(student.id)
        cat_dict = {c["category"]: c["count"] for c in cats}
        assert cat_dict["verb_tenses"] == 2
        assert cat_dict["articles"] == 1


@pytest.mark.django_db
class TestGetCommonMistakes:
    def test_empty_when_no_corrections(self):
        student = Student.objects.create(name="Test", email="test5@test.com")
        result = services.get_common_mistakes(student, period_days=30)
        assert result == []

    def test_ranked_by_frequency(self):
        student = Student.objects.create(name="Test", email="test6@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        services.log_correction(student, "c", "d", category="verb_tenses")
        services.log_correction(student, "e", "f", category="articles")

        result = services.get_common_mistakes(student, period_days=30)
        assert result[0]["category"] == "verb_tenses"
        assert result[0]["count"] == 2
        assert result[1]["category"] == "articles"

    def test_percentages_sum_to_100(self):
        student = Student.objects.create(name="Test", email="test7@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")
        services.log_correction(student, "c", "d", category="articles")

        result = services.get_common_mistakes(student, period_days=30)
        total_pct = sum(r["percentage"] for r in result)
        assert total_pct == 100.0


@pytest.mark.django_db
class TestGetMistakeTrend:
    def test_trend_for_category(self):
        student = Student.objects.create(name="Test", email="test8@test.com")
        services.log_correction(student, "a", "b", category="verb_tenses")

        result = services.get_mistake_trend(student, "verb_tenses", weeks=8)
        assert len(result) >= 1

    def test_empty_for_no_data(self):
        student = Student.objects.create(name="Test", email="test9@test.com")
        result = services.get_mistake_trend(student, "verb_tenses", weeks=8)
        assert result == []