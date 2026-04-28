from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

DEFAULT_RIDE_LISTING_EVENTS_CHANNEL = "ride_listing_events"
RIDE_LISTING_CHANGED_EVENT_TYPE = "ride_listing_changed"


@dataclass(frozen=True, slots=True)
class RideListingChanged:
    ride_id: int
    event_type: str = RIDE_LISTING_CHANGED_EVENT_TYPE

    def __post_init__(self) -> None:
        if self.ride_id <= 0:
            raise ValueError("ride_id must be a positive integer")

    def to_payload(self) -> str:
        return json.dumps(
            {
                "event_type": self.event_type,
                "ride_id": self.ride_id,
            }
        )

    @classmethod
    def from_payload(cls, payload: str | bytes | dict[str, Any]) -> RideListingChanged:
        if isinstance(payload, bytes):
            payload = payload.decode()

        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload

        return cls(
            ride_id=int(data["ride_id"]),
            event_type=str(data.get("event_type", RIDE_LISTING_CHANGED_EVENT_TYPE)),
        )
