from __future__ import annotations

from typing import Type


class StageError(Exception):
    """Base class for classified stage failures."""


class RetryableStageError(StageError):
    """Transient failure that may succeed on retry."""


class FatalStageError(StageError):
    """Failure that should not be retried."""


RETRYABLE_TYPES: tuple[Type[Exception], ...] = (
    RetryableStageError,
)

_RETRYABLE_HINTS = (
    "timeout",
    "timed out",
    "rate limit",
    "429",
    "connection reset",
    "temporarily unavailable",
    "503",
    "502",
    "500",
)


def classify_stage_error(exc: Exception) -> StageError:
    """Convert an arbitrary exception into a classified StageError.

    Known StageError subclasses pass through. Otherwise, classify by message hints.
    """
    if isinstance(exc, StageError):
        return exc
    text = str(exc).lower()
    if any(hint in text for hint in _RETRYABLE_HINTS):
        return RetryableStageError(str(exc))
    return FatalStageError(str(exc))


def is_retryable(exc: Exception) -> bool:
    return isinstance(classify_stage_error(exc), RetryableStageError)
