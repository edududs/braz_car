from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RideDriver:
    name: str
    rating: Decimal
    total_rides: int
    avatar: str | None

    def __post_init__(self) -> None:
        if self.total_rides < 0:
            raise ValueError("driver total rides cannot be negative")
        if self.rating < Decimal("0"):
            raise ValueError("driver rating cannot be negative")


@dataclass(frozen=True, slots=True)
class RideVehicle:
    model: str
    color: str


@dataclass(frozen=True, slots=True)
class RideListing:
    ride_id: int
    origin: str
    destination: str
    available_seats: int
    price: Decimal
    payment_methods: tuple[str, ...]
    departure_time: time
    departure_date: date | None
    route_stops: tuple[str, ...]
    driver: RideDriver
    vehicle: RideVehicle | None
    restrictions: str | None

    def __post_init__(self) -> None:
        if self.available_seats < 0:
            raise ValueError("available seats cannot be negative")
        if self.price < Decimal("0"):
            raise ValueError("price cannot be negative")

        object.__setattr__(self, "payment_methods", _normalize_text_items(self.payment_methods))
        object.__setattr__(self, "route_stops", _normalize_text_items(self.route_stops))


def _normalize_text_items(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())
