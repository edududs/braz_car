from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from psycopg.conninfo import make_conninfo

from src.brazcar.adapters.outbound.postgres_notification_listener import PostgresNotificationListener
from src.brazcar.adapters.outbound.stream_hub import StreamHub
from src.brazcar.application.events import RideListingChanged


@dataclass(frozen=True, slots=True)
class FakeNotify:
    channel: str
    payload: str
    pid: int = 1234


class FakeConnection:
    def __init__(self, notifications: list[FakeNotify]) -> None:
        self.notifications = tuple(notifications)
        self.autocommit = False
        self.executed: list[str] = []
        self.notifies_calls: list[dict[str, object]] = []
        self.closed = False

    def set_autocommit(self, value: bool) -> None:
        self.autocommit = value

    def execute(self, statement: str) -> None:
        self.executed.append(statement)

    def notifies(self, *, timeout: float | None = None, stop_after: int | None = None):
        self.notifies_calls.append({"timeout": timeout, "stop_after": stop_after})
        notifications = self.notifications if stop_after is None else self.notifications[:stop_after]
        for notification in notifications:
            yield notification

    def close(self) -> None:
        self.closed = True



def test_stream_hub_fan_outs_events_to_active_subscribers() -> None:
    hub = StreamHub()
    first = hub.subscribe()
    second = hub.subscribe()
    event = RideListingChanged(ride_id=7)

    hub.publish(event)

    assert first.drain() == (event,)
    assert second.drain() == (event,)



def test_stream_hub_stops_delivery_after_subscription_is_closed() -> None:
    hub = StreamHub()
    subscription = hub.subscribe()
    subscription.close()

    hub.publish(RideListingChanged(ride_id=7))

    assert subscription.drain() == ()



def test_notification_listener_registers_listen_and_publishes_events() -> None:
    channel = "ride_listing_events"
    connection = FakeConnection(
        [FakeNotify(channel=channel, payload=json.dumps({"ride_id": 7}))]
    )
    hub = StreamHub()
    subscription = hub.subscribe()
    listener = PostgresNotificationListener(
        connection_factory=lambda: connection,
        stream_hub=hub,
        channel=channel,
    )

    events = listener.listen_once(timeout=0.1, stop_after=1)

    assert connection.autocommit is True
    assert connection.executed == [f"LISTEN {channel}"]
    assert connection.notifies_calls == [{"timeout": 0.1, "stop_after": 1}]
    assert events == (RideListingChanged(ride_id=7),)
    assert subscription.drain() == events



def test_notification_listener_close_closes_open_connection() -> None:
    connection = FakeConnection([])
    listener = PostgresNotificationListener(
        connection_factory=lambda: connection,
        stream_hub=StreamHub(),
        channel="ride_listing_events",
    )

    listener.listen_once(stop_after=0)
    listener.close()

    assert connection.closed is True



def test_notification_listener_rejects_invalid_channel_name_before_listen() -> None:
    connection = FakeConnection([])
    listener = PostgresNotificationListener(
        connection_factory=lambda: connection,
        stream_hub=StreamHub(),
        channel='ride_listing_events; UNLISTEN *',
    )

    with pytest.raises(ValueError, match='Invalid PostgreSQL LISTEN channel'):
        listener.listen_once(stop_after=0)

    assert connection.autocommit is False
    assert connection.executed == []



def test_default_connection_factory_preserves_supported_database_options(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_connect(conninfo: str = "", **kwargs: object) -> FakeConnection:
        captured["conninfo"] = conninfo
        captured["kwargs"] = kwargs
        return FakeConnection([])

    monkeypatch.setattr(
        "src.brazcar.adapters.outbound.postgres_notification_listener.settings",
        SimpleNamespace(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": "brazcar",
                    "USER": "postgres",
                    "PASSWORD": "secret",
                    "HOST": "db.internal",
                    "PORT": 5433,
                    "OPTIONS": {
                        "sslmode": "require",
                        "target_session_attrs": "read-write",
                    },
                }
            }
        ),
    )
    monkeypatch.setattr(
        "src.brazcar.adapters.outbound.postgres_notification_listener.Connection.connect",
        fake_connect,
    )

    PostgresNotificationListener(stream_hub=StreamHub()).listen_once(stop_after=0)

    assert captured == {
        "conninfo": make_conninfo(
            dbname="brazcar",
            user="postgres",
            password="secret",
            host="db.internal",
            port=5433,
            sslmode="require",
            target_session_attrs="read-write",
        ),
        "kwargs": {"autocommit": True},
    }



def test_default_connection_factory_uses_django_default_postgres_settings(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_connect(conninfo: str = "", **kwargs: object) -> FakeConnection:
        captured["conninfo"] = conninfo
        captured["kwargs"] = kwargs
        return FakeConnection([])

    monkeypatch.setattr(
        "src.brazcar.adapters.outbound.postgres_notification_listener.settings",
        SimpleNamespace(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": "brazcar",
                    "USER": "postgres",
                    "PASSWORD": "secret",
                    "HOST": "db.internal",
                    "PORT": 5433,
                }
            }
        ),
    )
    monkeypatch.setattr(
        "src.brazcar.adapters.outbound.postgres_notification_listener.Connection.connect",
        fake_connect,
    )

    PostgresNotificationListener(stream_hub=StreamHub()).listen_once(stop_after=0)

    assert captured == {
        "conninfo": make_conninfo(
            dbname="brazcar",
            user="postgres",
            password="secret",
            host="db.internal",
            port=5433,
        ),
        "kwargs": {"autocommit": True},
    }
