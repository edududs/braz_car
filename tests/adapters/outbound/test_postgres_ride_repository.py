from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from locations.models import Address, Location
from rides.models import Ride, RideListingRecord
from src.brazcar.application.dto import RideListingsFilter
from src.brazcar.adapters.outbound.postgres_ride_repository import PostgresRideRepository
from vehicles.models import Vehicle


class PostgresRideRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.repository = PostgresRideRepository()
        self.address = Address.objects.create(
            neighborhood="Centro",
            street="Rua A",
            number="10",
            complement="Casa",
            zip_code="70000-000",
        )
        user_model = get_user_model()
        self.driver = user_model.objects.create_user(
            username="driver",
            password="senha-segura",
            first_name="João",
            last_name="Silva",
            email="driver@example.com",
            cpf="12345678901",
            phone="61999999999",
            birth_date=date(1990, 1, 1),
            address=self.address,
        )
        self.passenger = user_model.objects.create_user(
            username="passenger",
            password="senha-segura",
            first_name="Maria",
            last_name="Souza",
            email="passenger@example.com",
            cpf="10987654321",
            phone="61888888888",
            birth_date=date(1992, 2, 2),
            address=self.address,
        )
        self._sequence = 0

    def test_list_returns_domain_snapshots_filtered_by_origin_destination_and_departure_date(self) -> None:
        matching = self._create_listing_record(
            origin_name="Brazlândia",
            destination_name="Centro",
            departure_date_value=date(2026, 4, 20),
            payment_methods=["PIX", "Dinheiro"],
            route_stops=["Esplanada"],
            restrictions="Não fumo",
        )
        self._create_listing_record(
            origin_name="Ceilândia",
            destination_name="Centro",
            departure_date_value=date(2026, 4, 20),
        )
        self._create_listing_record(
            origin_name="Brazlândia",
            destination_name="Aeroporto",
            departure_date_value=date(2026, 4, 21),
        )

        listings = self.repository.list(
            RideListingsFilter(
                origin="Brazlândia",
                destination="Centro",
                departure_date=date(2026, 4, 20),
            )
        )

        assert len(listings) == 1
        listing = listings[0]
        assert listing.ride_id == matching.ride_id
        assert listing.origin == "Brazlândia"
        assert listing.destination == "Centro"
        assert listing.available_seats == 3
        assert listing.price == Decimal("7.00")
        assert listing.payment_methods == ("PIX", "Dinheiro")
        assert listing.departure_time == time(19, 30)
        assert listing.departure_date == date(2026, 4, 20)
        assert listing.route_stops == ("Esplanada",)
        assert listing.driver.name == "João Silva"
        assert listing.driver.rating == Decimal("4.50")
        assert listing.driver.total_rides == 127
        assert listing.driver.avatar is None
        assert listing.vehicle is not None
        assert listing.vehicle.model == "Civic 1"
        assert listing.vehicle.color == "Branco"
        assert listing.restrictions == "Não fumo"

    def test_get_by_ride_id_returns_none_when_snapshot_does_not_exist(self) -> None:
        assert self.repository.get_by_ride_id(99999) is None

    def test_get_by_ride_id_maps_blank_optional_snapshot_fields_to_none(self) -> None:
        record = self._create_listing_record(
            origin_name="Brazlândia",
            destination_name="Centro",
            departure_date_value=date(2026, 4, 20),
        )
        record.driver_avatar = ""
        record.vehicle_model = ""
        record.vehicle_color = ""
        record.restrictions = ""
        record.save(update_fields=["driver_avatar", "vehicle_model", "vehicle_color", "restrictions"])

        listing = self.repository.get_by_ride_id(record.ride_id)

        assert listing is not None
        assert listing.driver.avatar is None
        assert listing.vehicle is None
        assert listing.restrictions is None

    def test_get_by_ride_id_maps_partial_vehicle_snapshot_to_none(self) -> None:
        record = self._create_listing_record(
            origin_name="Brazlândia",
            destination_name="Centro",
            departure_date_value=date(2026, 4, 20),
        )
        record.vehicle_model = ""
        record.vehicle_color = "Branco"
        record.save(update_fields=["vehicle_model", "vehicle_color"])

        listing = self.repository.get_by_ride_id(record.ride_id)

        assert listing is not None
        assert listing.vehicle is None

    def _create_listing_record(
        self,
        *,
        origin_name: str,
        destination_name: str,
        departure_date_value: date | None,
        payment_methods: list[str] | None = None,
        route_stops: list[str] | None = None,
        restrictions: str = "",
    ) -> RideListingRecord:
        self._sequence += 1
        origin = Location.objects.create(name=origin_name)
        destination = Location.objects.create(name=destination_name)
        vehicle = Vehicle.objects.create(
            owner=self.driver,
            type="car",
            brand="Honda",
            model=f"Civic {self._sequence}",
            year=2020,
            color="Branco",
            plate=f"ABC{self._sequence:04d}",
            capacity=4,
        )
        ride = Ride.objects.create(
            driver=self.driver,
            passenger=self.passenger,
            vehicle=vehicle,
            location_start=origin,
            location_end=destination,
        )
        record = RideListingRecord.build_for_ride(
            ride=ride,
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods=payment_methods or ["PIX"],
            departure_time=time(19, 30),
            departure_date=departure_date_value,
            route_stops=route_stops or [],
            driver_rating=Decimal("4.50"),
            driver_total_rides=127,
            restrictions=restrictions,
        )
        record.save()
        return record
