"""Compatibility entrypoint for P12 recommendation outcome calibration.

Forecast calibration remains in :mod:`calibration_service`; this module is
the separate, gated recommendation-memory contract.
"""

from src.services.agentic_outcome_service import (
    AgenticOutcomeService,
    CALIBRATION_THRESHOLDS,
    MIN_BOOKED_CALLS,
    MIN_POSITIVE_REPLIES,
    MIN_SENT_PACKAGES,
    OUTCOME_MEMORY_VERSION,
    OutcomeAssociation,
    OutcomeCalibrationService,
    OutcomeCalibrationSummary,
    RecommendationOutcomeMemoryService,
    RecommendationOutcomeService,
)


AgenticCalibrationService = OutcomeCalibrationService


__all__ = [
    "OUTCOME_MEMORY_VERSION",
    "CALIBRATION_THRESHOLDS",
    "MIN_SENT_PACKAGES",
    "MIN_POSITIVE_REPLIES",
    "MIN_BOOKED_CALLS",
    "OutcomeAssociation",
    "OutcomeCalibrationSummary",
    "RecommendationOutcomeService",
    "OutcomeCalibrationService",
    "RecommendationOutcomeMemoryService",
    "AgenticOutcomeService",
    "AgenticCalibrationService",
]
