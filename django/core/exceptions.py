"""Custom exception classes and the API exception handler for DorisTrack."""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as drf_exception_handler


class DorisTrackException(Exception):
    """Base exception for DorisTrack."""
    pass


class ScoreError(DorisTrackException):
    """Raised when a score operation fails."""
    pass


class VocabularyError(DorisTrackException):
    """Raised when a vocabulary operation fails."""
    pass


# --- API exceptions -------------------------------------------------------
# Specific, descriptive errors for the REST API. `default_code` doubles as the
# UPPERCASE_SNAKE_CASE error code surfaced to the client.

class StudentNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Student not found."
    default_code = "STUDENT_NOT_FOUND"


class WordNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Word not found."
    default_code = "WORD_NOT_FOUND"


class WordAlreadyExists(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This word already exists for the student."
    default_code = "WORD_ALREADY_EXISTS"


class QuizNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Quiz not found."
    default_code = "QUIZ_NOT_FOUND"


class QuestionNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Quiz question not found."
    default_code = "QUESTION_NOT_FOUND"


def api_exception_handler(exc, context):
    """
    Render DRF exceptions in the project's structured error format:

        {"error": {"code": "UPPERCASE_SNAKE_CASE", "message": "...",
                   "details": {...}}}

    Validation errors keep their per-field messages under ``details``.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data

    # Serializer/field validation errors arrive as a dict (or list) of messages
    # without a top-level "detail" key.
    is_validation_error = (
        isinstance(detail, list)
        or (isinstance(detail, dict) and "detail" not in detail)
    )

    if is_validation_error:
        error = {
            "code": "VALIDATION_ERROR",
            "message": "Validation failed.",
            "details": detail,
        }
    else:
        message = detail["detail"] if isinstance(detail, dict) else detail
        error = {
            "code": str(getattr(exc, "default_code", "error")).upper(),
            "message": str(message),
        }

    response.data = {"error": error}
    return response
