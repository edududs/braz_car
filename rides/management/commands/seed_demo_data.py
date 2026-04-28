from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from locations.models import Address, Location
from rides.models import Ride, RideListingRecord
from vehicles.models import Vehicle


class Command(BaseCommand):
    help = "Populate BrazCar with demo data for local testing"

    def handle(self, *args, **options):
        user_model = get_user_model()

        address, _ = Address.objects.get_or_create(
            neighborhood="Brazlândia",
            street="Rua Central",
            number="100",
            complement="Casa",
            zip_code="72700-000",
        )

        driver_specs = [
            {
                "username": "joao.driver",
                "first_name": "João",
                "last_name": "Silva",
                "email": "joao@example.com",
                "cpf": "12345678909",
                "phone": "61999990001",
                "birth_date": date(1990, 5, 10),
            },
            {
                "username": "maria.driver",
                "first_name": "Maria",
                "last_name": "Souza",
                "email": "maria@example.com",
                "cpf": "98765432100",
                "phone": "61999990002",
                "birth_date": date(1992, 8, 20),
            },
            {
                "username": "carlos.driver",
                "first_name": "Carlos",
                "last_name": "Oliveira",
                "email": "carlos@example.com",
                "cpf": "11144477735",
                "phone": "61999990003",
                "birth_date": date(1988, 3, 15),
            },
        ]

        drivers = []
        for spec in driver_specs:
            user, created = user_model.objects.get_or_create(
                username=spec["username"],
                defaults={
                    **spec,
                    "address": address,
                    "is_verified": True,
                },
            )
            if created:
                user.set_password("demo123456")
                user.save(update_fields=["password"])
            drivers.append(user)

        passenger, created = user_model.objects.get_or_create(
            username="passageiro.demo",
            defaults={
                "first_name": "Paula",
                "last_name": "Demo",
                "email": "paula@example.com",
                "cpf": "93541134780",
                "phone": "61999990004",
                "birth_date": date(1995, 1, 1),
                "address": address,
                "is_verified": True,
            },
        )
        if created:
            passenger.set_password("demo123456")
            passenger.save(update_fields=["password"])

        origin, _ = Location.objects.get_or_create(name="Brazlândia", defaults={"city": "Brasília", "state": "DF"})
        centro, _ = Location.objects.get_or_create(name="Plano Piloto", defaults={"city": "Brasília", "state": "DF"})
        aeroporto, _ = Location.objects.get_or_create(name="Aeroporto", defaults={"city": "Brasília", "state": "DF"})
        asa_sul, _ = Location.objects.get_or_create(name="Asa Sul", defaults={"city": "Brasília", "state": "DF"})

        vehicle_specs = [
            (drivers[0], "Honda", "Civic", "Branco", "BRA2C34"),
            (drivers[1], "Toyota", "Corolla", "Prata", "BRA5D67"),
            (drivers[2], "Volkswagen", "Voyage", "Azul", "BRA8F90"),
        ]

        vehicles = []
        for owner, brand, model, color, plate in vehicle_specs:
            vehicle, _ = Vehicle.objects.get_or_create(
                plate=plate,
                defaults={
                    "owner": owner,
                    "type": "car",
                    "brand": brand,
                    "model": model,
                    "year": 2020,
                    "color": color,
                    "capacity": 4,
                },
            )
            vehicles.append(vehicle)

        ride_specs = [
            {
                "driver": drivers[0],
                "vehicle": vehicles[0],
                "destination": centro,
                "available_seats": 3,
                "price": Decimal("7.00"),
                "payment_methods": ["Dinheiro", "PIX"],
                "departure_time": time(19, 30),
                "departure_date": date.today(),
                "route_stops": ["Taguatinga", "Eixo Monumental"],
                "driver_rating": Decimal("4.50"),
                "driver_total_rides": 127,
                "restrictions": "Não respondo perfil sem foto",
            },
            {
                "driver": drivers[1],
                "vehicle": vehicles[1],
                "destination": aeroporto,
                "available_seats": 2,
                "price": Decimal("9.00"),
                "payment_methods": ["PIX"],
                "departure_time": time(18, 0),
                "departure_date": date.today(),
                "route_stops": ["Taguatinga", "EPIA"],
                "driver_rating": Decimal("4.80"),
                "driver_total_rides": 89,
                "restrictions": "Carona fixa (segunda a sexta)",
            },
            {
                "driver": drivers[2],
                "vehicle": vehicles[2],
                "destination": asa_sul,
                "available_seats": 1,
                "price": Decimal("7.00"),
                "payment_methods": ["Dinheiro", "PIX"],
                "departure_time": time(7, 0),
                "departure_date": date.today(),
                "route_stops": ["Setor Policial", "Hospital Santa Lúcia"],
                "driver_rating": Decimal("4.20"),
                "driver_total_rides": 203,
                "restrictions": "Sem bagagem grande",
            },
        ]

        created_count = 0
        for spec in ride_specs:
            ride, ride_created = Ride.objects.get_or_create(
                driver=spec["driver"],
                passenger=passenger,
                vehicle=spec["vehicle"],
                location_start=origin,
                location_end=spec["destination"],
            )
            listing, listing_created = RideListingRecord.objects.get_or_create(
                ride=ride,
                defaults={
                    "origin": origin.name,
                    "destination": spec["destination"].name,
                    "available_seats": spec["available_seats"],
                    "price": spec["price"],
                    "payment_methods": spec["payment_methods"],
                    "departure_time": spec["departure_time"],
                    "departure_date": spec["departure_date"],
                    "route_stops": spec["route_stops"],
                    "driver_name": spec["driver"].get_full_name(),
                    "driver_rating": spec["driver_rating"],
                    "driver_total_rides": spec["driver_total_rides"],
                    "driver_avatar": "",
                    "vehicle_model": spec["vehicle"].model,
                    "vehicle_color": spec["vehicle"].color,
                    "restrictions": spec["restrictions"],
                },
            )
            if not listing_created:
                listing.refresh_from_ride(
                    available_seats=spec["available_seats"],
                    price=spec["price"],
                    payment_methods=spec["payment_methods"],
                    departure_time=spec["departure_time"],
                    departure_date=spec["departure_date"],
                    route_stops=spec["route_stops"],
                    driver_rating=spec["driver_rating"],
                    driver_total_rides=spec["driver_total_rides"],
                    restrictions=spec["restrictions"],
                )
                listing.save()
            if ride_created or listing_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Demo data ready. New records touched: {created_count}"))
        self.stdout.write("Users: joao.driver, maria.driver, carlos.driver, passageiro.demo")
        self.stdout.write("Password for demo users: demo123456")
