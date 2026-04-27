# BrazCar MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild BrazCar as a Django 6 + React + SSE ride discovery MVP that reads from Supabase Postgres, updates live via Postgres `LISTEN/NOTIFY`, and ships as a single Render-ready container.

**Architecture:** Keep Django as the host application and auth/session boundary, move product logic into a new hexagonal `src/brazcar/` package, expose JSON + SSE endpoints for a React frontend, and use a Postgres listener plus an internal stream hub to push ride updates to connected clients. Preserve one deployable service and defer WebSockets/Channels until after the MVP proves out.

**Tech Stack:** Python 3.13, Django 6, uv, Ruff, Pyright, pytest, Granian, WhiteNoise, psycopg, Supabase Postgres, React, TypeScript, Vite, Tailwind, Yarn, ESLint, Prettier, Vitest.

---

## File Structure Map

### Modify
- `.python-version` — pin Python 3.13.
- `pyproject.toml` — upgrade Python/Django, add backend dependencies and tool config.
- `README.md` — document new architecture, setup, and Render flow.
- `manage.py` — keep Django CLI entrypoint aligned with new settings module.
- `core/settings.py` — convert to env-driven settings, add WhiteNoise, static config, ASGI config, installed apps, and frontend integration.
- `core/asgi.py` — assemble Django ASGI app plus startup hook for the Postgres listener.
- `core/urls.py` — route app shell, JSON API, SSE, and auth URLs.
- `rides/models.py` — replace read-side model with `RideListingRecord` that matches the MVP browse contract.
- `rides/admin.py` — register the new read model for inspection.
- `package.json` — switch scripts to Yarn-friendly React/Vite workflow.
- `vite.config.mjs` — point Vite at the new frontend entrypoint and build output.
- `.gitignore` — ignore frontend/node and runtime artifacts.

### Create
- `pyrightconfig.json` — Python type-checking config.
- `frontend/tsconfig.json` — TypeScript compiler config.
- `frontend/eslint.config.js` — frontend linting config.
- `frontend/.prettierrc.json` — frontend formatting config.
- `frontend/src/main.tsx` — React bootstrap.
- `frontend/src/app/App.tsx` — React app root.
- `frontend/src/app/router.tsx` — route mapping for dashboard/detail.
- `frontend/src/features/rides/api.ts` — fetch functions for list/detail.
- `frontend/src/features/rides/sse.ts` — browser SSE client.
- `frontend/src/features/rides/types.ts` — TS contracts for ride list/detail/event payloads.
- `frontend/src/features/rides/components/RideFilters.tsx` — filter UI.
- `frontend/src/features/rides/components/RideCard.tsx` — list card UI.
- `frontend/src/features/rides/components/RideDetail.tsx` — detail UI with login-gated future actions.
- `frontend/src/features/rides/pages/RideDashboardPage.tsx` — main list page.
- `frontend/src/features/rides/pages/RideDetailPage.tsx` — detail page.
- `frontend/src/test/setup.ts` — Vitest setup.
- `src/brazcar/domain/ride_listing.py` — domain entity/value object definitions.
- `src/brazcar/application/dto.py` — list/detail DTOs and query objects.
- `src/brazcar/application/ports.py` — query and streaming port interfaces.
- `src/brazcar/application/use_cases/list_ride_listings.py` — list use case.
- `src/brazcar/application/use_cases/get_ride_listing_detail.py` — detail use case.
- `src/brazcar/application/use_cases/get_current_user_context.py` — user context use case.
- `src/brazcar/application/events.py` — event payload contract for ride updates.
- `src/brazcar/bootstrap/config.py` — env config loader.
- `src/brazcar/bootstrap/container.py` — dependency wiring.
- `src/brazcar/bootstrap/runtime.py` — startup/shutdown hooks for the listener.
- `src/brazcar/adapters/outbound/postgres_ride_repository.py` — read repository adapter.
- `src/brazcar/adapters/outbound/postgres_notification_listener.py` — `LISTEN/NOTIFY` listener adapter.
- `src/brazcar/adapters/outbound/stream_hub.py` — in-process SSE subscriber hub.
- `src/brazcar/adapters/inbound/http/api_views.py` — JSON list/detail endpoints.
- `src/brazcar/adapters/inbound/http/page_views.py` — app-shell HTML views.
- `src/brazcar/adapters/inbound/http/sse_views.py` — SSE endpoint.
- `src/brazcar/adapters/inbound/http/urls.py` — app URLs.
- `templates/app_shell.html` — Django host template for the React app.
- `rides/migrations/0003_ride_listing_record.py` — schema + trigger migration.
- `tests/bootstrap/test_config.py` — config loader tests.
- `tests/domain/test_ride_listing.py` — domain tests.
- `tests/application/test_list_ride_listings.py` — list use-case tests.
- `tests/application/test_get_ride_listing_detail.py` — detail use-case tests.
- `tests/adapters/outbound/test_postgres_ride_repository.py` — repository mapping tests.
- `tests/adapters/outbound/test_postgres_notification_listener.py` — listener tests.
- `tests/adapters/inbound/test_api_views.py` — JSON API tests.
- `tests/adapters/inbound/test_sse_views.py` — SSE endpoint tests.
- `frontend/src/features/rides/__tests__/RideDashboardPage.test.tsx` — dashboard tests.
- `frontend/src/features/rides/__tests__/RideDetailPage.test.tsx` — detail tests.
- `Dockerfile` — multi-stage production container.
- `scripts/entrypoint.sh` — runtime bootstrap.
- `render.yaml` — optional Render deployment descriptor.

