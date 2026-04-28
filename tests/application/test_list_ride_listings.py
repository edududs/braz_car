from __future__ import annotations

from collections.abc import Sequence
from datetime import date, time
from decimal import Decimal

from src.brazcar.application.dto import CurrentUserContext, RideListingsFilter
from src.brazcar.application.use_cases.get_current_user_context import GetCurrentUserContext
from src.brazcar.application.use_cases.list_ride_listings import ListRideListings
from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle


class FakeRideListingReader:
    def __init__(self, listings: Sequence[RideListing]) -> None:
        self._listings = tuple(listings)
        self.seen_filters: list[RideListingsFilter] = []

    def list(self, filters: RideListingsFilter) -> Sequence[RideListing]:
        self.seen_filters.append(filters)
        return self._listings

    def get_by_ride_id(self, ride_id: int) -> RideListing | None:
        return next((listing for listing in self._listings if listing.ride_id == ride_id), None)


class FakeCurrentUserContextProvider:
    def __init__(self, context: CurrentUserContext) -> None:
        self._context = context

    def get_current_user_context(self) -> CurrentUserContext:
        return self._context



def test_list_ride_listings_delegates_filter_to_reader() -> None:
    reader = FakeRideListingReader([build_listing(ride_id=7)])
    use_case = ListRideListings(reader=reader)
    filters = RideListingsFilter(origin="Brazlândia", destination="Centro", departure_date=date(2026, 4, 20))

    result = use_case.execute(filters)

    assert result == (build_listing(ride_id=7),)
    assert reader.seen_filters == [filters]



def test_get_current_user_context_returns_provider_value() -> None:
    provider = FakeCurrentUserContextProvider(
        CurrentUserContext(user_id=99, is_authenticated=True)
    )
    use_case = GetCurrentUserContext(provider=provider)

    result = use_case.execute()

    assert result == CurrentUserContext(user_id=99, is_authenticated=True)



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
