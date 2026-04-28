from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Condition, Lock
from typing import Generic, TypeVar

TEvent = TypeVar("TEvent")


@dataclass(slots=True)
class StreamSubscription(Generic[TEvent]):
    _hub: "StreamHub[TEvent]"
    _events: deque[TEvent] = field(default_factory=deque)
    _condition: Condition = field(default_factory=Condition)
    _closed: bool = False

    def push(self, event: TEvent) -> None:
        if self._closed:
            return
        with self._condition:
            self._events.append(event)
            self._condition.notify_all()

    def drain(self) -> tuple[TEvent, ...]:
        with self._condition:
            drained = tuple(self._events)
            self._events.clear()
            return drained

    def wait(self, timeout: float | None = None) -> tuple[TEvent, ...]:
        with self._condition:
            if not self._events and not self._closed:
                self._condition.wait(timeout=timeout)
            drained = tuple(self._events)
            self._events.clear()
            return drained

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        with self._condition:
            self._condition.notify_all()
        self._hub.unsubscribe(self)


class StreamHub(Generic[TEvent]):
    def __init__(self) -> None:
        self._subscriptions: list[StreamSubscription[TEvent]] = []
        self._subscriptions_lock = Lock()

    def subscribe(self) -> StreamSubscription[TEvent]:
        subscription = StreamSubscription(_hub=self)
        with self._subscriptions_lock:
            self._subscriptions.append(subscription)
        return subscription

    def unsubscribe(self, subscription: StreamSubscription[TEvent]) -> None:
        with self._subscriptions_lock:
            self._subscriptions = [item for item in self._subscriptions if item is not subscription]

    def publish(self, event: TEvent) -> None:
        with self._subscriptions_lock:
            subscriptions = tuple(self._subscriptions)
        for subscription in subscriptions:
            subscription.push(event)
