"""Pure throughput calculation using an explicit authorized open-time denominator."""

from __future__ import annotations

from math import isfinite

from app.services.types import MetricResult


def calculate_throughput(
    completed_episode_count: int,
    valid_observation_count: int,
    scheduled_open_minutes: float | None,
    exclusions: dict[str, int],
) -> MetricResult:
    """Calculate completed episodes per scheduled open hour.

    Scheduled minutes must be supplied by the approved centre configuration;
    closures or staffing downtime are not inferred or removed here.
    """
    if completed_episode_count < 0:
        return MetricResult(
            "unavailable", None, "completed service episodes per scheduled open hour",
            None, None, 0, "Completed episode count cannot be negative.", exclusions,
        )
    if valid_observation_count <= 0:
        return MetricResult(
            "unavailable", None, "completed service episodes per scheduled open hour",
            None, None, 0,
            "No valid authorized observations support a throughput calculation.", exclusions,
        )
    if scheduled_open_minutes is None or not isfinite(scheduled_open_minutes) or scheduled_open_minutes <= 0:
        return MetricResult(
            "unavailable", None, "completed service episodes per scheduled open hour",
            None, None, 0,
            "Authorized scheduled open minutes must be explicitly supplied as a finite positive value.",
            exclusions,
        )
    open_hours = scheduled_open_minutes / 60
    return MetricResult(
        "available", completed_episode_count / open_hours,
        "completed service episodes per scheduled open hour",
        completed_episode_count, open_hours, completed_episode_count,
        "Valid completed episodes divided by authorized scheduled open hours; downtime is not selectively excluded.",
        exclusions,
    )