### Delete
- `package-lock.json` — replace npm lockfile with Yarn lockfile.
- `static/js/main.js` — superseded by React frontend entrypoint.
- `static/css/main.css` — superseded by frontend Tailwind entrypoint.
- `braz_car/templates/index.html` — replaced by React shell.
- `braz_car/templates/base.html` — replaced by `templates/app_shell.html`.

---

### Task 1: Reset runtime, package management, and environment-driven settings foundation

**Files:**
- Modify: `.python-version`
- Modify: `pyproject.toml`
- Modify: `core/settings.py`
- Modify: `.gitignore`
- Delete: `package-lock.json`
- Modify: `package.json`
- Create: `pyrightconfig.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/eslint.config.js`
- Create: `frontend/.prettierrc.json`
- Create: `src/brazcar/bootstrap/config.py`
- Test: `tests/bootstrap/test_config.py`

- [ ] **Step 1: Write the failing backend config test**

```python
from src.brazcar.bootstrap.config import load_app_config


def test_load_app_config_reads_required_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://example.com")

    config = load_app_config()

    assert config.python_version == "3.13"
    assert config.database_url.startswith("postgresql://postgres:")
    assert config.allowed_hosts == ["localhost", "127.0.0.1"]
    assert config.csrf_trusted_origins == ["https://example.com"]
```

- [ ] **Step 2: Run the backend config test to verify it fails**

Run: `uv run pytest tests/bootstrap/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.brazcar.bootstrap.config'`

- [ ] **Step 3: Implement the config loader and modern toolchain baseline**

```python
# src/brazcar/bootstrap/config.py
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    secret_key: str
    database_url: str
    allowed_hosts: list[str]
    csrf_trusted_origins: list[str]
    debug: bool
    python_version: str = "3.13"


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_app_config() -> AppConfig:
    return AppConfig(
        secret_key=os.environ["SECRET_KEY"],
        database_url=os.environ["DATABASE_URL"],
        allowed_hosts=_split_csv(os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")),
        csrf_trusted_origins=_split_csv(os.getenv("CSRF_TRUSTED_ORIGINS", "")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
```

```toml
# pyproject.toml
[project]
name = "brazcar"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "django>=6.0a1",
  "dj-database-url>=2.2.0",
  "whitenoise>=6.8.2",
  "granian>=1.7.6",
  "psycopg[binary]>=3.2.3",
  "django-vite>=3.1.0",
  "pillow>=11.3.0",
]

[dependency-groups]
dev = [
  "pytest>=8.4.2",
  "pytest-django>=4.9.0",
  "ruff>=0.15.9",
  "pyright>=1.1.405",
]

[tool.ruff]
target-version = "py313"
line-length = 100
```

```python
# core/settings.py
from pathlib import Path
import dj_database_url
from src.brazcar.bootstrap.config import load_app_config

BASE_DIR = Path(__file__).resolve().parent.parent
APP_CONFIG = load_app_config()
SECRET_KEY = APP_CONFIG.secret_key
DEBUG = APP_CONFIG.debug
ALLOWED_HOSTS = APP_CONFIG.allowed_hosts
CSRF_TRUSTED_ORIGINS = APP_CONFIG.csrf_trusted_origins
DATABASES = {"default": dj_database_url.parse(APP_CONFIG.database_url, conn_max_age=600)}
ASGI_APPLICATION = "core.asgi.application"
WSGI_APPLICATION = "core.wsgi.application"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_vite",
    "braz_car",
    "users",
    "rides",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "assets"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
```

```json
// package.json
{
  "private": true,
  "packageManager": "yarn@1.22.22",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint ./frontend/src --max-warnings=0",
    "test": "vitest run"
  }
}
```

- [ ] **Step 4: Run backend and frontend checks to verify the foundation passes**

Run: `uv run pytest tests/bootstrap/test_config.py -v && uv run pyright && uv run ruff check . && uv run ruff format --check .`
Expected: `1 passed` and no Ruff/Pyright errors

Run: `yarn install && yarn lint`
Expected: ESLint exits `0` and generates `yarn.lock`

- [ ] **Step 5: Commit**

```bash
git add .python-version pyproject.toml core/settings.py .gitignore package.json yarn.lock pyrightconfig.json frontend/tsconfig.json frontend/eslint.config.js frontend/.prettierrc.json src/brazcar/bootstrap/config.py tests/bootstrap/test_config.py
git rm package-lock.json
git commit -m "chore: reset BrazCar runtime and tooling foundation"
```

### Task 2: Build the ride read model and hexagonal application core

