"""Custom exception classes for DorisTrack."""


class DorisTrackException(Exception):
    """Base exception for DorisTrack."""
    pass


class ScoreError(DorisTrackException):
    """Raised when a score operation fails."""
    pass


class VocabularyError(DorisTrackException):
    """Raised when a vocabulary operation fails."""
    pass
