from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from src.brazcar.adapters.outbound.postgres_notification_listener import PostgresNotificationListener
from src.brazcar.adapters.outbound.postgres_ride_repository import PostgresRideRepository
from src.brazcar.adapters.outbound.stream_hub import StreamHub
from src.brazcar.application.dto import CurrentUserContext
from src.brazcar.application.events import RideListingChanged
from src.brazcar.application.ports import CurrentUserContextProvider, RideListingReader
from src.brazcar.application.use_cases.get_current_user_context import GetCurrentUserContext
from src.brazcar.application.use_cases.list_ride_listings import ListRideListings


class SupportsCurrentUserUseCase(Protocol):
    def execute(self) -> CurrentUserContext: ...


@dataclass(frozen=True, slots=True)
class DjangoCurrentUserContextProvider(CurrentUserContextProvider):
    request: HttpRequest | None = None

    def get_current_user_context(self) -> CurrentUserContext:
        user = getattr(self.request, "user", AnonymousUser()) if self.request is not None else AnonymousUser()
        is_authenticated = bool(getattr(user, "is_authenticated", False))
        user_id = int(user.pk) if is_authenticated and getattr(user, "pk", None) is not None else None
        return CurrentUserContext(user_id=user_id, is_authenticated=is_authenticated)


@dataclass(slots=True)
class AppContainer:
    reader: RideListingReader = field(default_factory=PostgresRideRepository)
    events_hub: StreamHub[RideListingChanged] = field(default_factory=StreamHub)
    _listener: PostgresNotificationListener | None = field(default=None, init=False, repr=False)

    def list_ride_listings(self) -> ListRideListings:
        return ListRideListings(reader=self.reader)

    def get_current_user_context(self, request: HttpRequest | None = None) -> SupportsCurrentUserUseCase:
        return GetCurrentUserContext(provider=DjangoCurrentUserContextProvider(request=request))

    def ride_listing_events_hub(self) -> StreamHub[RideListingChanged]:
        return self.events_hub

    def notification_listener(self) -> PostgresNotificationListener:
        if self._listener is None:
            self._listener = PostgresNotificationListener(stream_hub=self.events_hub)
        return self._listener


_container: AppContainer | None = None


def get_container() -> AppContainer:
    global _container
    if _container is None:
        _container = AppContainer()
    return _container
