from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class EventRecord:
    event: str
    created_at: str


events: list[EventRecord] = []


def track_event(event: str) -> EventRecord:
    record = EventRecord(event=event, created_at=datetime.now(timezone.utc).isoformat())
    events.append(record)
    return record


def get_all_events() -> list[EventRecord]:
    return events.copy()
