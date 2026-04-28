from __future__ import annotations

from collections.abc import Iterator

from django.http import HttpRequest, StreamingHttpResponse

from src.brazcar.bootstrap.container import get_container


_CONNECT_EVENT = b"event: connect\ndata: {}\n\n"
_HEARTBEAT_EVENT = b": keepalive\n\n"


def ride_listing_events_stream(request: HttpRequest) -> StreamingHttpResponse:
    subscription = get_container().ride_listing_events_hub().subscribe()

    def event_stream() -> Iterator[bytes]:
        try:
            yield _CONNECT_EVENT
            while True:
                events = subscription.wait(timeout=15.0)
                if not events:
                    yield _HEARTBEAT_EVENT
                    continue
                for event in events:
                    yield f"event: {event.event_type}\n".encode()
                    yield f"data: {event.to_payload()}\n\n".encode()
        finally:
            subscription.close()

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response
