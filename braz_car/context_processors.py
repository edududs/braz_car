"""Context processors for BrazCar app"""

from datetime import date, time
from decimal import Decimal


def mock_rides_data(request):
    """Context processor that provides mock ride data for templates"""
    mock_rides = [
        {
            "origin": "Brazlândia",
            "destination": "Centro",
            "available_seats": 3,
            "price": Decimal("7.00"),
            "payment_methods": "Dinheiro ou PIX",
            "departure_time": time(19, 30),
            "departure_date": date.today(),
            "route_stops": ["Esplanada", "Eixo Monumental", "Estrutural"],
            "driver": {"name": "João Silva", "rating": 4.5, "total_rides": 127, "avatar": None},
            "vehicle": {"model": "Honda Civic", "color": "Branco"},
            "restrictions": "Não respondo perfil sem foto",
        },
        {
            "origin": "Brazlândia",
            "destination": "Aeroporto",
            "available_seats": 0,
            "price": Decimal("9.00"),
            "payment_methods": "Dinheiro ou PIX",
            "departure_time": time(18, 0),
            "departure_date": date.today(),
            "route_stops": ["Log Brasília", "Bombeiros", "Octogonal", "Estrutural", "Rodeador", "Veredas"],
            "driver": {"name": "Maria Santos", "rating": 4.8, "total_rides": 89, "avatar": None},
            "vehicle": {"model": "Toyota Corolla", "color": "Prata"},
            "restrictions": "Carona fixa (segunda a sexta-feira)",
        },
        {
            "origin": "Estrutural",
            "destination": "Asa Sul",
            "available_seats": 2,
            "price": Decimal("6.00"),
            "payment_methods": "PIX",
            "departure_time": time(7, 0),
            "departure_date": date.today(),
            "route_stops": ["Eixo Monumental", "Setor Policial", "Hospital Santa Lúcia"],
            "driver": {"name": "Carlos Oliveira", "rating": 4.2, "total_rides": 203, "avatar": None},
            "vehicle": {"model": "Volkswagen Voyage", "color": "Azul"},
            "restrictions": None,
        },
    ]

    return {
        "mock_rides": mock_rides,
        "featured_ride": mock_rides[0],  # First ride for the example
    }