**Files:**
- Modify: `rides/models.py`
- Modify: `rides/admin.py`
- Create: `rides/migrations/0003_ride_listing_record.py`
- Create: `src/brazcar/domain/ride_listing.py`
- Create: `src/brazcar/application/dto.py`
- Create: `src/brazcar/application/ports.py`
- Create: `src/brazcar/application/use_cases/list_ride_listings.py`
- Create: `src/brazcar/application/use_cases/get_ride_listing_detail.py`
- Create: `src/brazcar/application/use_cases/get_current_user_context.py`
- Test: `tests/domain/test_ride_listing.py`
- Test: `tests/application/test_list_ride_listings.py`
- Test: `tests/application/test_get_ride_listing_detail.py`

- [ ] **Step 1: Write the failing domain and use-case tests**

```python
from decimal import Decimal
from datetime import datetime, UTC

from src.brazcar.application.dto import RideListQuery
from src.brazcar.application.use_cases.list_ride_listings import ListRideListings
from src.brazcar.domain.ride_listing import RideListing


class FakeRideRepository:
    def list(self, query):
        return [
            RideListing(
                public_id="ride-1",
                origin="Brazlândia",
                destination="Esplanada",
                departure_at=datetime(2026, 4, 19, 19, 30, tzinfo=UTC),
                price=Decimal("7.00"),
                seats=3,
                driver_name="João Silva",
                vehicle_label="Civic Branco",
                route_stops=["Eixo Monumental"],
                notes="Chamar PV",
                payment_method="PIX",
                contact_link="https://wa.me/5561999999999",
                created_at=datetime(2026, 4, 19, 18, 0, tzinfo=UTC),
                updated_at=datetime(2026, 4, 19, 18, 0, tzinfo=UTC),
                is_visible=True,
            )
        ]


def test_ride_listing_requires_non_negative_price_and_seats():
    RideListing(
        public_id="ride-1",
        origin="A",
        destination="B",
        departure_at=datetime(2026, 4, 19, 19, 30, tzinfo=UTC),
        price=Decimal("7.00"),
        seats=1,
        driver_name="João",
        vehicle_label="Civic",
        route_stops=[],
        notes="",
        payment_method="PIX",
        contact_link="https://wa.me/1",
        created_at=datetime(2026, 4, 19, 18, 0, tzinfo=UTC),
        updated_at=datetime(2026, 4, 19, 18, 0, tzinfo=UTC),
        is_visible=True,
    )


def test_list_ride_listings_returns_repository_results():
    use_case = ListRideListings(repository=FakeRideRepository())

    result = use_case.execute(
        RideListQuery(origin="Brazlândia", destination="Esplanada")
    )

    assert result.items[0].public_id == "ride-1"
    assert result.items[0].price == "7.00"
```

- [ ] **Step 2: Run the domain and use-case tests to verify they fail**

Run: `uv run pytest tests/domain/test_ride_listing.py tests/application/test_list_ride_listings.py tests/application/test_get_ride_listing_detail.py -v`
Expected: FAIL with missing `src.brazcar.domain.ride_listing` and `src.brazcar.application` modules

- [ ] **Step 3: Implement the read model, domain entity, and use cases**

```python
# rides/models.py
from django.db import models


class RideListingRecord(models.Model):
    public_id = models.SlugField(unique=True)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    departure_at = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats = models.PositiveIntegerField()
    driver_name = models.CharField(max_length=120)
    vehicle_label = models.CharField(max_length=120)
    route_stops = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=120)
    contact_link = models.URLField(max_length=500)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-departure_at", "-created_at"]
```

```python
# src/brazcar/domain/ride_listing.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class RideListing:
    public_id: str
    origin: str
    destination: str
    departure_at: datetime
    price: Decimal
    seats: int
    driver_name: str
    vehicle_label: str
    route_stops: list[str]
    notes: str
    payment_method: str
    contact_link: str
    created_at: datetime
    updated_at: datetime
    is_visible: bool

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError("price must be non-negative")
        if self.seats < 0:
            raise ValueError("seats must be non-negative")
```

```python
# src/brazcar/application/dto.py
from dataclasses import dataclass


@dataclass(frozen=True)
class RideListQuery:
    origin: str | None = None
    destination: str | None = None
    departure_after: str | None = None
    max_price: str | None = None
    min_seats: int | None = None


@dataclass(frozen=True)
class RideListItem:
    public_id: str
    origin: str
    destination: str
    departure_at: str
    price: str
    seats: int
    driver_name: str
    vehicle_label: str
    route_stops: list[str]
    notes: str
    payment_method: str
    contact_link: str


@dataclass(frozen=True)
class RideListResult:
    items: list[RideListItem]
```

```python
# src/brazcar/application/ports.py
from typing import Protocol
from src.brazcar.application.dto import RideListQuery
from src.brazcar.domain.ride_listing import RideListing


class RideListingQueryPort(Protocol):
    def list(self, query: RideListQuery) -> list[RideListing]: ...
    def get_by_public_id(self, public_id: str) -> RideListing | None: ...
```

