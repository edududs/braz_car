import type {
  CurrentUserContext,
  RideDashboardFilters,
  RideListing,
  RideRuntimeConfig,
} from "./types";

const JSON_HEADERS = { Accept: "application/json" };
const DEFAULT_PRICE = "7.00";

export function getRuntimeConfig(): RideRuntimeConfig {
  const shell = document.getElementById("app-shell");
  const dataset = shell?.dataset;

  return {
    apiBaseUrl: dataset?.apiBaseUrl ?? "/api",
    rideListingsUrl: dataset?.rideListingsUrl ?? "/api/ride-listings",
    rideListingEventsUrl: dataset?.rideListingEventsUrl ?? "/events/ride-listings/",
    currentUserUrl: dataset?.currentUserUrl ?? "/api/me",
  };
}

export function createDefaultFilters(): RideDashboardFilters {
  return {
    origin: "",
    destination: "",
    departureDate: "",
    price: "",
    seats: "",
  };
}

export function parseFilters(search: string): RideDashboardFilters {
  const params = new URLSearchParams(search);
  return {
    origin: params.get("origin") ?? "",
    destination: params.get("destination") ?? "",
    departureDate: params.get("departureDate") ?? "",
    price: params.get("price") ?? "",
    seats: params.get("seats") ?? "",
  };
}

export function buildSearchParams(filters: RideDashboardFilters): URLSearchParams {
  const params = new URLSearchParams();

  if (filters.origin.trim()) {
    params.set("origin", filters.origin.trim());
  }
  if (filters.destination.trim()) {
    params.set("destination", filters.destination.trim());
  }
  if (filters.departureDate.trim()) {
    params.set("departureDate", filters.departureDate.trim());
  }
  const normalizedPrice = normalizePrice(filters.price);
  if (normalizedPrice) {
    params.set("price", normalizedPrice);
  }
  if (filters.seats.trim()) {
    params.set("seats", filters.seats.trim());
  }

  return params;
}

export async function fetchRideListings(filters: RideDashboardFilters): Promise<RideListing[]> {
  const runtime = getRuntimeConfig();
  const url = new URL(runtime.rideListingsUrl, window.location.origin);

  if (filters.origin.trim()) {
    url.searchParams.set("origin", filters.origin.trim());
  }
  if (filters.destination.trim()) {
    url.searchParams.set("destination", filters.destination.trim());
  }
  if (filters.departureDate.trim()) {
    url.searchParams.set("departure_date", filters.departureDate.trim());
  }
  const normalizedPrice = normalizePrice(filters.price);
  if (normalizedPrice) {
    url.searchParams.set("price", normalizedPrice);
  }
  if (filters.seats.trim()) {
    url.searchParams.set("seats", filters.seats.trim());
  }

  const response = await fetch(`${url.pathname}${url.search}`, {
    headers: JSON_HEADERS,
  });

  if (!response.ok) {
    throw new Error("Failed to load ride listings");
  }

  const payload = (await response.json()) as RideListing[];
  return payload.map(normalizeRideListing);
}

export async function fetchCurrentUser(): Promise<CurrentUserContext> {
  const runtime = getRuntimeConfig();
  const response = await fetch(runtime.currentUserUrl, {
    headers: JSON_HEADERS,
  });

  if (!response.ok) {
    throw new Error("Failed to load current user");
  }

  return (await response.json()) as CurrentUserContext;
}

function normalizeRideListing(listing: RideListing): RideListing {
  return {
    ...listing,
    price: listing.price?.trim() ? listing.price : DEFAULT_PRICE,
  };
}

function normalizePrice(value: string): string {
  const trimmed = value.trim();
  if (!trimmed.includes(",")) {
    return trimmed;
  }
  return trimmed.replaceAll(".", "").replace(",", ".");
}
