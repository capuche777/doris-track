"""Views for grammar app."""
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.profiles.models import Student
from .models import Correction
from . import services, selectors


def correction_list_view(request):
    """
    Display all corrections for a student with optional filters.
    URL: /grammar/
    """
    student = Student.objects.first()
    if not student:
        return render(request, "grammar/correction_list.html", {
            "corrections": [],
            "categories": [],
            "student": None,
        })

    category = request.GET.get("category", "")
    date_from_str = request.GET.get("date_from", "")
    date_to_str = request.GET.get("date_to", "")

    date_from = date.fromisoformat(date_from_str) if date_from_str else None
    date_to = date.fromisoformat(date_to_str) if date_to_str else None

    corrections = selectors.get_corrections(
        student, category=category or None, date_from=date_from, date_to=date_to
    )
    categories = selectors.get_categories(student.id)

    return render(request, "grammar/correction_list.html", {
        "corrections": corrections,
        "categories": categories,
        "student": student,
        "filters": {"category": category, "date_from": date_from_str, "date_to": date_to_str},
    })


def correction_add_view(request):
    """Add a new grammar correction."""
    student = Student.objects.first()
    if not student:
        messages.error(request, "No student found.")
        return redirect("grammar:correction_list")

    if request.method == "POST":
        mistake = request.POST.get("student_mistake", "").strip()
        correct = request.POST.get("correct_version", "").strip()
        rule = request.POST.get("grammar_rule", "").strip()
        category = request.POST.get("category", "other").strip()

        if mistake and correct:
            services.log_correction(
                student=student,
                mistake=mistake,
                correct=correct,
                rule=rule,
                category=category or "other",
            )
            messages.success(request, "Correction logged.")
            return redirect("grammar:correction_list")
        else:
            messages.error(request, "Both mistake and correct version are required.")

    return render(request, "grammar/correction_form.html", {"student": student})


def correction_analytics_view(request):
    """Analytics page: bar chart of mistake categories + weekly trend."""
    student = Student.objects.first()
    if not student:
        return render(request, "grammar/correction_analytics.html", {
            "mistake_data": [],
            "trend_data": [],
            "student": None,
        })

    period = int(request.GET.get("period", 30))
    category = request.GET.get("trend_category", "")

    mistake_data = services.get_common_mistakes(student, period_days=period)
    trend_data = services.get_mistake_trend(student, category) if category else []

    # Prepare chart data as JSON-serializable lists
    category_labels = [m["label"] for m in mistake_data]
    count_values = [m["count"] for m in mistake_data]
    percentages = [m["percentage"] for m in mistake_data]

    return render(request, "grammar/correction_analytics.html", {
        "mistake_data": mistake_data,
        "trend_data": trend_data,
        "student": student,
        "period": period,
        "selected_category": category,
        "chart_labels": category_labels,
        "chart_values": count_values,
        "chart_percentages": percentages,
    })