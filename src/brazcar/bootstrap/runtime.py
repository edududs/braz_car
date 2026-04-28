from __future__ import annotations

import threading
import time
from typing import Protocol

from django.conf import settings

from src.brazcar.bootstrap.container import get_container

_RUNTIME_STARTED = False
_RUNTIME_LOCK = threading.Lock()


class SupportsRuntimeListener(Protocol):
    def listen_once(self, *, timeout: float | None = None, stop_after: int | None = 1): ...
    def close(self) -> None: ...


def start_runtime() -> None:
    global _RUNTIME_STARTED

    if settings.DATABASES["default"].get("ENGINE") != "django.db.backends.postgresql":
        return

    with _RUNTIME_LOCK:
        if _RUNTIME_STARTED:
            return

        listener = get_container().notification_listener()
        thread = threading.Thread(
            target=_listen_forever,
            args=(listener,),
            name="brazcar-ride-listing-listener",
            daemon=True,
        )
        thread.start()
        _RUNTIME_STARTED = True


def _listen_forever(listener: SupportsRuntimeListener) -> None:
    while True:
        try:
            listener.listen_once(timeout=1.0, stop_after=1)
        except Exception:
            listener.close()
            time.sleep(1.0)
            continue
