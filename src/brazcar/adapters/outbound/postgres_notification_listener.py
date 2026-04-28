from __future__ import annotations

import re
from collections.abc import Callable
from typing import Protocol

from django.conf import settings
from psycopg import Connection
from psycopg.conninfo import make_conninfo

from src.brazcar.adapters.outbound.stream_hub import StreamHub
from src.brazcar.application.events import DEFAULT_RIDE_LISTING_EVENTS_CHANNEL, RideListingChanged


_LISTEN_CHANNEL_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class SupportsNotifications(Protocol):
    autocommit: bool

    def set_autocommit(self, value: bool) -> None: ...

    def execute(self, statement: str) -> None: ...

    def notifies(
        self,
        *,
        timeout: float | None = None,
        stop_after: int | None = None,
    ): ...

    def close(self) -> None: ...


class PostgresNotificationListener:
    def __init__(
        self,
        *,
        connection_factory: Callable[[], SupportsNotifications] | None = None,
        stream_hub: StreamHub[RideListingChanged],
        channel: str = DEFAULT_RIDE_LISTING_EVENTS_CHANNEL,
    ) -> None:
        self._connection_factory = connection_factory or self._default_connection_factory
        self._stream_hub = stream_hub
        self._channel = channel
        self._connection: SupportsNotifications | None = None
        self._is_listening = False

    def listen_once(
        self,
        *,
        timeout: float | None = None,
        stop_after: int | None = 1,
    ) -> tuple[RideListingChanged, ...]:
        connection = self._ensure_connection()
        notifications = connection.notifies(timeout=timeout, stop_after=stop_after)
        events: list[RideListingChanged] = []

        for notification in notifications:
            event = RideListingChanged.from_payload(notification.payload)
            self._stream_hub.publish(event)
            events.append(event)

        return tuple(events)

    def close(self) -> None:
        if self._connection is None:
            return
        self._connection.close()
        self._connection = None
        self._is_listening = False

    def _ensure_connection(self) -> SupportsNotifications:
        if self._connection is None:
            self._connection = self._connection_factory()

        if not self._is_listening:
            if _LISTEN_CHANNEL_PATTERN.fullmatch(self._channel) is None:
                raise ValueError("Invalid PostgreSQL LISTEN channel.")
            self._connection.set_autocommit(True)
            self._connection.execute(f"LISTEN {self._channel}")
            self._is_listening = True

        return self._connection

    def _default_connection_factory(self) -> SupportsNotifications:
        database_settings = settings.DATABASES["default"]
        engine = database_settings.get("ENGINE", "")
        if engine != "django.db.backends.postgresql":
            raise RuntimeError(
                "PostgresNotificationListener requires Django default database to use PostgreSQL."
            )

        options = {
            key: value
            for key, value in (database_settings.get("OPTIONS") or {}).items()
            if value is not None and key not in {"conninfo", "autocommit"}
        }
        conninfo = make_conninfo(
            dbname=database_settings.get("NAME") or None,
            user=database_settings.get("USER") or None,
            password=database_settings.get("PASSWORD") or None,
            host=database_settings.get("HOST") or None,
            port=database_settings.get("PORT") or None,
            **options,
        )
        return Connection.connect(conninfo=conninfo, autocommit=True)
