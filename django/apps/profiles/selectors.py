"""Selectors for profiles app."""
from .models import Student, Tutor


def get_all_tutors():
    return Tutor.objects.all()


def get_student_by_email(email: str):
    return Student.objects.filter(email=email).first()


def get_students_by_tutor(tutor):
    return Student.objects.filter(tutor=tutor)


def get_student_profile(student_id: int):
    """Return the student with the given id, or None if not found."""
    return Student.objects.filter(id=student_id).first()
