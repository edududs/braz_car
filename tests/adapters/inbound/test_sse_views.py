from __future__ import annotations

import pytest

from src.brazcar.adapters.outbound.stream_hub import StreamHub
from src.brazcar.application.events import RideListingChanged


class FakeContainer:
    def __init__(self, hub: StreamHub[RideListingChanged]) -> None:
        self._hub = hub

    def ride_listing_events_hub(self) -> StreamHub[RideListingChanged]:
        return self._hub


@pytest.fixture
def event_hub() -> StreamHub[RideListingChanged]:
    return StreamHub()


@pytest.fixture(autouse=True)
def patch_sse_container(
    monkeypatch: pytest.MonkeyPatch,
    event_hub: StreamHub[RideListingChanged],
) -> None:
    monkeypatch.setattr(
        "src.brazcar.adapters.inbound.http.sse_views.get_container",
        lambda: FakeContainer(event_hub),
        raising=False,
    )


@pytest.mark.django_db
def test_ride_listing_events_stream_is_exposed(event_hub: StreamHub[RideListingChanged], client) -> None:
    response = client.get("/events/ride-listings/")

    event_hub.publish(RideListingChanged(ride_id=7))
    chunks: list[bytes] = []
    stream = response.streaming_content
    for _ in range(4):
        chunks.append(next(stream))
    payload = b"".join(chunks)
    response.close()

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/event-stream")
    assert response["Cache-Control"] == "no-cache"
    assert b"event: connect\ndata: {}\n\n" in payload
    assert b"event: ride_listing_changed\n" in payload
    assert b'data: {"event_type": "ride_listing_changed", "ride_id": 7}\n\n' in payload


@pytest.mark.django_db
def test_ride_listing_events_stream_emits_keepalive_when_idle(client, monkeypatch: pytest.MonkeyPatch) -> None:
    class IdleSubscription:
        def wait(self, timeout: float | None = None) -> tuple[RideListingChanged, ...]:
            return ()

        def close(self) -> None:
            return None

    class IdleContainer:
        def ride_listing_events_hub(self):
            class IdleHub:
                def subscribe(self_inner):
                    return IdleSubscription()

            return IdleHub()

    monkeypatch.setattr(
        "src.brazcar.adapters.inbound.http.sse_views.get_container",
        lambda: IdleContainer(),
        raising=False,
    )

    response = client.get("/events/ride-listings/")
    stream = response.streaming_content
    first_chunk = next(stream)
    second_chunk = next(stream)
    response.close()

    assert first_chunk == b"event: connect\ndata: {}\n\n"
    assert second_chunk == b": keepalive\n\n"
