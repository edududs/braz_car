from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from rides.models import RideListingRecord
from src.brazcar.application.dto import RideListingsFilter
from src.brazcar.application.ports import RideListingReader
from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle


class PostgresRideRepository(RideListingReader):
    def list(self, filters: RideListingsFilter) -> Sequence[RideListing]:
        queryset = RideListingRecord.objects.select_related("ride").all()

        if filters.origin:
            queryset = queryset.filter(origin__icontains=filters.origin)
        if filters.destination:
            queryset = queryset.filter(destination__icontains=filters.destination)
        if filters.departure_date:
            queryset = queryset.filter(departure_date=filters.departure_date)
        if filters.price is not None:
            queryset = queryset.filter(price__lte=filters.price)
        if filters.seats is not None:
            queryset = queryset.filter(available_seats__gte=filters.seats)

        return tuple(self._to_domain(record) for record in queryset)

    def get_by_ride_id(self, ride_id: int) -> RideListing | None:
        record = (
            RideListingRecord.objects.select_related("ride")
            .filter(ride_id=ride_id)
            .first()
        )
        if record is None:
            return None
        return self._to_domain(record)

    def _to_domain(self, record: RideListingRecord) -> RideListing:
        return RideListing(
            ride_id=record.ride_id,
            origin=record.origin,
            destination=record.destination,
            available_seats=record.available_seats,
            price=Decimal(record.price),
            payment_methods=tuple(record.payment_methods),
            departure_time=record.departure_time,
            departure_date=record.departure_date,
            route_stops=tuple(record.route_stops),
            driver=RideDriver(
                name=record.driver_name,
                rating=Decimal(record.driver_rating),
                total_rides=record.driver_total_rides,
                avatar=record.driver_avatar or None,
            ),
            vehicle=self._to_vehicle(record),
            restrictions=record.restrictions or None,
        )

    def _to_vehicle(self, record: RideListingRecord) -> RideVehicle | None:
        if not record.vehicle_model or not record.vehicle_color:
            return None
        return RideVehicle(
            model=record.vehicle_model,
            color=record.vehicle_color,
        )
