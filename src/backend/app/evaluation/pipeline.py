"""Evaluate authorized observed FCFS and slot-policy event records from CSV."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any

from app.services.baseline import QueueArrival, order_unmanaged_fcfs
from app.services.metrics import calculate_metrics
from app.services.types import EpisodeRecord, EvaluationScope

EVALUATION_PIPELINE_VERSION = "0.1.0"
POLICY_ARMS = ("fcfs", "slot_policy")
REQUIRED_COLUMNS = {
    "episode_id", "centre_id", "crop_code", "season_code", "policy_arm",
    "policy_version", "service_stream_id", "centre_configuration_reference",
    "service_assumptions_reference", "operating_period_id", "check_in_at",
    "service_stream_id", "comparison_block_id",
    "service_start_at", "service_complete_at", "cancelled_at", "no_show_declared_at",
    "no_show_confirmed", "check_in_sequence", "fairness_group",
    "deduplication_resolved", "correction_resolved", "provenance_valid", "eligible",
}
REQUIRED_SETTINGS = {
    "evaluation_id", "protocol_version", "comparison_design", "comparison_protocol_reference",
    "source_description", "source_reference", "permission_reference", "centre_id", "crop_code",
    "season_code", "period_start", "period_end", "extracted_at",
    "dataset_schema_version",
    "service_assumptions_reference", "scheduled_open_minutes_by_arm", "demand_equivalence_mode",
    "centre_configuration_reference", "policy_versions_by_arm",
    "fairness_groups_authorized", "fairness_group_authorization_reference",
    "fairness_minimum_group_observations", "no_show_policy_authorized",
    "no_show_policy_authorization_reference",
}


class EvaluationInputError(ValueError):
    """Raised when the supplied dataset/settings cannot be safely interpreted."""


@dataclass(frozen=True)
class EvaluationSettings:
    values: dict[str, Any]
    period_start: datetime
    period_end: datetime
    extracted_at: datetime


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise EvaluationInputError(f"{field} must be an ISO-8601 timestamp.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvaluationInputError(f"{field} must include a timezone offset.")
    return parsed


def load_settings(path: str | Path) -> EvaluationSettings:
    settings_path = Path(path)
    try:
        values = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationInputError(f"Could not read settings JSON: {exc}") from exc
    if not isinstance(values, dict):
        raise EvaluationInputError("Settings must be a JSON object.")
    missing = sorted(REQUIRED_SETTINGS - values.keys())
    if missing:
        raise EvaluationInputError(f"Settings are missing required keys: {', '.join(missing)}")
    for field in ("evaluation_id", "protocol_version", "comparison_design", "comparison_protocol_reference",
                  "source_description", "source_reference", "permission_reference", "centre_id", "crop_code",
                  "season_code", "service_assumptions_reference", "centre_configuration_reference",
                  "dataset_schema_version"):
        if not isinstance(values[field], str) or not values[field].strip():
            raise EvaluationInputError(f"Settings field {field!r} must be a non-empty string.")
    if values["demand_equivalence_mode"] != "exact_equal_arrival_counts_per_period":
        raise EvaluationInputError("Only exact_equal_arrival_counts_per_period is implemented; no adjustment model is assumed.")
    for field in ("fairness_groups_authorized", "no_show_policy_authorized"):
        if not isinstance(values[field], bool):
            raise EvaluationInputError(f"Settings field {field!r} must be true or false.")
    if values["fairness_groups_authorized"] and not str(values["fairness_group_authorization_reference"] or "").strip():
        raise EvaluationInputError("Authorized fairness grouping requires a provenance reference.")
    if values["no_show_policy_authorized"] and not str(values["no_show_policy_authorization_reference"] or "").strip():
        raise EvaluationInputError("Authorized no-show classification requires a policy reference.")
    open_minutes = values["scheduled_open_minutes_by_arm"]
    if not isinstance(open_minutes, dict) or set(open_minutes) != set(POLICY_ARMS):
        raise EvaluationInputError("scheduled_open_minutes_by_arm must explicitly contain fcfs and slot_policy.")
    for arm, minutes in open_minutes.items():
        if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not isfinite(minutes) or minutes <= 0:
            raise EvaluationInputError(f"Scheduled open minutes for {arm} must be a positive number.")
    policy_versions = values["policy_versions_by_arm"]
    if not isinstance(policy_versions, dict) or set(policy_versions) != set(POLICY_ARMS):
        raise EvaluationInputError("policy_versions_by_arm must explicitly contain fcfs and slot_policy.")
    if any(not isinstance(value, str) or not value.strip() for value in policy_versions.values()):
        raise EvaluationInputError("Each policy version must be a non-empty string.")
    if values["fairness_minimum_group_observations"] is not None:
        minimum = values["fairness_minimum_group_observations"]
        if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
            raise EvaluationInputError("fairness_minimum_group_observations must be null or a positive integer.")
    period_start = _parse_datetime(values["period_start"], "period_start")
    period_end = _parse_datetime(values["period_end"], "period_end")
    extracted_at = _parse_datetime(values["extracted_at"], "extracted_at")
    if period_end <= period_start:
        raise EvaluationInputError("period_end must be after period_start.")
    if extracted_at < period_end:
        raise EvaluationInputError("extracted_at must not precede period_end.")
    return EvaluationSettings(values, period_start, period_end, extracted_at)


def _parse_boolean(value: str, field: str, row_number: int) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise EvaluationInputError(f"Row {row_number}: {field} must be true or false.")


def _optional_timestamp(row: dict[str, str], field: str, row_number: int, errors: list[str]) -> datetime | None:
    value = row.get(field, "").strip()
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"invalid_timestamp_format:{field}")
        return None


def load_dataset(path: str | Path) -> list[EpisodeRecord]:
    dataset_path = Path(path)
    try:
        with dataset_path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            headers = set(reader.fieldnames or ())
            missing = sorted(REQUIRED_COLUMNS - headers)
            if missing:
                raise EvaluationInputError(f"Dataset is missing required columns: {', '.join(missing)}")
            records: list[EpisodeRecord] = []
            for row_number, row in enumerate(reader, start=2):
                errors: list[str] = []
                required_values = (
                    "episode_id", "centre_id", "crop_code", "season_code", "policy_arm",
                    "policy_version", "service_assumptions_reference", "centre_configuration_reference",
                    "operating_period_id", "comparison_block_id", "service_stream_id",
                )
                empty = [field for field in required_values if not row.get(field, "").strip()]
                if empty:
                    raise EvaluationInputError(f"Row {row_number}: required values missing: {', '.join(empty)}")
                if row["policy_arm"] not in POLICY_ARMS:
                    raise EvaluationInputError(f"Row {row_number}: policy_arm must be fcfs or slot_policy.")
                times = {
                    field: _optional_timestamp(row, field, row_number, errors)
                    for field in ("check_in_at", "service_start_at", "service_complete_at", "cancelled_at", "no_show_declared_at")
                }
                try:
                    sequence = int(row["check_in_sequence"]) if row["check_in_sequence"].strip() else None
                    if sequence is not None and sequence < 0:
                        errors.append("invalid_check_in_sequence")
                except ValueError:
                    sequence = None
                    errors.append("invalid_check_in_sequence")
                records.append(EpisodeRecord(
                    episode_id=row["episode_id"].strip(),
                    centre_id=row["centre_id"].strip(),
                    crop_code=row["crop_code"].strip(),
                    season_code=row["season_code"].strip(),
                    policy_arm=row["policy_arm"].strip(),
                    policy_version=row["policy_version"].strip(),
                    service_stream_id=row["service_stream_id"].strip(),
                    centre_configuration_reference=row["centre_configuration_reference"].strip(),
                    service_assumptions_reference=row["service_assumptions_reference"].strip(),
                    operating_period_id=row["operating_period_id"].strip(),
                    comparison_block_id=row["comparison_block_id"].strip(),
                    check_in_at=times["check_in_at"],
                    service_start_at=times["service_start_at"],
                    service_complete_at=times["service_complete_at"],
                    cancelled_at=times["cancelled_at"],
                    no_show_declared_at=times["no_show_declared_at"],
                    no_show_confirmed=_parse_boolean(row["no_show_confirmed"], "no_show_confirmed", row_number),
                    check_in_sequence=sequence,
                    fairness_group=row["fairness_group"].strip() or None,
                    deduplication_resolved=_parse_boolean(row["deduplication_resolved"], "deduplication_resolved", row_number),
                    correction_resolved=_parse_boolean(row["correction_resolved"], "correction_resolved", row_number),
                    provenance_valid=_parse_boolean(row["provenance_valid"], "provenance_valid", row_number),
                    eligible=_parse_boolean(row["eligible"], "eligible", row_number),
                    input_errors=tuple(errors),
                ))
    except OSError as exc:
        raise EvaluationInputError(f"Could not read input dataset: {exc}") from exc
    return records


def _is_valid_arrival(record: EpisodeRecord, settings: EvaluationSettings) -> bool:
    return (
        record.centre_id == settings.values["centre_id"]
        and record.crop_code == settings.values["crop_code"]
        and record.season_code == settings.values["season_code"]
        and record.service_assumptions_reference == settings.values["service_assumptions_reference"]
        and record.centre_configuration_reference == settings.values["centre_configuration_reference"]
        and record.policy_version == settings.values["policy_versions_by_arm"][record.policy_arm]
        and record.eligible and record.provenance_valid and record.deduplication_resolved
        and record.correction_resolved and not record.input_errors and record.check_in_at is not None
        and record.check_in_at.tzinfo is not None and record.check_in_at.utcoffset() is not None
        and settings.period_start <= record.check_in_at < settings.period_end
    )


def _comparison_gate(
    grouped: dict[str, list[EpisodeRecord]],
    arm_metrics: dict[str, dict[str, object]],
    settings: EvaluationSettings,
) -> tuple[str, list[str], dict[str, dict[str, int]], dict[str, dict[str, dict[str, int]]]]:
    reasons: list[str] = []
    arrivals_by_block: dict[str, dict[str, int]] = {arm: {} for arm in POLICY_ARMS}
    arrivals_by_block_stream: dict[str, dict[str, dict[str, int]]] = {arm: {} for arm in POLICY_ARMS}
    for arm in POLICY_ARMS:
        counts: Counter[str] = Counter()
        stream_counts: dict[str, Counter[str]] = defaultdict(Counter)
        for record in grouped[arm]:
            if _is_valid_arrival(record, settings):
                counts[record.comparison_block_id] += 1
                stream_counts[record.comparison_block_id][record.service_stream_id] += 1
        arrivals_by_block[arm] = dict(counts)
        arrivals_by_block_stream[arm] = {block: dict(streams) for block, streams in stream_counts.items()}
    if not grouped["fcfs"] or not grouped["slot_policy"]:
        reasons.append("Both policy arms require genuine event records.")
    fcfs_blocks = set(arrivals_by_block["fcfs"])
    slot_blocks = set(arrivals_by_block["slot_policy"])
    if not fcfs_blocks or fcfs_blocks != slot_blocks:
        reasons.append("Both arms must contain the same matched comparison-block identifiers.")
    elif any(arrivals_by_block["fcfs"][block] != arrivals_by_block["slot_policy"][block] for block in fcfs_blocks):
        reasons.append("Eligible arrival counts differ within one or more matched periods; no adjustment model is authorized.")
    if arrivals_by_block_stream["fcfs"] != arrivals_by_block_stream["slot_policy"]:
        reasons.append("Eligible arrivals differ by service stream within one or more comparison blocks.")
    open_minutes = settings.values["scheduled_open_minutes_by_arm"]
    if open_minutes["fcfs"] != open_minutes["slot_policy"]:
        reasons.append("Scheduled open minutes differ between arms.")
    if not arm_metrics["fcfs"]["total_wait"]["status"] == "available" or not arm_metrics["slot_policy"]["total_wait"]["status"] == "available":
        reasons.append("Both arms require valid observed wait records.")
    if arm_metrics["fcfs"]["censored_episodes"] != arm_metrics["slot_policy"]["censored_episodes"]:
        reasons.append("Right-censored visit counts differ; a total-wait comparison is incomplete under the approved rules.")
    if any(
        arm_metrics[arm]["exclusions"].get("service_assumptions_mismatch", 0)
        for arm in POLICY_ARMS
    ):
        reasons.append("Some records do not match the declared service-assumptions reference.")
    if any(
        arm_metrics[arm]["exclusions"].get(reason, 0)
        for arm in POLICY_ARMS
        for reason in ("centre_configuration_mismatch", "out_of_scope")
    ):
        reasons.append("Some records do not match the authorized centre configuration or evaluation scope.")
    timestamp_or_order_errors = ("invalid_timestamp_format", "invalid_timestamp_timezone", "invalid_event_order")
    if any(
        count
        for arm in POLICY_ARMS
        for key, count in arm_metrics[arm]["exclusions"].items()
        if key.startswith(timestamp_or_order_errors)
    ):
        reasons.append("Invalid timestamps or event ordering were found; demand equivalence cannot be established safely.")
    return ("available" if not reasons else "unavailable", reasons, arrivals_by_block, arrivals_by_block_stream)


def run_evaluation(dataset_path: str | Path, settings_path: str | Path) -> dict[str, object]:
    """Run observed-arm evaluation without simulation or data fabrication."""
    settings = load_settings(settings_path)
    records = load_dataset(dataset_path)
    grouped: dict[str, list[EpisodeRecord]] = {arm: [] for arm in POLICY_ARMS}
    for record in records:
        grouped[record.policy_arm].append(record)
    settings_values = settings.values
    arm_metrics: dict[str, dict[str, object]] = {}
    for arm in POLICY_ARMS:
        scope = EvaluationScope(
            centre_id=settings_values["centre_id"],
            crop_code=settings_values["crop_code"],
            season_code=settings_values["season_code"],
            policy_arm=arm,
            policy_version=settings_values["policy_versions_by_arm"][arm],
            centre_configuration_reference=settings_values["centre_configuration_reference"],
            period_start=settings.period_start,
            period_end=settings.period_end,
            extracted_at=settings.extracted_at,
            scheduled_open_minutes=float(settings_values["scheduled_open_minutes_by_arm"][arm]),
            fairness_groups_authorized=settings_values["fairness_groups_authorized"],
            fairness_minimum_group_observations=settings_values["fairness_minimum_group_observations"],
            service_assumptions_reference=settings_values["service_assumptions_reference"],
            no_show_policy_authorized=settings_values["no_show_policy_authorized"],
        )
        arm_metrics[arm] = calculate_metrics(grouped[arm], scope).to_dict()
    comparison_status, reasons, arrivals_by_period, arrivals_by_block_stream = _comparison_gate(grouped, arm_metrics, settings)
    difference = None
    if comparison_status == "available":
        difference = (
            arm_metrics["slot_policy"]["total_wait"]["value"]
            - arm_metrics["fcfs"]["total_wait"]["value"]
        )
    dataset_sha = hashlib.sha256(Path(dataset_path).read_bytes()).hexdigest()
    settings_sha = hashlib.sha256(Path(settings_path).read_bytes()).hexdigest()
    fcfs_arrivals = [
        QueueArrival(record.episode_id, record.service_stream_id, record.check_in_at,
                     record.check_in_sequence, record.eligible)
        for record in grouped["fcfs"]
    ]
    baseline_order = order_unmanaged_fcfs(fcfs_arrivals)
    return {
        "result_status": "measured_observed_data" if any(arm["validated_records"] for arm in arm_metrics.values()) else "unavailable_no_valid_records",
        "evaluation_mode": "observed_policy_arm_comparison",
        "synthetic_or_counterfactual_data_used": False,
        "comparison": {
            "status": comparison_status,
            "reasons": reasons,
            "total_wait_difference_slot_policy_minus_fcfs_person_minutes": difference,
            "interpretation": "Descriptive observed difference only; do not infer reduction or causality without the approved design and analysis.",
            "uncertainty_status": "not_computed; statistical method and adequacy criterion require protocol approval",
            "eligible_arrivals_by_comparison_block_and_arm": arrivals_by_period,
            "eligible_arrivals_by_comparison_block_and_service_stream": arrivals_by_block_stream,
            "fcfs_ordered_arrivals": sum(len(order) for order in baseline_order.order_by_stream.values()),
            "fcfs_excluded_arrivals": len(baseline_order.excluded),
        },
        "arms": arm_metrics,
        "scope_and_settings": settings_values,
        "input_provenance": {
            "dataset_path_label": Path(dataset_path).name,
            "dataset_sha256": dataset_sha,
            "settings_path_label": Path(settings_path).name,
            "settings_sha256": settings_sha,
            "source_description": settings_values["source_description"],
            "source_reference": settings_values["source_reference"],
            "permission_reference": settings_values["permission_reference"],
            "protocol_version": settings_values["protocol_version"],
        },
        "run_manifest": {
            "pipeline_version": EVALUATION_PIPELINE_VERSION,
            "python_version": platform.python_version(),
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
