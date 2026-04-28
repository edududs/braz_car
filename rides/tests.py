from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings

from locations.models import Address, Location
from rides.admin import RideListingRecordAdmin
from rides.models import Ride, RideListingRecord
from vehicles.models import Vehicle


class RideListingRecordModelTests(SimpleTestCase):
    def test_payment_methods_uses_json_field_for_multi_value_contract(self) -> None:
        field = RideListingRecord._meta.get_field("payment_methods")

        assert isinstance(field, models.JSONField)
        assert field.default is list
        assert field.blank is True

    def test_clean_rejects_scalar_payment_methods_payload(self) -> None:
        record = RideListingRecord(payment_methods="PIX", route_stops=[])

        with self.assertRaisesMessage(ValidationError, "payment_methods"):
            record.clean()

    def test_clean_rejects_object_route_stops_payload(self) -> None:
        record = RideListingRecord(payment_methods=[], route_stops={"stop": "Esplanada"})

        with self.assertRaisesMessage(ValidationError, "route_stops"):
            record.clean()

    def test_clean_rejects_mixed_payment_methods_payload(self) -> None:
        record = RideListingRecord(payment_methods=["PIX", 2], route_stops=[])

        with self.assertRaisesMessage(ValidationError, "payment_methods"):
            record.clean()

    def test_clean_keeps_valid_list_payloads(self) -> None:
        record = RideListingRecord(payment_methods=["PIX", "Dinheiro"], route_stops=["Esplanada"])

        record.clean()

        assert record.payment_methods == ["PIX", "Dinheiro"]
        assert record.route_stops == ["Esplanada"]


