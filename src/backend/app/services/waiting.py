"""Pure observed total, mean and worst-case wait calculations."""

from __future__ import annotations

from typing import Iterable

from app.services.types import EpisodeRecord, MetricResult


def calculate_waiting_metrics(
    wait_records: Iterable[tuple[EpisodeRecord, float]],
    exclusions: dict[str, int],
) -> tuple[MetricResult, MetricResult, MetricResult]:
    """Return total, mean and observed sample maximum for valid visits."""
    values = [minutes for _, minutes in wait_records]
    if not values:
        explanation = "No valid served visits have both a genuine check-in and service-start timestamp."
        return tuple(
            MetricResult("unavailable", None, unit, None, None, 0, explanation, exclusions)
            for unit in ("person-minutes", "minutes", "minutes")
        )  # type: ignore[return-value]
    total = sum(values)
    count = len(values)
    return (
        MetricResult("available", total, "person-minutes", total, count, count,
                     "Sum of observed waits among valid served visits in the declared cohort.", exclusions),
        MetricResult("available", total / count, "minutes per valid served visit", total, count, count,
                     "Total observed wait divided by the number of valid served visits.", exclusions),
        MetricResult("available", max(values), "minutes; observed sample maximum", max(values), count, count,
                     "Observed sample maximum; it is not a guaranteed maximum.", exclusions),
    )