```python
# src/brazcar/application/use_cases/list_ride_listings.py
from src.brazcar.application.dto import RideListItem, RideListQuery, RideListResult
from src.brazcar.application.ports import RideListingQueryPort


class ListRideListings:
    def __init__(self, repository: RideListingQueryPort) -> None:
        self._repository = repository

    def execute(self, query: RideListQuery) -> RideListResult:
        rides = self._repository.list(query)
        return RideListResult(
            items=[
                RideListItem(
                    public_id=ride.public_id,
                    origin=ride.origin,
                    destination=ride.destination,
                    departure_at=ride.departure_at.isoformat(),
                    price=f"{ride.price:.2f}",
                    seats=ride.seats,
                    driver_name=ride.driver_name,
                    vehicle_label=ride.vehicle_label,
                    route_stops=ride.route_stops,
                    notes=ride.notes,
                    payment_method=ride.payment_method,
                    contact_link=ride.contact_link,
                )
                for ride in rides
            ]
        )
```

- [ ] **Step 4: Run the domain and application tests to verify they pass**

Run: `uv run pytest tests/domain/test_ride_listing.py tests/application/test_list_ride_listings.py tests/application/test_get_ride_listing_detail.py -v`
Expected: all listed tests PASS

- [ ] **Step 5: Generate and inspect the migration**

Run: `uv run python manage.py makemigrations rides`
Expected: Django creates `rides/migrations/0003_ride_listing_record.py`

Run: `uv run python manage.py sqlmigrate rides 0003`
Expected: SQL for `ride_listing_record` table creation prints without errors

- [ ] **Step 6: Commit**

```bash
git add rides/models.py rides/admin.py rides/migrations/0003_ride_listing_record.py src/brazcar/domain/ride_listing.py src/brazcar/application/dto.py src/brazcar/application/ports.py src/brazcar/application/use_cases/list_ride_listings.py src/brazcar/application/use_cases/get_ride_listing_detail.py src/brazcar/application/use_cases/get_current_user_context.py tests/domain/test_ride_listing.py tests/application/test_list_ride_listings.py tests/application/test_get_ride_listing_detail.py
git commit -m "feat: add ride listing read model and application core"
```

### Task 3: Add the Postgres repository, `LISTEN/NOTIFY`, and in-process stream hub

**Files:**
- Create: `src/brazcar/application/events.py`
- Create: `src/brazcar/adapters/outbound/postgres_ride_repository.py`
- Create: `src/brazcar/adapters/outbound/postgres_notification_listener.py`
- Create: `src/brazcar/adapters/outbound/stream_hub.py`
- Modify: `rides/migrations/0003_ride_listing_record.py`
- Test: `tests/adapters/outbound/test_postgres_ride_repository.py`
- Test: `tests/adapters/outbound/test_postgres_notification_listener.py`

- [ ] **Step 1: Write the failing repository and listener tests**

```python
from decimal import Decimal
from datetime import datetime, UTC

from src.brazcar.adapters.outbound.postgres_ride_repository import map_record_to_domain
from src.brazcar.adapters.outbound.stream_hub import StreamHub


class DummyRecord:
    public_id = "ride-1"
    origin = "Brazlândia"
    destination = "Esplanada"
    departure_at = datetime(2026, 4, 19, 19, 30, tzinfo=UTC)
    price = Decimal("7.00")
    seats = 3
    driver_name = "João"
    vehicle_label = "Civic Branco"
    route_stops = ["Eixo Monumental"]
    notes = "Chamar PV"
    payment_method = "PIX"
    contact_link = "https://wa.me/5561999999999"
    is_visible = True
    created_at = datetime(2026, 4, 19, 18, 0, tzinfo=UTC)
    updated_at = datetime(2026, 4, 19, 18, 0, tzinfo=UTC)


def test_map_record_to_domain_returns_ride_listing():
    ride = map_record_to_domain(DummyRecord())

    assert ride.public_id == "ride-1"
    assert ride.route_stops == ["Eixo Monumental"]


def test_stream_hub_fan_out_sends_events_to_all_subscribers():
    hub = StreamHub()
    subscriber_a = hub.subscribe()
    subscriber_b = hub.subscribe()

    hub.publish({"event": "ride-upserted", "public_id": "ride-1"})

    assert subscriber_a.get_nowait()["public_id"] == "ride-1"
    assert subscriber_b.get_nowait()["event"] == "ride-upserted"
```

- [ ] **Step 2: Run the repository and listener tests to verify they fail**

Run: `uv run pytest tests/adapters/outbound/test_postgres_ride_repository.py tests/adapters/outbound/test_postgres_notification_listener.py -v`
Expected: FAIL with missing outbound adapter modules

- [ ] **Step 3: Implement the repository mapping, stream hub, and SQL notification trigger**

```python
# src/brazcar/application/events.py
from dataclasses import dataclass


@dataclass(frozen=True)
class RideUpsertedEvent:
    public_id: str
    updated_at: str
```

