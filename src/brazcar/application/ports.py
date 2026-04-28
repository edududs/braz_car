from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from src.brazcar.application.dto import CurrentUserContext, RideListingsFilter
from src.brazcar.domain.ride_listing import RideListing


class RideListingReader(Protocol):
    def list(self, filters: RideListingsFilter) -> Sequence[RideListing]: ...

    def get_by_ride_id(self, ride_id: int) -> RideListing | None: ...


class CurrentUserContextProvider(Protocol):
    def get_current_user_context(self) -> CurrentUserContext: ...
