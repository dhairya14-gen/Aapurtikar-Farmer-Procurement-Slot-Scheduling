"""Pure event classification for late arrivals, cancellations and no-shows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

LateAction = Literal["retain_slot", "join_fcfs", "reject", "reschedule"]


@dataclass(frozen=True)
class LateArrivalDecision:
    status: str
    is_late: bool | None
    authorized_action: str | None
    explanation: str


@dataclass(frozen=True)
class EpisodeDisposition:
    status: str
    contributes_wait: bool
    contributes_throughput: bool
    explanation: str


def classify_late_arrival(
    *,
    check_in_at: datetime,
    authorized_cutoff_at: datetime | None,
    cutoff_is_inclusive: bool | None,
    authorized_action: LateAction | None,
    authorization_status: str,
    authorization_reference: str | None,
) -> LateArrivalDecision:
    """Classify lateness only with a complete, explicitly authorized rule.

    No late policy is selected here. The cutoff boundary convention, action and
    authorization provenance are explicit caller inputs.
    """
    if (
        authorization_status != "authorized"
        or not authorization_reference
        or authorized_cutoff_at is None
        or cutoff_is_inclusive is None
        or authorized_action is None
    ):
        return LateArrivalDecision(
            "awaiting_authorization", None, None,
            "Late-arrival cutoff, boundary rule, action and authorization reference are required.",
        )
    if not _aware(check_in_at) or not _aware(authorized_cutoff_at):
        return LateArrivalDecision("invalid", None, None, "Arrival and cutoff timestamps must include timezone offsets.")
    if cutoff_is_inclusive:
        late = check_in_at > authorized_cutoff_at
    else:
        late = check_in_at >= authorized_cutoff_at
    return LateArrivalDecision(
        "classified",
        late,
        authorized_action if late else None,
        "Classification only; this function does not change a reservation or queue position.",
    )


def classify_episode_disposition(
    *,
    check_in_at: datetime | None,
    service_start_at: datetime | None,
    service_complete_at: datetime | None,
    cancelled_at: datetime | None,
    no_show_declared_at: datetime | None,
    no_show_verified: bool,
    no_show_authorization_status: str,
    extracted_at: datetime,
) -> EpisodeDisposition:
    """Classify event completeness without imputing timestamps or outcomes."""
    timestamps = (check_in_at, service_start_at, service_complete_at, cancelled_at, no_show_declared_at, extracted_at)
    if any(value is not None and not _aware(value) for value in timestamps):
        return _disposition("invalid", False, False, "All supplied event timestamps must include timezone offsets.")
    if not _aware(extracted_at):
        return _disposition("invalid", False, False, "Extraction timestamp must include a timezone offset.")
    if any(value is not None and value > extracted_at for value in timestamps[:-1]):
        return _disposition("invalid", False, False, "An event timestamp occurs after the declared extraction time.")
    if no_show_verified and (no_show_declared_at is None or no_show_authorization_status != "authorized"):
        return _disposition("awaiting_authorization", False, False, "A verified no-show requires a declared event and authorized cutoff policy.")
    if no_show_declared_at is not None and check_in_at is None:
        if no_show_verified:
            return _disposition("no_show", False, False, "Verified no-show; excluded from on-site wait and completed throughput.")
        return _disposition("pending_no_show", False, False, "No-show is not verified under an authorized policy.")
    if no_show_declared_at is not None and check_in_at is not None:
        return _disposition("invalid", False, False, "A no-show declaration conflicts with a recorded check-in.")
    if cancelled_at is not None and check_in_at is None:
        if service_start_at is not None or service_complete_at is not None:
            return _disposition("invalid", False, False, "Service events conflict with cancellation before check-in.")
        return _disposition("cancelled_before_check_in", False, False, "Pre-check-in cancellation; report separately from wait metrics.")
    if check_in_at is None:
        return _disposition("incomplete", False, False, "A valid check-in event is required for wait measurement.")
    if cancelled_at is not None and cancelled_at <= check_in_at:
        return _disposition("invalid", False, False, "Cancellation is not demonstrably after check-in.")
    if service_complete_at is not None and service_start_at is None:
        return _disposition("invalid", False, False, "Completion exists without a service-start event.")
    if service_start_at is None:
        if cancelled_at is not None:
            return _disposition("left_before_service", False, False, "Post-check-in departure before service is not a served wait.")
        return _disposition("right_censored", False, False, "Checked-in visit has no service start at extraction; follow-up is required.")
    if service_start_at < check_in_at:
        return _disposition("invalid", False, False, "Service start precedes check-in.")
    if cancelled_at == service_start_at and cancelled_at is not None:
        return _disposition("invalid", False, False, "Cancellation and service start tie without an approved event-order rule.")
    if cancelled_at is not None and cancelled_at < service_start_at:
        return _disposition("left_before_service", False, False, "Departure was recorded before service started.")
    if service_complete_at is not None and service_complete_at < service_start_at:
        return _disposition("invalid", False, False, "Service completion precedes service start.")
    if service_complete_at is None:
        return _disposition("served_incomplete", True, False, "Wait is measurable; missing completion excludes this episode from throughput.")
    return _disposition("completed", True, True, "Valid served and completed episode.")


def _aware(value: datetime | None) -> bool:
    return value is not None and value.tzinfo is not None and value.utcoffset() is not None


def _disposition(status: str, wait: bool, throughput: bool, explanation: str) -> EpisodeDisposition:
    return EpisodeDisposition(status, wait, throughput, explanation)
