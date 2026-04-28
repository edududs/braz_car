from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from ninja import NinjaAPI, Query, Schema

from src.brazcar.application.dto import RideListingsFilter
from src.brazcar.bootstrap.container import get_container
from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle

_DEFAULT_PRICE = Decimal("7.00")


class RideListingsQuerySchema(Schema):
    origin: str | None = None
    destination: str | None = None
    departure_date: date | None = None
    price: Decimal | None = None
    seats: int | None = None


class CurrentUserContextSchema(Schema):
    user_id: int | None = None
    is_authenticated: bool


class RideDriverSchema(Schema):
    name: str
    rating: str
    total_rides: int
    avatar: str | None = None


class RideVehicleSchema(Schema):
    model: str
    color: str


class RideListingSchema(Schema):
    ride_id: int
    origin: str
    destination: str
    available_seats: int
    price: str
    payment_methods: list[str]
    departure_time: str
    departure_date: str | None = None
    route_stops: list[str]
    driver: RideDriverSchema
    vehicle: RideVehicleSchema | None = None
    restrictions: str | None = None


api = NinjaAPI(title="BrazCar API", version="0.1.0")


@api.get("/ride-listings", response=list[RideListingSchema])
def list_ride_listings(request, filters: RideListingsQuerySchema = Query(...)) -> list[RideListingSchema]:
    listings = get_container().list_ride_listings().execute(
        RideListingsFilter(
            origin=filters.origin,
            destination=filters.destination,
            departure_date=filters.departure_date,
            price=filters.price,
            seats=filters.seats,
        )
    )
    return [_to_ride_listing_schema(listing) for listing in listings]


@api.get("/me", response=CurrentUserContextSchema)
def get_current_user_context_view(request) -> CurrentUserContextSchema:
    use_case = _resolve_current_user_use_case(request)
    context = use_case.execute()
    return CurrentUserContextSchema(
        user_id=context.user_id,
        is_authenticated=context.is_authenticated,
    )


def _resolve_current_user_use_case(request: Any) -> Any:
    getter = get_container().get_current_user_context
    try:
        return getter(request)
    except TypeError:
        return getter()


def _to_ride_listing_schema(listing: RideListing) -> RideListingSchema:
    return RideListingSchema(
        ride_id=listing.ride_id,
        origin=listing.origin,
        destination=listing.destination,
        available_seats=listing.available_seats,
        price=_format_decimal(getattr(listing, "price", None)),
        payment_methods=list(listing.payment_methods),
        departure_time=listing.departure_time.isoformat(),
        departure_date=listing.departure_date.isoformat() if listing.departure_date else None,
        route_stops=list(listing.route_stops),
        driver=_to_driver_schema(listing.driver),
        vehicle=_to_vehicle_schema(listing.vehicle),
        restrictions=listing.restrictions,
    )


def _to_driver_schema(driver: RideDriver) -> RideDriverSchema:
    return RideDriverSchema(
        name=driver.name,
        rating=_format_decimal(driver.rating),
        total_rides=driver.total_rides,
        avatar=driver.avatar,
    )


def _to_vehicle_schema(vehicle: RideVehicle | None) -> RideVehicleSchema | None:
    if vehicle is None:
        return None
    return RideVehicleSchema(model=vehicle.model, color=vehicle.color)


def _format_decimal(value: Decimal | None) -> str:
    return f"{(value if value is not None else _DEFAULT_PRICE):.2f}"