```python
# src/brazcar/adapters/outbound/postgres_ride_repository.py
from rides.models import RideListingRecord
from src.brazcar.application.dto import RideListQuery
from src.brazcar.domain.ride_listing import RideListing


def map_record_to_domain(record: RideListingRecord) -> RideListing:
    return RideListing(
        public_id=record.public_id,
        origin=record.origin,
        destination=record.destination,
        departure_at=record.departure_at,
        price=record.price,
        seats=record.seats,
        driver_name=record.driver_name,
        vehicle_label=record.vehicle_label,
        route_stops=record.route_stops,
        notes=record.notes,
        payment_method=record.payment_method,
        contact_link=record.contact_link,
        created_at=record.created_at,
        updated_at=record.updated_at,
        is_visible=record.is_visible,
    )


class PostgresRideRepository:
    def list(self, query: RideListQuery) -> list[RideListing]:
        queryset = RideListingRecord.objects.filter(is_visible=True)
        if query.origin:
            queryset = queryset.filter(origin__icontains=query.origin)
        if query.destination:
            queryset = queryset.filter(destination__icontains=query.destination)
        if query.max_price:
            queryset = queryset.filter(price__lte=query.max_price)
        if query.min_seats is not None:
            queryset = queryset.filter(seats__gte=query.min_seats)
        return [map_record_to_domain(record) for record in queryset.order_by("departure_at", "-created_at")]
```

```python
# src/brazcar/adapters/outbound/stream_hub.py
from __future__ import annotations

from queue import Queue


class StreamHub:
    def __init__(self) -> None:
        self._subscribers: set[Queue] = set()

    def subscribe(self) -> Queue:
        queue: Queue = Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: Queue) -> None:
        self._subscribers.discard(queue)

    def publish(self, payload: dict[str, str]) -> None:
        for queue in list(self._subscribers):
            queue.put_nowait(payload)
```

```sql
-- rides/migrations/0003_ride_listing_record.py (RunSQL fragment)
CREATE OR REPLACE FUNCTION notify_ride_listing_changes() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'rides_changed',
        json_build_object(
            'event', TG_OP,
            'public_id', NEW.public_id,
            'updated_at', NEW.updated_at
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ride_listing_notify_trigger
AFTER INSERT OR UPDATE ON rides_ridelistingrecord
FOR EACH ROW EXECUTE FUNCTION notify_ride_listing_changes();
```

- [ ] **Step 4: Implement the listener adapter and verify its event contract**

```python
# src/brazcar/adapters/outbound/postgres_notification_listener.py
from __future__ import annotations

import json
from psycopg import Connection

from src.brazcar.adapters.outbound.stream_hub import StreamHub


class PostgresNotificationListener:
    def __init__(self, connection: Connection, hub: StreamHub) -> None:
        self._connection = connection
        self._hub = hub

    def listen_forever(self) -> None:
        self._connection.execute("LISTEN rides_changed;")
        for notify in self._connection.notifies(timeout=None):
            payload = json.loads(notify.payload)
            self._hub.publish(
                {
                    "event": "ride-upserted",
                    "public_id": payload["public_id"],
                    "updated_at": payload["updated_at"],
                }
            )
```

- [ ] **Step 5: Run outbound adapter tests to verify they pass**

Run: `uv run pytest tests/adapters/outbound/test_postgres_ride_repository.py tests/adapters/outbound/test_postgres_notification_listener.py -v`
Expected: all listed tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/brazcar/application/events.py src/brazcar/adapters/outbound/postgres_ride_repository.py src/brazcar/adapters/outbound/postgres_notification_listener.py src/brazcar/adapters/outbound/stream_hub.py rides/migrations/0003_ride_listing_record.py tests/adapters/outbound/test_postgres_ride_repository.py tests/adapters/outbound/test_postgres_notification_listener.py
git commit -m "feat: add Postgres repository and notification stream"
```

### Task 4: Expose the JSON API, SSE endpoint, app shell, and runtime wiring

**Files:**
- Create: `src/brazcar/bootstrap/container.py`
- Create: `src/brazcar/bootstrap/runtime.py`
- Create: `src/brazcar/adapters/inbound/http/api_views.py`
- Create: `src/brazcar/adapters/inbound/http/page_views.py`
- Create: `src/brazcar/adapters/inbound/http/sse_views.py`
- Create: `src/brazcar/adapters/inbound/http/urls.py`
- Create: `templates/app_shell.html`
- Modify: `core/asgi.py`
- Modify: `core/urls.py`
- Test: `tests/adapters/inbound/test_api_views.py`
- Test: `tests/adapters/inbound/test_sse_views.py`

- [ ] **Step 1: Write the failing API and SSE tests**

```python
import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_ride_list_api_returns_items(client):
    response = client.get(reverse("api:ride-list"), {"origin": "Brazlândia"})

    assert response.status_code == 200
    body = response.json()
    assert "items" in body