@override_settings(MEDIA_ROOT="/tmp/brazcar-test-media")
class RideListingRecordPersistenceTests(TestCase):
    def setUp(self) -> None:
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
        self.origin = Location.objects.create(name="Brazlândia")
        self.destination = Location.objects.create(name="Centro")
        self.vehicle = Vehicle.objects.create(
            owner=self.driver,
            type="car",
            brand="Honda",
            model="Civic",
            year=2020,
            color="Branco",
            plate="ABC1234",
            capacity=4,
        )
        self.ride = Ride.objects.create(
            driver=self.driver,
            passenger=self.passenger,
            vehicle=self.vehicle,
            location_start=self.origin,
            location_end=self.destination,
        )

    def test_save_rejects_invalid_json_scalar_payload(self) -> None:
        record = RideListingRecord(
            ride=self.ride,
            origin="Brazlândia",
            destination="Centro",
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods="PIX",
            departure_time=time(19, 30),
            departure_date=date(2026, 4, 20),
            route_stops=["Esplanada"],
            driver_name="João Silva",
            driver_rating=Decimal("4.5"),
            driver_total_rides=127,
            driver_avatar="",
            vehicle_model="Civic",
            vehicle_color="Branco",
            restrictions="",
        )

        with self.assertRaisesMessage(ValidationError, "payment_methods"):
            record.save()

    def test_build_for_ride_populates_snapshot_from_ride(self) -> None:
        self.driver.profile_picture = SimpleUploadedFile(
            "avatar.jpg",
            b"filecontent",
            content_type="image/jpeg",
        )
        self.driver.save(update_fields=["profile_picture"])

        record = RideListingRecord.build_for_ride(
            ride=self.ride,
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods=["PIX", "Dinheiro"],
            departure_time=time(19, 30),
            departure_date=date(2026, 4, 20),
            route_stops=["Esplanada", "Eixo Monumental"],
            driver_rating=Decimal("4.50"),
            driver_total_rides=127,
            restrictions="Não respondo perfil sem foto",
        )

        assert record.ride == self.ride
        assert record.origin == "Brazlândia"
        assert record.destination == "Centro"
        assert record.payment_methods == ["PIX", "Dinheiro"]
        assert record.route_stops == ["Esplanada", "Eixo Monumental"]
        assert record.driver_name == "João Silva"
        assert record.vehicle_model == "Civic"
        assert record.vehicle_color == "Branco"
        assert record.driver_avatar == self.driver.profile_picture.name
        assert record.driver_avatar.startswith("profiles/")
        assert record.driver_avatar.endswith(".jpg")

    def test_build_for_ride_persists_uploaded_avatar_path(self) -> None:
        self.driver.profile_picture = SimpleUploadedFile(
            "avatar.jpg",
            b"filecontent",
            content_type="image/jpeg",
        )
        self.driver.save(update_fields=["profile_picture"])

        record = RideListingRecord.build_for_ride(
            ride=self.ride,
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods=["PIX"],
            departure_time=time(19, 30),
            departure_date=date(2026, 4, 20),
            route_stops=["Esplanada"],
            driver_rating=Decimal("4.50"),
            driver_total_rides=127,
        )

        record.save()
        persisted_record = RideListingRecord.objects.get(pk=record.pk)

        assert persisted_record.driver_avatar == self.driver.profile_picture.name
        assert persisted_record.driver_avatar.startswith("profiles/")
        assert persisted_record.driver_avatar.endswith(".jpg")

    def test_refresh_from_ride_updates_existing_snapshot(self) -> None:
        record = RideListingRecord.build_for_ride(
            ride=self.ride,
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods=["PIX"],
            departure_time=time(19, 30),
            departure_date=date(2026, 4, 20),
            route_stops=["Esplanada"],
            driver_rating=Decimal("4.50"),
            driver_total_rides=127,
        )

        self.origin.name = "Novo Terminal"
        self.origin.save(update_fields=["name"])
        self.vehicle.color = "Preto"
        self.vehicle.save(update_fields=["color"])

        record.refresh_from_ride(
            available_seats=1,
            price=Decimal("9.00"),
            payment_methods=["Dinheiro"],
            departure_time=time(20, 0),
            departure_date=None,
            route_stops=["Rodoviária"],
            driver_rating=Decimal("4.80"),
            driver_total_rides=130,
            restrictions="Somente ida",
        )

        assert record.origin == "Novo Terminal"
        assert record.vehicle_color == "Preto"
        assert record.available_seats == 1
        assert record.price == Decimal("9.00")
        assert record.payment_methods == ["Dinheiro"]
        assert record.route_stops == ["Rodoviária"]
        assert record.departure_time == time(20, 0)
        assert record.departure_date is None
        assert record.driver_rating == Decimal("4.80")
        assert record.driver_total_rides == 130
        assert record.restrictions == "Somente ida"

    def test_ride_card_template_renders_real_listing_record_shape(self) -> None:
        self.driver.profile_picture = SimpleUploadedFile(
            "avatar.jpg",
            b"filecontent",
            content_type="image/jpeg",
        )
        self.driver.save(update_fields=["profile_picture"])

        record = RideListingRecord.build_for_ride(
            ride=self.ride,
            available_seats=3,
            price=Decimal("7.00"),
            payment_methods=["PIX", "Dinheiro"],
            departure_time=time(19, 30),
            departure_date=date(2026, 4, 20),
            route_stops=["Esplanada", "Eixo Monumental"],
            driver_rating=Decimal("4.50"),
            driver_total_rides=127,
            restrictions="Não respondo perfil sem foto",
        )

        rendered = render_to_string(
            "components/ride_card.html",
            {"ride": record, "MEDIA_URL": "/media/"},
        )

        assert "Brazlândia → Centro" in rendered
        assert "PIX, Dinheiro" in rendered
        assert "João Silva" in rendered
        assert "127 viagens" in rendered
        assert "Civic - Branco" in rendered
        assert f'/media/{record.driver_avatar}' in rendered


class RideListingRecordAdminTests(SimpleTestCase):
    def setUp(self) -> None:
        self.admin = RideListingRecordAdmin(RideListingRecord, AdminSite())

    def test_admin_disables_manual_snapshot_changes(self) -> None:
        request = object()

        assert self.admin.has_add_permission(request) is False
        assert self.admin.has_change_permission(request) is False
        assert self.admin.has_delete_permission(request) is False

    def test_admin_marks_snapshot_fields_read_only(self) -> None:
        expected_fields = {
            "ride",
            "origin",
            "destination",
            "available_seats",
            "price",
            "payment_methods",
            "departure_time",
            "departure_date",
            "route_stops",
            "driver_name",
            "driver_rating",
            "driver_total_rides",
            "driver_avatar",
            "vehicle_model",
            "vehicle_color",
            "restrictions",
            "created_at",
            "updated_at",
        }

        assert set(self.admin.readonly_fields) == expected_fields
