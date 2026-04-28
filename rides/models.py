from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models

if TYPE_CHECKING:
    from locations.models import Location
    from users.models import User
    from vehicles.models import Vehicle


class Ride(models.Model):
    driver = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rides_as_driver")
    passenger = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rides_as_passenger")
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="rides")
    location_start = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="rides_start")
    location_end = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="rides_end")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        driver: User
        passenger: User
        vehicle: Vehicle
        location_start: Location
        location_end: Location

    def __str__(self) -> str:
        return f"{self.driver.get_full_name()} - {self.passenger.get_full_name()}"


class RideRequest(models.Model):
    ride = models.ForeignKey("Ride", on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="ride_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        ride: Ride
        user: User

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} - {self.ride.driver.get_full_name()}"


class RideListingRecord(models.Model):
    ride = models.OneToOneField("Ride", on_delete=models.CASCADE, related_name="listing_record")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    available_seats = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_methods = models.JSONField(default=list, blank=True)
    departure_time = models.TimeField()
    departure_date = models.DateField(null=True, blank=True)
    route_stops = models.JSONField(default=list, blank=True)
    driver_name = models.CharField(max_length=150)
    driver_rating = models.DecimalField(max_digits=3, decimal_places=2)
    driver_total_rides = models.PositiveIntegerField(default=0)  # pyright: ignore[reportArgumentType]
    driver_avatar = models.CharField(max_length=500, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_color = models.CharField(max_length=50, blank=True)
    restrictions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        ride: Ride
        origin: str
        destination: str
        available_seats: int
        price: Decimal
        payment_methods: list[str]
        departure_time: time
        departure_date: date | None
        route_stops: list[str]
        driver_name: str
        driver_rating: Decimal
        driver_total_rides: int
        driver_avatar: str
        vehicle_model: str
        vehicle_color: str
        restrictions: str

    class Meta:
        ordering = ["departure_date", "departure_time", "id"]

    @classmethod
    def build_for_ride(
        cls,
        *,
        ride: Ride,
        available_seats: int,
        price: Decimal,
        payment_methods: list[str] | tuple[str, ...],
        departure_time: time,
        departure_date: date | None,
        route_stops: list[str] | tuple[str, ...],
        driver_rating: Decimal,
        driver_total_rides: int,
        restrictions: str = "",
    ) -> RideListingRecord:
        record = cls(ride=ride)
        record.refresh_from_ride(
            available_seats=available_seats,
            price=price,
            payment_methods=payment_methods,
            departure_time=departure_time,
            departure_date=departure_date,
            route_stops=route_stops,
            driver_rating=driver_rating,
            driver_total_rides=driver_total_rides,
            restrictions=restrictions,
        )
        return record

    def clean(self) -> None:
        super().clean()
        self.payment_methods = _normalize_text_list(self.payment_methods, field_name="payment_methods")
        self.route_stops = _normalize_text_list(self.route_stops, field_name="route_stops")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def refresh_from_ride(
        self,
        *,
        available_seats: int,
        price: Decimal,
        payment_methods: list[str] | tuple[str, ...],
        departure_time: time,
        departure_date: date | None,
        route_stops: list[str] | tuple[str, ...],
        driver_rating: Decimal,
        driver_total_rides: int,
        restrictions: str = "",
    ) -> None:
        self.origin = self.ride.location_start.name
        self.destination = self.ride.location_end.name
        self.available_seats = available_seats
        self.price = price
        self.payment_methods = _normalize_text_list(payment_methods, field_name="payment_methods")
        self.departure_time = departure_time
        self.departure_date = departure_date
        self.route_stops = _normalize_text_list(route_stops, field_name="route_stops")
        self.driver_name = self.ride.driver.get_full_name()
        self.driver_rating = driver_rating
        self.driver_total_rides = driver_total_rides
        self.driver_avatar = _driver_avatar_path(self.ride.driver)
        self.vehicle_model = self.ride.vehicle.model
        self.vehicle_color = self.ride.vehicle.color
        self.restrictions = restrictions

    def __str__(self) -> str:
        return f"{self.origin} → {self.destination}"


def _normalize_text_list(value: object, *, field_name: str) -> list[str]:
    if isinstance(value, (list, tuple)):
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValidationError({field_name: "must contain only strings."})
            normalized.append(item)
        return normalized

    raise ValidationError({field_name: "must be a list of strings."})


def _driver_avatar_path(driver: User) -> str:
    profile_picture = driver.profile_picture
    if not profile_picture or not profile_picture.name:
        return ""
    return profile_picture.name
