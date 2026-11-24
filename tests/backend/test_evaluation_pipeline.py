"""Evaluation pipeline integration fixtures are TEST DATA only and use tmp_path."""

import csv
import json
from datetime import datetime, timedelta, timezone

import pytest

from app.evaluation.pipeline import EvaluationInputError, REQUIRED_COLUMNS, run_evaluation

UTC = timezone.utc


def fixture_settings() -> dict[str, object]:
    return {
        "evaluation_id": "TEST_DATA_EVALUATION",
        "protocol_version": "TEST_DATA_PROTOCOL_V1",
        "dataset_schema_version": "TEST_DATA_SCHEMA_V1",
        "comparison_design": "TEST_DATA_MATCHED_PERIODS",
        "comparison_protocol_reference": "TEST_DATA_PROTOCOL_REFERENCE",
        "source_description": "TEST DATA fixture; not an operational dataset",
        "source_reference": "TEST DATA only",
        "permission_reference": "TEST DATA fixture only",
        "centre_id": "TEST_DATA_CENTRE",
        "crop_code": "TEST_DATA_CROP",
        "season_code": "TEST_DATA_SEASON",
        "centre_configuration_reference": "TEST_DATA_CENTRE_CONFIG",
        "policy_versions_by_arm": {"fcfs": "TEST_DATA_POLICY_fcfs", "slot_policy": "TEST_DATA_POLICY_slot_policy"},
        "period_start": "2026-01-01T08:00:00+00:00",
        "period_end": "2026-01-01T12:00:00+00:00",
        "extracted_at": "2026-01-01T13:00:00+00:00",
        "service_assumptions_reference": "TEST_DATA_SERVICE_CONFIG",
        "scheduled_open_minutes_by_arm": {"fcfs": 240, "slot_policy": 240},
        "demand_equivalence_mode": "exact_equal_arrival_counts_per_period",
        "fairness_groups_authorized": False,
        "fairness_group_authorization_reference": "",
        "fairness_minimum_group_observations": None,
        "no_show_policy_authorized": False,
        "no_show_policy_authorization_reference": "",
    }


def fixture_row(episode: str, arm: str, period: str, block: str) -> dict[str, str]:
    start = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    check_in = start if arm == "fcfs" else start + timedelta(minutes=1)
    service_start = check_in + timedelta(minutes=10)
    service_complete = service_start + timedelta(minutes=15)
    return {
        "episode_id": episode,
        "centre_id": "TEST_DATA_CENTRE",
        "crop_code": "TEST_DATA_CROP",
        "season_code": "TEST_DATA_SEASON",
        "policy_arm": arm,
        "policy_version": f"TEST_DATA_POLICY_{arm}",
        "service_stream_id": "TEST_DATA_STREAM",
        "centre_configuration_reference": "TEST_DATA_CENTRE_CONFIG",
        "service_assumptions_reference": "TEST_DATA_SERVICE_CONFIG",
        "operating_period_id": period,
        "comparison_block_id": block,
        "check_in_at": check_in.isoformat(),
        "service_start_at": service_start.isoformat(),
        "service_complete_at": service_complete.isoformat(),
        "cancelled_at": "",
        "no_show_declared_at": "",
        "no_show_confirmed": "false",
        "check_in_sequence": "1",
        "fairness_group": "",
        "deduplication_resolved": "true",
        "correction_resolved": "true",
        "provenance_valid": "true",
        "eligible": "true",
    }


def write_test_inputs(tmp_path, rows: list[dict[str, str]]):
    csv_path = tmp_path / "TEST_DATA_events.csv"
    json_path = tmp_path / "TEST_DATA_settings.json"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(REQUIRED_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(fixture_settings()), encoding="utf-8")
    return csv_path, json_path


def test_pipeline_validates_and_compares_observed_arms_without_claims(tmp_path) -> None:
    dataset, settings = write_test_inputs(tmp_path, [
        fixture_row("TEST_DATA_FCFS_EPISODE", "fcfs", "TEST_SESSION_FCFS", "TEST_BLOCK_1"),
        fixture_row("TEST_DATA_SLOT_EPISODE", "slot_policy", "TEST_SESSION_SLOT", "TEST_BLOCK_1"),
    ])

    output = run_evaluation(dataset, settings)

    assert output["result_status"] == "measured_observed_data"
    assert output["synthetic_or_counterfactual_data_used"] is False
    assert output["comparison"]["status"] == "available"
    assert output["comparison"]["total_wait_difference_slot_policy_minus_fcfs_person_minutes"] == 0
    assert "do not infer reduction" in output["comparison"]["interpretation"]
    assert output["input_provenance"]["dataset_sha256"]


def test_pipeline_rejects_dataset_missing_required_columns(tmp_path) -> None:
    dataset = tmp_path / "TEST_DATA_incomplete.csv"
    settings = tmp_path / "TEST_DATA_settings.json"
    dataset.write_text("episode_id,policy_arm\nTEST_DATA_1,fcfs\n", encoding="utf-8")
    settings.write_text(json.dumps(fixture_settings()), encoding="utf-8")

    with pytest.raises(EvaluationInputError, match="missing required columns"):
        run_evaluation(dataset, settings)


def test_pipeline_marks_bad_timestamp_row_unavailable_for_comparison(tmp_path) -> None:
    fcfs = fixture_row("TEST_DATA_FCFS_EPISODE", "fcfs", "TEST_SESSION_FCFS", "TEST_BLOCK_1")
    slot = fixture_row("TEST_DATA_SLOT_EPISODE", "slot_policy", "TEST_SESSION_SLOT", "TEST_BLOCK_1")
    fcfs["check_in_at"] = "not-a-timestamp"
    dataset, settings = write_test_inputs(tmp_path, [fcfs, slot])

    output = run_evaluation(dataset, settings)

    assert output["arms"]["fcfs"]["mean_wait"]["status"] == "unavailable"
    assert output["comparison"]["status"] == "unavailable"
    assert any(key.startswith("invalid_timestamp_format") for key in output["arms"]["fcfs"]["exclusions"])
