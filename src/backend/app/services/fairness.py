"""Pure fairness-spread calculation for approved subgroups."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.services.types import EpisodeRecord, MetricResult


def calculate_fairness_spread(
    wait_records: Iterable[tuple[EpisodeRecord, float]],
    *,
    groups_authorized: bool,
    minimum_group_observations: int | None,
    exclusions: dict[str, int],
) -> MetricResult:
    """Compute max(group mean wait) - min(group mean wait), with explicit gates."""
    unit = "minutes between subgroup means"
    if not groups_authorized:
        return _unavailable(unit, "Fairness grouping has not been authorized.", exclusions)
    records = list(wait_records)
    grouped: dict[str, list[float]] = defaultdict(list)
    for record, wait in records:
        if record.fairness_group:
            grouped[record.fairness_group].append(wait)
    counts = {group: len(values) for group, values in grouped.items()}
    if minimum_group_observations is None or minimum_group_observations < 1:
        return _unavailable(
            unit,
            "An approved minimum observation count per group has not been supplied.",
            exclusions,
            {"group_counts": counts, "ungrouped_valid_wait_records": sum(not r.fairness_group for r, _ in records),
             "uncertainty_status": "not_computed"},
        )
    if len(grouped) < 2:
        return _unavailable(
            unit, "At least two authorized groups with valid observations are required.", exclusions,
            {"group_counts": counts, "ungrouped_valid_wait_records": sum(not r.fairness_group for r, _ in records),
             "uncertainty_status": "not_computed"},
        )
    inadequate = {group: len(values) for group, values in grouped.items() if len(values) < minimum_group_observations}
    if inadequate:
        return _unavailable(
            unit,
            f"Group counts do not meet the approved minimum of {minimum_group_observations} observations: {inadequate}.",
            exclusions,
            {"group_counts": counts, "approved_minimum_group_observations": minimum_group_observations,
             "ungrouped_valid_wait_records": sum(not r.fairness_group for r, _ in records),
             "uncertainty_status": "not_computed"},
        )
    means = [sum(values) / len(values) for values in grouped.values()]
    value = max(means) - min(means)
    count = sum(map(len, grouped.values()))
    return MetricResult(
        "available", value, unit, value, count, count,
        "Difference between the largest and smallest approved subgroup mean waits.", exclusions,
        {"group_counts": counts, "approved_minimum_group_observations": minimum_group_observations,
         "ungrouped_valid_wait_records": sum(not r.fairness_group for r, _ in records),
         "uncertainty_status": "not_computed"},
    )


def _unavailable(
    unit: str, explanation: str, exclusions: dict[str, int], details: dict[str, object] | None = None
) -> MetricResult:
    return MetricResult("unavailable", None, unit, None, None, 0, explanation, exclusions, details or {})
