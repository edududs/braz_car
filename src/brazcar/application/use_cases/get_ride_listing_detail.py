from __future__ import annotations

from dataclasses import dataclass

from src.brazcar.application.dto import RideListingDetailQuery
from src.brazcar.application.ports import RideListingReader
from src.brazcar.domain.ride_listing import RideListing


class RideListingNotFoundError(LookupError):
    pass


@dataclass(frozen=True, slots=True)
class GetRideListingDetail:
    reader: RideListingReader

    def execute(self, query: RideListingDetailQuery) -> RideListing:
        listing = self.reader.get_by_ride_id(query.ride_id)
        if listing is None:
            raise RideListingNotFoundError(f"Ride listing {query.ride_id} was not found")
        return listing
