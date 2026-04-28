from __future__ import annotations

from datetime import date, time
from decimal import Decimal

import pytest

from src.brazcar.application.dto import CurrentUserContext, RideListingsFilter
from src.brazcar.domain.ride_listing import RideDriver, RideListing, RideVehicle


class FakeListRideListings:
    def __init__(self, listings: tuple[RideListing, ...]) -> None:
        self._listings = listings
        self.seen_filters: list[RideListingsFilter] = []

    def execute(self, filters: RideListingsFilter) -> tuple[RideListing, ...]:
        self.seen_filters.append(filters)
        return self._listings


class FakeGetCurrentUserContext:
    def __init__(self, context: CurrentUserContext) -> None:
        self._context = context

    def execute(self) -> CurrentUserContext:
        return self._context


class FakeContainer:
    def __init__(
        self,
        *,
        list_use_case: FakeListRideListings,
        current_user_use_case: FakeGetCurrentUserContext,
    ) -> None:
        self._list_use_case = list_use_case
        self._current_user_use_case = current_user_use_case

    def list_ride_listings(self) -> FakeListRideListings:
        return self._list_use_case

    def get_current_user_context(self) -> FakeGetCurrentUserContext:
        return self._current_user_use_case


@pytest.fixture
def sample_listing() -> RideListing:
    return RideListing(
        ride_id=7,
        origin="Brazlândia",
        destination="Plano Piloto",
        available_seats=3,
        price=Decimal("8.50"),
        payment_methods=("PIX", "Dinheiro"),
        departure_time=time(19, 30),
        departure_date=date(2026, 4, 20),
        route_stops=("Taguatinga", "Eixo Monumental"),
        driver=RideDriver(
            name="João Silva",
            rating=Decimal("4.50"),
            total_rides=127,
            avatar=None,
        ),
        vehicle=RideVehicle(model="Honda Civic", color="Branco"),
        restrictions="Sem animais",
    )


@pytest.fixture
def fake_container(sample_listing: RideListing) -> FakeContainer:
    return FakeContainer(
        list_use_case=FakeListRideListings((sample_listing,)),
        current_user_use_case=FakeGetCurrentUserContext(
            CurrentUserContext(user_id=None, is_authenticated=False)
        ),
    )


@pytest.fixture(autouse=True)
def patch_http_container(monkeypatch: pytest.MonkeyPatch, fake_container: FakeContainer) -> None:
    monkeypatch.setattr(
        "src.brazcar.adapters.inbound.http.api_views.get_container",
        lambda: fake_container,
        raising=False,
    )
    monkeypatch.setattr(
        "src.brazcar.adapters.inbound.http.page_views.get_container",
        lambda: fake_container,
        raising=False,
    )


@pytest.mark.django_db
def test_root_route_renders_app_shell_with_runtime_endpoints(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="app-shell"' in response.content
    assert b'data-api-base-url="/api"' in response.content
    assert b'data-ride-listings-url="/api/ride-listings"' in response.content
    assert b'data-ride-listing-events-url="/events/ride-listings/"' in response.content
    assert b'data-current-user-url="/api/me"' in response.content
    assert b"frontend/src/main.tsx" in response.content
    assert b"static/js/main.js" not in response.content
    assert b"Dashboard bootstrap pronto." in response.content


@pytest.mark.django_db
def test_login_route_renders_login_page(client) -> None:
    response = client.get("/users/login/", {"next": "/rides/7/"})

    assert response.status_code == 200
    assert b"Entre na sua conta" in response.content


@pytest.mark.django_db
def test_login_failure_message_is_rendered_in_login_page(client) -> None:
    response = client.post(
        "/users/login/?next=/rides/7/",
        {"username": "inexistente", "password": "errada"},
        follow=True,
    )

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == "/users/login/"
    assert b"Usu\xc3\xa1rio ou senha incorretos." in response.content
    assert b"Entre na sua conta" in response.content


@pytest.mark.django_db
def test_list_ride_listings_api_serializes_domain_listing_and_filter_input(
    client,
    fake_container: FakeContainer,
) -> None:
    response = client.get(
        "/api/ride-listings",
        {
            "origin": "Brazlândia",
            "destination": "Plano Piloto",
            "departure_date": "2026-04-20",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "ride_id": 7,
            "origin": "Brazlândia",
            "destination": "Plano Piloto",
            "available_seats": 3,
            "price": "8.50",
            "payment_methods": ["PIX", "Dinheiro"],
            "departure_time": "19:30:00",
            "departure_date": "2026-04-20",
            "route_stops": ["Taguatinga", "Eixo Monumental"],
            "driver": {
                "name": "João Silva",
                "rating": "4.50",
                "total_rides": 127,
                "avatar": None
            },
            "vehicle": {
                "model": "Honda Civic",
                "color": "Branco"
            },
            "restrictions": "Sem animais"
        }
    ]
    assert fake_container.list_ride_listings().seen_filters == [
        RideListingsFilter(
            origin="Brazlândia",
            destination="Plano Piloto",
            departure_date=date(2026, 4, 20),
            price=None,
            seats=None,
        )
    ]


@pytest.mark.django_db
def test_logout_requires_post(client) -> None:
    response = client.get("/users/logout/")

    assert response.status_code == 405


@pytest.mark.django_db
def test_list_ride_listings_api_exposes_current_user_context(client) -> None:
    response = client.get("/api/me")

    assert response.status_code == 200
    assert response.json() == {"user_id": None, "is_authenticated": False}
