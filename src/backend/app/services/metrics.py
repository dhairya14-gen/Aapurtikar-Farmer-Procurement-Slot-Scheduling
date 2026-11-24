"""Metric aggregation across the pure validation and metric modules."""

from __future__ import annotations

from typing import Iterable

from app.services.fairness import calculate_fairness_spread
from app.services.throughput import calculate_throughput
from app.services.types import EpisodeRecord, EvaluationScope, WaitMetrics
from app.services.validation import validate_episode_records
from app.services.waiting import calculate_waiting_metrics


def calculate_metrics(records: Iterable[EpisodeRecord], scope: EvaluationScope) -> WaitMetrics:
    """Calculate observed total/mean/worst wait, throughput and fairness spread."""
    cohort = validate_episode_records(records, scope)
    total, mean, worst = calculate_waiting_metrics(cohort.wait_minutes, cohort.exclusions)
    throughput = calculate_throughput(
        len(cohort.completed), cohort.validated_records,
        scope.scheduled_open_minutes, cohort.throughput_exclusions
    )
    fairness = calculate_fairness_spread(
        cohort.wait_minutes,
        groups_authorized=scope.fairness_groups_authorized,
        minimum_group_observations=scope.fairness_minimum_group_observations,
        exclusions=cohort.exclusions,
    )
    return WaitMetrics(
        total_wait=total,
        mean_wait=mean,
        worst_case_wait=worst,
        throughput=throughput,
        fairness_spread=fairness,
        cohort_arrivals=cohort.arrived,
        completed_episodes=len(cohort.completed),
        censored_episodes=cohort.censored,
        validated_records=cohort.validated_records,
        exclusions=cohort.exclusions,
    )