def test_ride_stream_endpoint_uses_event_stream_content_type(client):
    response = client.get(reverse("api:ride-stream"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/event-stream")
```

- [ ] **Step 2: Run the API and SSE tests to verify they fail**

Run: `uv run pytest tests/adapters/inbound/test_api_views.py tests/adapters/inbound/test_sse_views.py -v`
Expected: FAIL with missing URL names or missing view modules

- [ ] **Step 3: Implement the container, API views, app shell, and SSE endpoint**

```python
# src/brazcar/bootstrap/container.py
from psycopg import connect

from src.brazcar.adapters.outbound.postgres_ride_repository import PostgresRideRepository
from src.brazcar.adapters.outbound.stream_hub import StreamHub
from src.brazcar.adapters.outbound.postgres_notification_listener import PostgresNotificationListener
from src.brazcar.application.use_cases.list_ride_listings import ListRideListings
from src.brazcar.application.use_cases.get_ride_listing_detail import GetRideListingDetail


class Container:
    def __init__(self, database_url: str) -> None:
        self.stream_hub = StreamHub()
        self.repository = PostgresRideRepository()
        self.list_ride_listings = ListRideListings(repository=self.repository)
        self.get_ride_listing_detail = GetRideListingDetail(repository=self.repository)
        self.notification_connection = connect(database_url, autocommit=True)
        self.notification_listener = PostgresNotificationListener(
            connection=self.notification_connection,
            hub=self.stream_hub,
        )
```

```python
# src/brazcar/adapters/inbound/http/api_views.py
from django.http import JsonResponse, Http404
from django.views import View

from src.brazcar.application.dto import RideListQuery
from src.brazcar.bootstrap.container import Container
from src.brazcar.bootstrap.config import load_app_config

container = Container(load_app_config().database_url)


class RideListApiView(View):
    def get(self, request):
        query = RideListQuery(
            origin=request.GET.get("origin"),
            destination=request.GET.get("destination"),
            departure_after=request.GET.get("departure_after"),
            max_price=request.GET.get("max_price"),
            min_seats=int(request.GET["min_seats"]) if request.GET.get("min_seats") else None,
        )
        result = container.list_ride_listings.execute(query)
        return JsonResponse({"items": [item.__dict__ for item in result.items]})
```

```python
# src/brazcar/adapters/inbound/http/sse_views.py
import json
from django.http import StreamingHttpResponse

from src.brazcar.adapters.inbound.http.api_views import container


def ride_stream_view(request):
    queue = container.stream_hub.subscribe()

    def event_stream():
        try:
            while True:
                payload = queue.get()
                yield f"event: ride-upserted\ndata: {json.dumps(payload)}\n\n"
        finally:
            container.stream_hub.unsubscribe(queue)

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
```

```python
# src/brazcar/adapters/inbound/http/urls.py
from django.urls import path
from src.brazcar.adapters.inbound.http.api_views import RideListApiView, RideDetailApiView
from src.brazcar.adapters.inbound.http.page_views import AppShellView, RideDetailShellView
from src.brazcar.adapters.inbound.http.sse_views import ride_stream_view

app_name = "api"

urlpatterns = [
    path("", AppShellView.as_view(), name="dashboard"),
    path("rides/<slug:public_id>/", RideDetailShellView.as_view(), name="ride-detail-page"),
    path("api/rides/", RideListApiView.as_view(), name="ride-list"),
    path("api/rides/<slug:public_id>/", RideDetailApiView.as_view(), name="ride-detail"),
    path("api/stream/rides/", ride_stream_view, name="ride-stream"),
]
```

```html
<!-- templates/app_shell.html -->
{% load django_vite %}
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BrazCar</title>
    {% vite_hmr_client %}
    {% vite_asset 'frontend/src/main.tsx' %}
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

- [ ] **Step 4: Wire the URLs and startup runtime**

```python
# core/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("", include("src.brazcar.adapters.inbound.http.urls", namespace="api")),
]
```

```python
# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from src.brazcar.adapters.inbound.http.api_views import container
from src.brazcar.bootstrap.runtime import start_listener_thread

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
start_listener_thread(container.notification_listener)
application = get_asgi_application()
```

- [ ] **Step 5: Run inbound adapter tests to verify they pass**

Run: `uv run pytest tests/adapters/inbound/test_api_views.py tests/adapters/inbound/test_sse_views.py -v`
Expected: all listed tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/brazcar/bootstrap/container.py src/brazcar/bootstrap/runtime.py src/brazcar/adapters/inbound/http/api_views.py src/brazcar/adapters/inbound/http/page_views.py src/brazcar/adapters/inbound/http/sse_views.py src/brazcar/adapters/inbound/http/urls.py templates/app_shell.html core/asgi.py core/urls.py tests/adapters/inbound/test_api_views.py tests/adapters/inbound/test_sse_views.py
git commit -m "feat: expose ride APIs, SSE stream, and app shell"
```

### Task 5: Build the React dashboard and detail frontend on top of the new API

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app/App.tsx`
- Create: `frontend/src/app/router.tsx`
- Create: `frontend/src/features/rides/types.ts`
- Create: `frontend/src/features/rides/api.ts`
- Create: `frontend/src/features/rides/sse.ts`
- Create: `frontend/src/features/rides/components/RideFilters.tsx`
- Create: `frontend/src/features/rides/components/RideCard.tsx`
- Create: `frontend/src/features/rides/components/RideDetail.tsx`
- Create: `frontend/src/features/rides/pages/RideDashboardPage.tsx`
- Create: `frontend/src/features/rides/pages/RideDetailPage.tsx`
- Create: `frontend/src/test/setup.ts`
- Modify: `vite.config.mjs`
- Test: `frontend/src/features/rides/__tests__/RideDashboardPage.test.tsx`
- Test: `frontend/src/features/rides/__tests__/RideDetailPage.test.tsx`

- [ ] **Step 1: Write the failing dashboard and detail tests**

```tsx
import { render, screen } from "@testing-library/react";
import { RideDashboardPage } from "../pages/RideDashboardPage";

it("renders required filter controls", async () => {
  render(<RideDashboardPage />);

  expect(screen.getByLabelText(/origem/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/destino/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/preço máximo/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/vagas mínimas/i)).toBeInTheDocument();
});
```

```tsx
import { render, screen } from "@testing-library/react";
import { RideDetailPage } from "../pages/RideDetailPage";

it("shows a login-only action placeholder on the detail page", async () => {
  render(<RideDetailPage />);

  expect(screen.getByText(/entre para ver ações desta carona/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the frontend tests to verify they fail**

Run: `yarn test frontend/src/features/rides/__tests__/RideDashboardPage.test.tsx frontend/src/features/rides/__tests__/RideDetailPage.test.tsx`
Expected: FAIL with missing React app files

- [ ] **Step 3: Implement the React app, API client, filters, and SSE client**

```tsx
// frontend/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./app/router";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("app")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
```

```tsx
// frontend/src/features/rides/api.ts
import type { RideListItem } from "./types";

export async function fetchRides(search: URLSearchParams): Promise<RideListItem[]> {
  const response = await fetch(`/api/rides/?${search.toString()}`, { credentials: "same-origin" });
  const body = await response.json();
  return body.items;
}
```

```tsx
// frontend/src/features/rides/sse.ts
export function subscribeToRideStream(onRideUpserted: (publicId: string) => void) {
  const source = new EventSource("/api/stream/rides/");
  source.addEventListener("ride-upserted", (event) => {
    const payload = JSON.parse((event as MessageEvent).data) as { public_id: string };
    onRideUpserted(payload.public_id);
  });
  return () => source.close();
}
```

```tsx
// frontend/src/features/rides/pages/RideDashboardPage.tsx
import { useEffect, useMemo, useState } from "react";
import { fetchRides } from "../api";
import { subscribeToRideStream } from "../sse";
import { RideCard } from "../components/RideCard";
import { RideFilters } from "../components/RideFilters";
import type { RideListItem } from "../types";

export function RideDashboardPage() {
  const [rides, setRides] = useState<RideListItem[]>([]);
  const [searchParams, setSearchParams] = useState(new URLSearchParams(window.location.search));

  useEffect(() => {
    fetchRides(searchParams).then(setRides);
  }, [searchParams]);

  useEffect(() => {
    return subscribeToRideStream(() => {
      fetchRides(searchParams).then(setRides);
    });
  }, [searchParams]);

  return (
    <main>
      <RideFilters searchParams={searchParams} onChange={setSearchParams} />
      <section>
        {rides.map((ride) => (
          <RideCard key={ride.public_id} ride={ride} />
        ))}
      </section>
    </main>
  );
}
```

- [ ] **Step 4: Run frontend quality checks to verify the app passes**

Run: `yarn test && yarn lint && yarn build`
Expected: all commands exit `0` and Vite emits production assets into `assets/`

- [ ] **Step 5: Commit**

```bash
git add frontend/src/main.tsx frontend/src/app/App.tsx frontend/src/app/router.tsx frontend/src/features/rides/types.ts frontend/src/features/rides/api.ts frontend/src/features/rides/sse.ts frontend/src/features/rides/components/RideFilters.tsx frontend/src/features/rides/components/RideCard.tsx frontend/src/features/rides/components/RideDetail.tsx frontend/src/features/rides/pages/RideDashboardPage.tsx frontend/src/features/rides/pages/RideDetailPage.tsx frontend/src/test/setup.ts frontend/src/features/rides/__tests__/RideDashboardPage.test.tsx frontend/src/features/rides/__tests__/RideDetailPage.test.tsx vite.config.mjs
git commit -m "feat: add React ride dashboard and detail frontend"
```

### Task 6: Wire auth-aware detail behavior, remove obsolete templates, and update docs

**Files:**
- Modify: `users/urls.py`
- Modify: `users/views.py`
- Modify: `README.md`
- Delete: `braz_car/templates/index.html`
- Delete: `braz_car/templates/base.html`
- Delete: `static/js/main.js`
- Delete: `static/css/main.css`
- Test: `tests/adapters/inbound/test_api_views.py`
- Test: `frontend/src/features/rides/__tests__/RideDetailPage.test.tsx`

- [ ] **Step 1: Extend the failing tests for auth-aware detail actions**

```python
@pytest.mark.django_db
def test_ride_detail_api_includes_auth_context_for_logged_out_user(client):
    response = client.get(reverse("api:ride-detail", kwargs={"public_id": "ride-1"}))

    assert response.status_code == 200
    assert response.json()["viewer"]["is_authenticated"] is False
```

```tsx
it("shows future action controls only for authenticated viewers", async () => {
  render(<RideDetail isAuthenticated={true} ride={rideFixture} />);

  expect(screen.getByText(/ações desta carona/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run: `uv run pytest tests/adapters/inbound/test_api_views.py -v && yarn test frontend/src/features/rides/__tests__/RideDetailPage.test.tsx`
Expected: FAIL because viewer auth state is not returned and detail action region is not conditionally rendered

- [ ] **Step 3: Implement auth-aware detail payloads and clean obsolete Django template assets**

```python
# src/brazcar/application/use_cases/get_current_user_context.py
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUserContext:
    is_authenticated: bool
    username: str | None


class GetCurrentUserContext:
    def execute(self, request) -> CurrentUserContext:
        user = request.user
        return CurrentUserContext(
            is_authenticated=user.is_authenticated,
            username=user.username if user.is_authenticated else None,
        )
```

```tsx
// frontend/src/features/rides/components/RideDetail.tsx
export function RideDetail({ ride, isAuthenticated }: Props) {
  return (
    <article>
      <h1>{ride.origin} → {ride.destination}</h1>
      {isAuthenticated ? (
        <section>
          <h2>Ações desta carona</h2>
          <p>Área reservada para entrar na fila e interações futuras.</p>
        </section>
      ) : (
        <p>Entre para ver ações desta carona.</p>
      )}
    </article>
  );
}
```

```md
<!-- README.md additions -->
## MVP atual
- Dashboard público de caronas
- Página de detalhe por carona
- Atualização automática com SSE + Postgres LISTEN/NOTIFY
- Frontend React hospedado pelo Django
```

- [ ] **Step 4: Run tests and smoke-check docs/build after cleanup**

Run: `uv run pytest tests/adapters/inbound/test_api_views.py -v && yarn test frontend/src/features/rides/__tests__/RideDetailPage.test.tsx && yarn build`
Expected: all commands exit `0`

- [ ] **Step 5: Commit**

```bash
git add users/urls.py users/views.py README.md src/brazcar/application/use_cases/get_current_user_context.py frontend/src/features/rides/components/RideDetail.tsx tests/adapters/inbound/test_api_views.py frontend/src/features/rides/__tests__/RideDetailPage.test.tsx
git rm braz_car/templates/index.html braz_car/templates/base.html static/js/main.js static/css/main.css
git commit -m "refactor: align auth-aware detail flow and remove obsolete templates"
```

### Task 7: Add Docker, entrypoint, Granian runtime, and final deployment verification

**Files:**
- Create: `Dockerfile`
- Create: `scripts/entrypoint.sh`
- Create: `render.yaml`
- Modify: `core/asgi.py`
- Test: `tests/bootstrap/test_config.py`

- [ ] **Step 1: Add the failing runtime smoke test**

```python
from pathlib import Path


def test_runtime_artifacts_exist():
    assert Path("Dockerfile").exists()
    assert Path("scripts/entrypoint.sh").exists()
```

- [ ] **Step 2: Run the runtime smoke test to verify it fails**

Run: `uv run pytest tests/bootstrap/test_config.py::test_runtime_artifacts_exist -v`
Expected: FAIL because runtime artifacts do not exist yet

- [ ] **Step 3: Implement the Dockerfile, entrypoint, and Render descriptor**

```dockerfile
# Dockerfile
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /app
COPY package.json yarn.lock ./
COPY frontend ./frontend
COPY vite.config.mjs ./
RUN corepack enable && yarn install --frozen-lockfile && yarn build

FROM python:3.13-slim-bookworm AS backend-build
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
COPY --from=frontend-build /app/assets ./assets

FROM python:3.13-slim-bookworm AS runtime
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=backend-build /app /app
RUN chown -R appuser:appuser /app
USER appuser
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
```

```bash
#!/usr/bin/env bash
set -euo pipefail

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput
exec uv run granian --interface asgi --host 0.0.0.0 --port "${PORT:-8000}" core.asgi:application
```

```yaml
# render.yaml
services:
  - type: web
    name: brazcar
    env: docker
    plan: free
    autoDeploy: true
```

- [ ] **Step 4: Verify the container and runtime end to end**

Run: `docker build -t brazcar:local .`
Expected: image builds successfully

Run: `DATABASE_URL='postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres' SECRET_KEY='test-secret' docker run --rm -p 8000:8000 brazcar:local`
Expected: Granian starts and listens on `0.0.0.0:8000`

Run: `uv run pytest && uv run pyright && uv run ruff check . && yarn test && yarn lint && yarn build`
Expected: all commands pass with exit code `0`

- [ ] **Step 5: Commit**

```bash
git add Dockerfile scripts/entrypoint.sh render.yaml core/asgi.py tests/bootstrap/test_config.py
git commit -m "feat: add Render-ready container runtime"
```

## Spec Coverage Check

- Public dashboard: covered by Tasks 4 and 5.
- Detail page: covered by Tasks 4, 5, and 6.
- Public browsing with login prepared for future actions: covered by Tasks 4 and 6.
- SSE + Postgres `LISTEN/NOTIFY`: covered by Tasks 3, 4, and 5.
- Supabase Postgres as source of truth: covered by Tasks 1, 2, and 3.
- Hexagonal architecture: covered by Tasks 2, 3, and 4.
- Granian + WhiteNoise + single-service Render deploy: covered by Tasks 1 and 7.
- Docker + entrypoint: covered by Task 7.
- Python 3.13, Django 6, uv, Ruff, Pyright, Yarn, TypeScript, Prettier, ESLint: covered by Tasks 1 and 5.

## Self-Review Notes

- No `TODO` or `TBD` placeholders remain.
- All later tasks reuse names defined earlier: `RideListingRecord`, `RideListQuery`, `PostgresRideRepository`, `StreamHub`, and `PostgresNotificationListener`.
- The plan stays within the approved MVP scope and defers bot ingestion, queueing, and WebSockets.
