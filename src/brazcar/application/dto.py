from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RideListingsFilter:
    origin: str | None = None
    destination: str | None = None
    departure_date: date | None = None
    price: Decimal | None = None
    seats: int | None = None


@dataclass(frozen=True, slots=True)
class RideListingDetailQuery:
    ride_id: int


@dataclass(frozen=True, slots=True)
class CurrentUserContext:
    user_id: int | None
    is_authenticated: bool
