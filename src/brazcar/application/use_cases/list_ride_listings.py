from __future__ import annotations

from dataclasses import dataclass

from src.brazcar.application.dto import RideListingsFilter
from src.brazcar.application.ports import RideListingReader
from src.brazcar.domain.ride_listing import RideListing


@dataclass(frozen=True, slots=True)
class ListRideListings:
    reader: RideListingReader

    def execute(self, filters: RideListingsFilter) -> tuple[RideListing, ...]:
        return tuple(self.reader.list(filters))
