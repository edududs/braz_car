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
            "payment_methods": ["Dinheiro", "PIX"],
            "departure_time": time(19, 30),
            "departure_date": date.today(),
            "route_stops": ["Esplanada", "Eixo Monumental", "Estrutural"],
            "driver_name": "João Silva",
            "driver_rating": 4.5,
            "driver_total_rides": 127,
            "driver_avatar": None,
            "vehicle_model": "Honda Civic",
            "vehicle_color": "Branco",
            "restrictions": "Não respondo perfil sem foto",
        },
        {
            "origin": "Brazlândia",
            "destination": "Aeroporto",
            "available_seats": 0,
            "price": Decimal("9.00"),
            "payment_methods": ["Dinheiro", "PIX"],
            "departure_time": time(18, 0),
            "departure_date": date.today(),
            "route_stops": ["Log Brasília", "Bombeiros", "Octogonal", "Estrutural", "Rodeador", "Veredas"],
            "driver_name": "Maria Santos",
            "driver_rating": 4.8,
            "driver_total_rides": 89,
            "driver_avatar": None,
            "vehicle_model": "Toyota Corolla",
            "vehicle_color": "Prata",
            "restrictions": "Carona fixa (segunda a sexta-feira)",
        },
        {
            "origin": "Estrutural",
            "destination": "Asa Sul",
            "available_seats": 2,
            "price": Decimal("6.00"),
            "payment_methods": ["PIX"],
            "departure_time": time(7, 0),
            "departure_date": date.today(),
            "route_stops": ["Eixo Monumental", "Setor Policial", "Hospital Santa Lúcia"],
            "driver_name": "Carlos Oliveira",
            "driver_rating": 4.2,
            "driver_total_rides": 203,
            "driver_avatar": None,
            "vehicle_model": "Volkswagen Voyage",
            "vehicle_color": "Azul",
            "restrictions": None,
        },
    ]

    return {
        "mock_rides": mock_rides,
        "featured_ride": mock_rides[0],  # First ride for the example
    }
