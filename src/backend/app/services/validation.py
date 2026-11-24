"""Event and scope validation shared by metric calculations and replay."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable

from app.services.types import EpisodeRecord, EvaluationScope


@dataclass(frozen=True)
class ValidatedCohort:
    wait_minutes: tuple[tuple[EpisodeRecord, float], ...]
    completed: tuple[EpisodeRecord, ...]
    arrived: int
    censored: int
    validated_records: int
    exclusions: dict[str, int]
    throughput_exclusions: dict[str, int]


def is_aware_timestamp(value: datetime | None) -> bool:
    return value is not None and value.tzinfo is not None and value.utcoffset() is not None


def validate_evaluation_scope(scope: EvaluationScope) -> str | None:
    if not all(is_aware_timestamp(value) for value in (scope.period_start, scope.period_end, scope.extracted_at)):
        return "Evaluation period and extraction timestamps must include timezone offsets."
    if scope.period_end <= scope.period_start:
        return "Evaluation period end must be after its start."
    if scope.extracted_at < scope.period_end:
        return "Extraction time must not precede the end of the declared cohort period."
    return None


def validate_episode_records(records: Iterable[EpisodeRecord], scope: EvaluationScope) -> ValidatedCohort:
    """Create valid wait/completion cohorts and count exclusions by reason."""
    exclusions: Counter[str] = Counter()
    throughput_exclusions: Counter[str] = Counter()
    waits: list[tuple[EpisodeRecord, float]] = []
    completed: list[EpisodeRecord] = []
    arrived_ids: set[str] = set()
    censored = 0
    record_list = list(records)
    seen_ids: Counter[str] = Counter(record.episode_id for record in record_list)
    scope_error = validate_evaluation_scope(scope)
    if scope_error:
        count = len(record_list) or 1
        return ValidatedCohort((), (), 0, 0, 0, {"invalid_scope": count}, {"invalid_scope": count})

    validated_records = 0

    for record in record_list:
        if seen_ids[record.episode_id] > 1:
            exclusions["duplicate_episode"] += 1
            throughput_exclusions["duplicate_episode"] += 1
            continue
        if not record.deduplication_resolved:
            exclusions["unresolved_duplicate"] += 1
            throughput_exclusions["unresolved_duplicate"] += 1
            continue
        if not record.correction_resolved:
            exclusions["unresolved_correction"] += 1
            throughput_exclusions["unresolved_correction"] += 1
            continue
        if not record.provenance_valid:
            exclusions["invalid_provenance"] += 1
            throughput_exclusions["invalid_provenance"] += 1
            continue
        if not record.eligible:
            exclusions["ineligible"] += 1
            throughput_exclusions["ineligible"] += 1
            continue
        if (
            record.centre_id != scope.centre_id
            or record.crop_code != scope.crop_code
            or record.season_code != scope.season_code
            or record.policy_arm != scope.policy_arm
            or record.policy_version != scope.policy_version
        ):
            exclusions["out_of_scope"] += 1
            throughput_exclusions["out_of_scope"] += 1
            continue
        if record.service_assumptions_reference != scope.service_assumptions_reference:
            exclusions["service_assumptions_mismatch"] += 1
            throughput_exclusions["service_assumptions_mismatch"] += 1
            continue
        if record.centre_configuration_reference != scope.centre_configuration_reference:
            exclusions["centre_configuration_mismatch"] += 1
            throughput_exclusions["centre_configuration_mismatch"] += 1
            continue
        if record.input_errors:
            reason = record.input_errors[0]
            exclusions[reason] += 1
            throughput_exclusions[reason] += 1
            continue
        if record.no_show_confirmed and not scope.no_show_policy_authorized:
            exclusions["unverified_no_show_status"] += 1
            throughput_exclusions["unverified_no_show_status"] += 1
            continue
        if record.no_show_confirmed and record.no_show_declared_at is None:
            exclusions["invalid_no_show_declaration"] += 1
            throughput_exclusions["invalid_no_show_declaration"] += 1
            continue
        timestamps = (
            record.check_in_at,
            record.service_start_at,
            record.service_complete_at,
            record.cancelled_at,
            record.no_show_declared_at,
        )
        if any(value is not None and not is_aware_timestamp(value) for value in timestamps):
            exclusions["invalid_timestamp_timezone"] += 1
            throughput_exclusions["invalid_timestamp_timezone"] += 1
            continue
        if any(value is not None and value > scope.extracted_at for value in timestamps):
            exclusions["event_after_extraction"] += 1
            throughput_exclusions["event_after_extraction"] += 1
            continue
        check_in = record.check_in_at
        if check_in is None:
            if record.no_show_confirmed and record.no_show_declared_at:
                reason = "no_show"
            elif record.no_show_confirmed:
                reason = "invalid_no_show_declaration"
            elif record.no_show_declared_at:
                reason = "pending_no_show"
            elif record.cancelled_at:
                reason = "cancelled_before_check_in"
            else:
                reason = "missing_check_in"
            exclusions[reason] += 1
            throughput_exclusions[reason] += 1
            continue
        if not (scope.period_start <= check_in < scope.period_end):
            exclusions["outside_cohort_window"] += 1
            throughput_exclusions["outside_cohort_window"] += 1
            continue
        arrived_ids.add(record.episode_id)
        if record.no_show_declared_at is not None:
            exclusions["conflicting_no_show_and_check_in"] += 1
            throughput_exclusions["conflicting_no_show_and_check_in"] += 1
            continue
        if record.cancelled_at is not None and record.cancelled_at <= check_in:
            exclusions["invalid_event_order"] += 1
            throughput_exclusions["invalid_event_order"] += 1
            continue

        start = record.service_start_at
        complete = record.service_complete_at
        cancel = record.cancelled_at
        if start is None:
            if complete is not None:
                exclusions["completion_without_service_start"] += 1
                throughput_exclusions["completion_without_service_start"] += 1
            elif cancel is not None:
                validated_records += 1
                exclusions["left_before_service"] += 1
                throughput_exclusions["left_before_service"] += 1
            else:
                validated_records += 1
                censored += 1
                exclusions["right_censored_at_extraction"] += 1
                throughput_exclusions["right_censored_at_extraction"] += 1
            continue
        if start < check_in:
            exclusions["invalid_event_order"] += 1
            throughput_exclusions["invalid_event_order"] += 1
            continue
        if cancel is not None:
            if cancel == start:
                exclusions["invalid_event_order"] += 1
                throughput_exclusions["invalid_event_order"] += 1
                continue
            if cancel < start:
                validated_records += 1
                exclusions["left_before_service"] += 1
                throughput_exclusions["left_before_service"] += 1
                continue
        if complete is not None and complete < start:
            exclusions["invalid_event_order"] += 1
            throughput_exclusions["invalid_event_order"] += 1
            continue
        if start == check_in:
            wait = 0.0
        else:
            wait = (start - check_in).total_seconds() / 60
        if wait < 0 or not isfinite(wait):
            exclusions["invalid_negative_wait"] += 1
            throughput_exclusions["invalid_negative_wait"] += 1
            continue
        waits.append((record, wait))
        validated_records += 1
        if complete is None:
            throughput_exclusions["incomplete_service"] += 1
        else:
            completed.append(record)

    return ValidatedCohort(
        tuple(waits), tuple(completed), len(arrived_ids), censored, validated_records,
        dict(exclusions), dict(throughput_exclusions),
    )
