from __future__ import annotations

from collections.abc import Sequence
from datetime import date, time
from decimal import Decimal

import pytest

from src.brazcar.application.dto import RideListingDetailQuery
from src.brazcar.application.use_cases.get_ride_listing_detail import (
    GetRideListingDetail,
    RideListingNotFoundError,
)
from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle


class FakeRideListingReader:
    def __init__(self, listings: Sequence[RideListing]) -> None:
        self._listings = tuple(listings)

    def list(self, filters: object) -> Sequence[RideListing]:
        return self._listings

    def get_by_ride_id(self, ride_id: int) -> RideListing | None:
        return next((listing for listing in self._listings if listing.ride_id == ride_id), None)



def test_get_ride_listing_detail_returns_matching_listing() -> None:
    expected_listing = build_listing(ride_id=7)
    use_case = GetRideListingDetail(reader=FakeRideListingReader([expected_listing]))

    result = use_case.execute(RideListingDetailQuery(ride_id=7))

    assert result == expected_listing



def test_get_ride_listing_detail_raises_when_listing_is_missing() -> None:
    use_case = GetRideListingDetail(reader=FakeRideListingReader([]))

    with pytest.raises(RideListingNotFoundError, match="7"):
        use_case.execute(RideListingDetailQuery(ride_id=7))



def build_listing(ride_id: int) -> RideListing:
    return RideListing(
        ride_id=ride_id,
        origin="Brazlândia",
        destination="Centro",
        available_seats=3,
        price=Decimal("7.00"),
        payment_methods=("Dinheiro", "PIX"),
        departure_time=time(19, 30),
        departure_date=date(2026, 4, 20),
        route_stops=("Esplanada",),
        driver=RideDriver(
            name="João Silva",
            rating=Decimal("4.5"),
            total_rides=127,
            avatar=None,
        ),
        vehicle=RideVehicle(model="Honda Civic", color="Branco"),
        restrictions=None,
    )
