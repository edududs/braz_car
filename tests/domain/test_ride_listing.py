from __future__ import annotations

from datetime import date, time
from decimal import Decimal

import pytest

from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle



def test_ride_listing_preserves_mvp_browse_fields() -> None:
    listing = RideListing(
        ride_id=42,
        origin="Brazlândia",
        destination="Centro",
        available_seats=3,
        price=Decimal("7.00"),
        payment_methods=("Dinheiro", "PIX"),
        departure_time=time(19, 30),
        departure_date=date(2026, 4, 20),
        route_stops=("Esplanada", "Eixo Monumental"),
        driver=RideDriver(
            name="João Silva",
            rating=Decimal("4.5"),
            total_rides=127,
            avatar=None,
        ),
        vehicle=RideVehicle(model="Honda Civic", color="Branco"),
        restrictions="Não respondo perfil sem foto",
    )

    assert listing.ride_id == 42
    assert listing.origin == "Brazlândia"
    assert listing.destination == "Centro"
    assert listing.available_seats == 3
    assert listing.price == Decimal("7.00")
    assert listing.payment_methods == ("Dinheiro", "PIX")
    assert listing.departure_time == time(19, 30)
    assert listing.departure_date == date(2026, 4, 20)
    assert listing.route_stops == ("Esplanada", "Eixo Monumental")
    assert listing.driver.name == "João Silva"
    assert listing.driver.rating == Decimal("4.5")
    assert listing.driver.total_rides == 127
    assert listing.driver.avatar is None
    assert listing.vehicle is not None
    assert listing.vehicle.model == "Honda Civic"
    assert listing.vehicle.color == "Branco"
    assert listing.restrictions == "Não respondo perfil sem foto"



def test_ride_listing_rejects_negative_available_seats() -> None:
    with pytest.raises(ValueError, match="available seats"):
        RideListing(
            ride_id=42,
            origin="Brazlândia",
            destination="Centro",
            available_seats=-1,
            price=Decimal("7.00"),
            payment_methods=("PIX",),
            departure_time=time(19, 30),
            departure_date=None,
            route_stops=(),
            driver=RideDriver(
                name="João Silva",
                rating=Decimal("4.5"),
                total_rides=127,
                avatar=None,
            ),
            vehicle=None,
            restrictions=None,
        )
