import { getRuntimeConfig } from "./api";
import type { RideListingEvent } from "./types";

export function subscribeToRideListingEvents(
  onRideChanged: (event: RideListingEvent) => void,
): () => void {
  const runtime = getRuntimeConfig();
  const source = new EventSource(runtime.rideListingEventsUrl);

  const handleRideChanged = (event: MessageEvent<string>) => {
    const payload = JSON.parse(event.data) as RideListingEvent;
    onRideChanged(payload);
  };

  source.addEventListener("ride_listing_changed", handleRideChanged as EventListener);

  return () => {
    source.removeEventListener("ride_listing_changed", handleRideChanged as EventListener);
    source.close();
  };
}
