"""Unmanaged first-come-first-served arrival ordering."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class QueueArrival:
    episode_id: str
    service_stream_id: str
    check_in_at: datetime | None
    server_sequence: int | None
    eligible: bool


@dataclass(frozen=True)
class FcfsOrder:
    order_by_stream: dict[str, tuple[str, ...]]
    excluded: dict[str, str]


def order_unmanaged_fcfs(arrivals: Iterable[QueueArrival]) -> FcfsOrder:
    """Order eligible genuine arrivals within each service stream.

    Primary order is recorded check-in. Equal timestamps use the server event
    sequence when available and then a stable episode key. Missing/naive times
    and ineligible arrivals are excluded with reasons; no service times are
    imputed or simulated.
    """
    by_stream: dict[str, list[QueueArrival]] = defaultdict(list)
    excluded: dict[str, str] = {}
    seen: set[str] = set()
    for arrival in arrivals:
        if arrival.episode_id in seen:
            excluded[arrival.episode_id] = "duplicate_episode"
            for stream_arrivals in by_stream.values():
                stream_arrivals[:] = [row for row in stream_arrivals if row.episode_id != arrival.episode_id]
            continue
        seen.add(arrival.episode_id)
        if not arrival.eligible:
            excluded[arrival.episode_id] = "ineligible"
        elif not arrival.service_stream_id:
            excluded[arrival.episode_id] = "missing_service_stream"
        elif arrival.check_in_at is None:
            excluded[arrival.episode_id] = "missing_check_in"
        elif arrival.check_in_at.tzinfo is None or arrival.check_in_at.utcoffset() is None:
            excluded[arrival.episode_id] = "invalid_timestamp_timezone"
        else:
            by_stream[arrival.service_stream_id].append(arrival)

    result: dict[str, tuple[str, ...]] = {}
    for stream_id, stream_arrivals in by_stream.items():
        stream_arrivals.sort(
            key=lambda row: (
                row.check_in_at,
                (0, row.server_sequence) if row.server_sequence is not None else (1, 0),
                row.episode_id,
            )
        )
        result[stream_id] = tuple(row.episode_id for row in stream_arrivals)
    return FcfsOrder(order_by_stream=result, excluded=excluded)
