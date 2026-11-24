"""Shared immutable input and result types for scheduling calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

PolicyArm = Literal["fcfs", "slot_policy"]
ResultStatus = Literal["available", "unavailable", "candidate_only"]


@dataclass(frozen=True)
class EpisodeRecord:
    """One authorized, provenance-bearing event row for one visit episode."""

    episode_id: str
    centre_id: str
    crop_code: str
    season_code: str
    policy_arm: str
    policy_version: str
    service_stream_id: str
    centre_configuration_reference: str
    service_assumptions_reference: str
    operating_period_id: str
    comparison_block_id: str
    check_in_at: datetime | None
    service_start_at: datetime | None
    service_complete_at: datetime | None
    cancelled_at: datetime | None
    no_show_declared_at: datetime | None
    no_show_confirmed: bool
    check_in_sequence: int | None
    fairness_group: str | None
    deduplication_resolved: bool
    correction_resolved: bool
    provenance_valid: bool
    eligible: bool
    input_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvaluationScope:
    centre_id: str
    crop_code: str
    season_code: str
    policy_arm: str
    policy_version: str
    centre_configuration_reference: str
    period_start: datetime
    period_end: datetime
    extracted_at: datetime
    scheduled_open_minutes: float | None
    fairness_groups_authorized: bool
    fairness_minimum_group_observations: int | None
    service_assumptions_reference: str
    no_show_policy_authorized: bool


@dataclass(frozen=True)
class MetricResult:
    status: ResultStatus
    value: float | None
    unit: str
    numerator: float | int | None
    denominator: float | int | None
    valid_records: int
    explanation: str
    exclusions: dict[str, int] = field(default_factory=dict)
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "value": self.value,
            "unit": self.unit,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "valid_records": self.valid_records,
            "explanation": self.explanation,
            "exclusions": self.exclusions,
            "details": self.details,
        }


@dataclass(frozen=True)
class WaitMetrics:
    total_wait: MetricResult
    mean_wait: MetricResult
    worst_case_wait: MetricResult
    throughput: MetricResult
    fairness_spread: MetricResult
    cohort_arrivals: int
    completed_episodes: int
    censored_episodes: int
    validated_records: int
    exclusions: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_wait": self.total_wait.to_dict(),
            "mean_wait": self.mean_wait.to_dict(),
            "worst_case_wait": self.worst_case_wait.to_dict(),
            "throughput": self.throughput.to_dict(),
            "fairness_spread": self.fairness_spread.to_dict(),
            "cohort_arrivals": self.cohort_arrivals,
            "completed_episodes": self.completed_episodes,
            "censored_episodes": self.censored_episodes,
            "validated_records": self.validated_records,
            "exclusions": self.exclusions,
        }
