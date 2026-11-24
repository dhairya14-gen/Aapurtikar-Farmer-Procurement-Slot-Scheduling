"""All records and configurations in this module are TEST DATA only."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.services.allocation import (
    AllocationAuthorization,
    SlotOffer,
    SlotSelectionRequest,
    review_slot_options,
)
from app.services.baseline import QueueArrival, order_unmanaged_fcfs
from app.services.events import classify_episode_disposition, classify_late_arrival
from app.services.metrics import calculate_metrics
from app.services.types import EpisodeRecord, EvaluationScope

UTC = timezone.utc
PERIOD_START = datetime(2026, 1, 1, 8, tzinfo=UTC)
PERIOD_END = datetime(2026, 1, 1, 12, tzinfo=UTC)
EXTRACTED = datetime(2026, 1, 1, 13, tzinfo=UTC)


def make_test_record(
    episode_id: str = "TEST_DATA_1",
    *,
    arm: str = "fcfs",
    arrival: datetime | None = PERIOD_START,
    start: datetime | None = PERIOD_START + timedelta(minutes=20),
    complete: datetime | None = PERIOD_START + timedelta(minutes=35),
    group: str | None = None,
    **changes: object,
) -> EpisodeRecord:
    base = EpisodeRecord(
        episode_id=episode_id,
        centre_id="TEST_DATA_CENTRE",
        crop_code="TEST_DATA_CROP",
        season_code="TEST_DATA_SEASON",
        policy_arm=arm,
        policy_version=f"TEST_DATA_POLICY_{arm}",
        service_stream_id="TEST_DATA_STREAM",
        centre_configuration_reference="TEST_DATA_CENTRE_CONFIG",
        service_assumptions_reference="TEST_DATA_SERVICE_CONFIG",
        operating_period_id="TEST_DATA_PERIOD",
        comparison_block_id="TEST_DATA_BLOCK",
        check_in_at=arrival,
        service_start_at=start,
        service_complete_at=complete,
        cancelled_at=None,
        no_show_declared_at=None,
        no_show_confirmed=False,
        check_in_sequence=1,
        fairness_group=group,
        deduplication_resolved=True,
        correction_resolved=True,
        provenance_valid=True,
        eligible=True,
    )
    return replace(base, **changes)


def make_test_scope(**changes: object) -> EvaluationScope:
    values = dict(
        centre_id="TEST_DATA_CENTRE",
        crop_code="TEST_DATA_CROP",
        season_code="TEST_DATA_SEASON",
        policy_arm="fcfs",
        policy_version="TEST_DATA_POLICY_fcfs",
        centre_configuration_reference="TEST_DATA_CENTRE_CONFIG",
        period_start=PERIOD_START,
        period_end=PERIOD_END,
        extracted_at=EXTRACTED,
        scheduled_open_minutes=240.0,
        fairness_groups_authorized=False,
        fairness_minimum_group_observations=None,
        service_assumptions_reference="TEST_DATA_SERVICE_CONFIG",
        no_show_policy_authorized=False,
    )
    values.update(changes)
    return EvaluationScope(**values)


def test_fcfs_orders_arrivals_within_stream_and_excludes_missing_time() -> None:
    result = order_unmanaged_fcfs([
        QueueArrival("TEST_DATA_LATE", "TEST_STREAM", PERIOD_START + timedelta(minutes=5), 3, True),
        QueueArrival("TEST_DATA_EARLY", "TEST_STREAM", PERIOD_START, 1, True),
        QueueArrival("TEST_DATA_MISSING", "TEST_STREAM", None, 4, True),
    ])

    assert result.order_by_stream["TEST_STREAM"] == ("TEST_DATA_EARLY", "TEST_DATA_LATE")
    assert result.excluded == {"TEST_DATA_MISSING": "missing_check_in"}


def test_equal_arrival_times_use_server_sequence_then_stable_key() -> None:
    tied = PERIOD_START
    result = order_unmanaged_fcfs([
        QueueArrival("TEST_DATA_Z", "TEST_STREAM", tied, 2, True),
        QueueArrival("TEST_DATA_B", "TEST_STREAM", tied, 1, True),
        QueueArrival("TEST_DATA_A", "TEST_STREAM", tied, None, True),
    ])

    assert result.order_by_stream["TEST_STREAM"] == ("TEST_DATA_B", "TEST_DATA_Z", "TEST_DATA_A")


def test_slot_selection_is_only_a_candidate_and_fails_closed_without_authorization() -> None:
    authorization = AllocationAuthorization(
        centre_verification_status="verified",
        participation_status="authorized",
        crop_season_status="authorized",
        operating_calendar_status="authorized",
        capacity_status="authorized",
        service_routing_status="authorized",
        allocation_policy_status="authorized",
        configuration_reference="TEST_DATA_AUTH_REF",
        capacity_unit="TEST_DATA_VISIT_UNIT",
    )
    slot = SlotOffer(
        slot_id="TEST_DATA_SLOT",
        centre_id="TEST_DATA_CENTRE",
        crop_code="TEST_DATA_CROP",
        season_code="TEST_DATA_SEASON",
        service_stream_id="TEST_DATA_STREAM",
        starts_at=PERIOD_START + timedelta(minutes=30),
        ends_at=PERIOD_START + timedelta(minutes=60),
        capacity_limit=2,
        capacity_unit="TEST_DATA_VISIT_UNIT",
        reserved_capacity=1,
        configuration_reference="TEST_DATA_AUTH_REF",
        status="authorized",
    )
    request = SlotSelectionRequest(
        centre_id="TEST_DATA_CENTRE", crop_code="TEST_DATA_CROP", season_code="TEST_DATA_SEASON",
        service_stream_id="TEST_DATA_STREAM", selected_slot_id="TEST_DATA_SLOT",
        requested_capacity=1,
    )

    allowed = review_slot_options(request, [slot], authorization)
    blocked = review_slot_options(
        request, [slot], replace(authorization, participation_status="awaiting_authorization")
    )

    assert allowed.status == "candidate_only"
    assert allowed.selected_slot_id == "TEST_DATA_SLOT"
    assert "no booking" in allowed.explanation.lower()
    assert blocked.status == "unavailable"
    assert blocked.selected_slot_id is None
    full_slot = replace(slot, reserved_capacity=slot.capacity_limit)
    full = review_slot_options(request, [full_slot], authorization)
    assert full.status == "unavailable"
    assert "capacity" in full.explanation.lower()


def test_late_arrival_requires_explicit_authorized_policy_and_honors_boundary_input() -> None:
    cutoff = PERIOD_START + timedelta(minutes=30)
    awaiting = classify_late_arrival(
        check_in_at=cutoff + timedelta(seconds=1), authorized_cutoff_at=None,
        cutoff_is_inclusive=None, authorized_action=None, authorization_status="awaiting_authorization",
        authorization_reference=None,
    )
    late = classify_late_arrival(
        check_in_at=cutoff + timedelta(seconds=1), authorized_cutoff_at=cutoff,
        cutoff_is_inclusive=True, authorized_action="join_fcfs", authorization_status="authorized",
        authorization_reference="TEST_DATA_APPROVAL",
    )
    at_inclusive_cutoff = classify_late_arrival(
        check_in_at=cutoff, authorized_cutoff_at=cutoff,
        cutoff_is_inclusive=True, authorized_action="join_fcfs", authorization_status="authorized",
        authorization_reference="TEST_DATA_APPROVAL",
    )

    assert awaiting.status == "awaiting_authorization"
    assert late.is_late is True and late.authorized_action == "join_fcfs"
    assert at_inclusive_cutoff.is_late is False


def test_verified_no_show_requires_authorization_and_is_not_wait_or_throughput() -> None:
    kwargs = dict(
        check_in_at=None, service_start_at=None, service_complete_at=None, cancelled_at=None,
        no_show_declared_at=PERIOD_START, no_show_verified=True, extracted_at=EXTRACTED,
    )
    unauthorized = classify_episode_disposition(**kwargs, no_show_authorization_status="awaiting_authorization")
    authorized = classify_episode_disposition(**kwargs, no_show_authorization_status="authorized")

    assert unauthorized.status == "awaiting_authorization"
    assert authorized.status == "no_show"
    assert not authorized.contributes_wait and not authorized.contributes_throughput


def test_cancellation_no_show_censoring_and_incomplete_dispositions() -> None:
    cancelled_before_arrival = classify_episode_disposition(
        check_in_at=None, service_start_at=None, service_complete_at=None,
        cancelled_at=PERIOD_START, no_show_declared_at=None, no_show_verified=False,
        no_show_authorization_status="awaiting_authorization", extracted_at=EXTRACTED,
    )
    left_before_start = classify_episode_disposition(
        check_in_at=PERIOD_START, service_start_at=None, service_complete_at=None,
        cancelled_at=PERIOD_START + timedelta(minutes=3), no_show_declared_at=None,
        no_show_verified=False, no_show_authorization_status="awaiting_authorization", extracted_at=EXTRACTED,
    )
    pending_no_show = classify_episode_disposition(
        check_in_at=None, service_start_at=None, service_complete_at=None, cancelled_at=None,
        no_show_declared_at=PERIOD_START, no_show_verified=False,
        no_show_authorization_status="awaiting_authorization", extracted_at=EXTRACTED,
    )
    censored = classify_episode_disposition(
        check_in_at=PERIOD_START, service_start_at=None, service_complete_at=None, cancelled_at=None,
        no_show_declared_at=None, no_show_verified=False,
        no_show_authorization_status="awaiting_authorization", extracted_at=EXTRACTED,
    )
    incomplete = classify_episode_disposition(
        check_in_at=PERIOD_START, service_start_at=PERIOD_START + timedelta(minutes=4),
        service_complete_at=None, cancelled_at=None, no_show_declared_at=None, no_show_verified=False,
        no_show_authorization_status="awaiting_authorization", extracted_at=EXTRACTED,
    )

    assert cancelled_before_arrival.status == "cancelled_before_check_in"
    assert not cancelled_before_arrival.contributes_wait
    assert left_before_start.status == "left_before_service"
    assert pending_no_show.status == "pending_no_show"
    assert censored.status == "right_censored"
    assert incomplete.status == "served_incomplete"
    assert incomplete.contributes_wait and not incomplete.contributes_throughput


def test_missing_and_invalid_timestamps_make_wait_metrics_unavailable() -> None:
    missing = calculate_metrics([make_test_record("TEST_DATA_MISSING_TIME", start=None, complete=None)], make_test_scope())
    invalid = calculate_metrics([
        make_test_record("TEST_DATA_NAIVE_TIME", arrival=datetime(2026, 1, 1, 8), start=PERIOD_START)
    ], make_test_scope())

    assert missing.mean_wait.status == "unavailable"
    assert missing.censored_episodes == 1
    assert invalid.mean_wait.status == "unavailable"
    assert invalid.exclusions["invalid_timestamp_timezone"] == 1


def test_zero_valid_records_leave_all_metrics_unavailable() -> None:
    empty = calculate_metrics([], make_test_scope())

    assert empty.total_wait.status == "unavailable"
    assert empty.mean_wait.status == "unavailable"
    assert empty.worst_case_wait.status == "unavailable"
    assert empty.throughput.status == "unavailable"
    assert empty.fairness_spread.status == "unavailable"


def test_fairness_needs_authorized_groups_and_approved_adequacy() -> None:
    records = [make_test_record("TEST_DATA_GROUP_A", group="TEST_GROUP_A"),
               make_test_record("TEST_DATA_GROUP_B", group="TEST_GROUP_B")]
    unavailable = calculate_metrics(records, make_test_scope(
        fairness_groups_authorized=True, fairness_minimum_group_observations=None,
    ))
    insufficient = calculate_metrics(records, make_test_scope(
        fairness_groups_authorized=True, fairness_minimum_group_observations=2,
    ))

    assert unavailable.fairness_spread.status == "unavailable"
    assert "approved minimum" in unavailable.fairness_spread.explanation
    assert insufficient.fairness_spread.status == "unavailable"
    assert "do not meet" in insufficient.fairness_spread.explanation


def test_boundary_window_excludes_period_end_and_zero_wait_is_valid() -> None:
    at_start = make_test_record("TEST_DATA_ZERO_WAIT", arrival=PERIOD_START, start=PERIOD_START)
    at_end = make_test_record("TEST_DATA_END_BOUNDARY", arrival=PERIOD_END, start=PERIOD_END)
    result = calculate_metrics([at_start, at_end], make_test_scope())

    assert result.mean_wait.status == "available"
    assert result.mean_wait.value == 0
    assert result.mean_wait.valid_records == 1
    assert result.exclusions["outside_cohort_window"] == 1


def test_wait_metrics_are_independent_of_invalid_throughput_denominator() -> None:
    observed = calculate_metrics(
        [make_test_record("TEST_DATA_VALID_WAIT")],
        make_test_scope(scheduled_open_minutes=0),
    )

    assert observed.mean_wait.status == "available"
    assert observed.throughput.status == "unavailable"


def test_fairness_spread_reports_group_counts_when_authorized() -> None:
    group_a = make_test_record("TEST_DATA_GROUP_A", group="TEST_GROUP_A")
    group_b = make_test_record(
        "TEST_DATA_GROUP_B", group="TEST_GROUP_B", start=PERIOD_START + timedelta(minutes=35)
    )
    result = calculate_metrics(
        [group_a, group_b],
        make_test_scope(fairness_groups_authorized=True, fairness_minimum_group_observations=1),
    )

    assert result.fairness_spread.status == "available"
    assert result.fairness_spread.value == 15
    assert result.fairness_spread.details["group_counts"] == {"TEST_GROUP_A": 1, "TEST_GROUP_B": 1}
