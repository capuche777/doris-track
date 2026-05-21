from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from apps.profiles.models import Student
from apps.profiles.selectors import get_student_profile


def student_profile_view(request, student_id=None):
    """Render the student profile page."""
    # If no student_id provided, get the first (and only) student
    if student_id is None:
        student = Student.objects.first()
        if student is None:
            return HttpResponse("No student found. Please create a student first.", status=404)
    else:
        student = get_student_profile(student_id)
        if student is None:
            return HttpResponse("Student not found.", status=404)

    context = {
        "student": student,
    }
    return render(request, "profiles/student_profile.html", context)