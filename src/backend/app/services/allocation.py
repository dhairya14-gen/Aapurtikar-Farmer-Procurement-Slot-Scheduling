"""Fail-closed, pure slot selection checks; never creates a reservation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class AllocationAuthorization:
    centre_verification_status: str
    participation_status: str
    crop_season_status: str
    operating_calendar_status: str
    capacity_status: str
    service_routing_status: str
    allocation_policy_status: str
    configuration_reference: str
    capacity_unit: str


@dataclass(frozen=True)
class SlotOffer:
    slot_id: str
    centre_id: str
    crop_code: str
    season_code: str
    service_stream_id: str
    starts_at: datetime
    ends_at: datetime
    capacity_limit: float
    capacity_unit: str
    reserved_capacity: float
    configuration_reference: str
    status: str


@dataclass(frozen=True)
class SlotSelectionRequest:
    centre_id: str
    crop_code: str
    season_code: str
    service_stream_id: str
    selected_slot_id: str | None
    requested_capacity: float


@dataclass(frozen=True)
class SlotSelectionDecision:
    status: str
    selected_slot_id: str | None
    feasible_slot_ids: tuple[str, ...]
    explanation: str


_REQUIRED_AUTHORIZATION = (
    "participation_status",
    "crop_season_status",
    "operating_calendar_status",
    "capacity_status",
    "service_routing_status",
    "allocation_policy_status",
)


def review_slot_options(
    request: SlotSelectionRequest,
    slots: Iterable[SlotOffer],
    authorization: AllocationAuthorization,
) -> SlotSelectionDecision:
    """Return feasible options or validate a user-selected option.

    Chronological ordering is for display only. This function does not rank by
    workload, reserve capacity, create a booking, or activate booking service.
    All configuration values are caller-supplied and must be authorized.
    """
    if authorization.centre_verification_status != "verified":
        return _unavailable("Centre verification is not complete.")
    if any(getattr(authorization, name) != "authorized" for name in _REQUIRED_AUTHORIZATION):
        return _unavailable("Required centre, crop, calendar, capacity, routing or policy authorization is incomplete.")
    if not authorization.configuration_reference.strip():
        return _unavailable("Authorized configuration provenance is required.")
    if not authorization.capacity_unit.strip():
        return _unavailable("An authorized capacity unit is required.")
    if not isfinite(request.requested_capacity) or request.requested_capacity <= 0:
        return _unavailable("Requested capacity must be explicitly supplied as a positive finite value.")

    feasible: list[SlotOffer] = []
    invalid_count = 0
    for slot in slots:
        times_valid = (
            slot.starts_at.tzinfo is not None
            and slot.starts_at.utcoffset() is not None
            and slot.ends_at.tzinfo is not None
            and slot.ends_at.utcoffset() is not None
            and slot.ends_at > slot.starts_at
        )
        valid_config = (
            slot.status == "authorized"
            and slot.configuration_reference.strip() == authorization.configuration_reference.strip()
            and isfinite(slot.capacity_limit) and slot.capacity_limit > 0
            and slot.capacity_unit.strip() == authorization.capacity_unit.strip()
            and isfinite(slot.reserved_capacity) and slot.reserved_capacity >= 0
            and bool(slot.service_stream_id)
        )
        matches_request = (
            slot.centre_id == request.centre_id
            and slot.crop_code == request.crop_code
            and slot.season_code == request.season_code
            and slot.service_stream_id == request.service_stream_id
        )
        if not times_valid or not valid_config:
            invalid_count += 1
            continue
        if matches_request and slot.reserved_capacity + request.requested_capacity <= slot.capacity_limit:
            feasible.append(slot)

    feasible.sort(key=lambda slot: (slot.starts_at, slot.slot_id))
    feasible_ids = tuple(slot.slot_id for slot in feasible)
    if request.selected_slot_id is None:
        if not feasible_ids:
            detail = "No authorized, matching slot option has unreserved capacity."
            if invalid_count:
                detail += f" {invalid_count} candidate slots had invalid configuration."
            return _unavailable(detail)
        return SlotSelectionDecision(
            "candidate_only",
            None,
            feasible_ids,
            "Feasible options for display only; no slot was selected or reserved.",
        )
    if request.selected_slot_id not in feasible_ids:
        return SlotSelectionDecision(
            "unavailable",
            None,
            feasible_ids,
            "Selected slot is unavailable, mismatched, or has no remaining configured capacity.",
        )
    return SlotSelectionDecision(
        "candidate_only",
        request.selected_slot_id,
        feasible_ids,
        "Selection is eligible for review only; no booking or reservation was created.",
    )


def _unavailable(explanation: str) -> SlotSelectionDecision:
    return SlotSelectionDecision("unavailable", None, (), explanation)
