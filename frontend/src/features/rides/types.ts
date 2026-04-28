export interface RideDriver {
  name: string;
  rating: string;
  total_rides: number;
  avatar: string | null;
}

export interface RideVehicle {
  model: string;
  color: string;
}

export interface RideListing {
  ride_id: number;
  origin: string;
  destination: string;
  available_seats: number;
  price: string;
  payment_methods: string[];
  departure_time: string;
  departure_date: string | null;
  route_stops: string[];
  driver: RideDriver;
  vehicle: RideVehicle | null;
  restrictions: string | null;
}

export interface CurrentUserContext {
  user_id: number | null;
  is_authenticated: boolean;
}

export interface RideListingEvent {
  event_type: string;
  ride_id: number;
}

export interface RideRuntimeConfig {
  apiBaseUrl: string;
  rideListingsUrl: string;
  rideListingEventsUrl: string;
  currentUserUrl: string;
}

export interface RideDashboardFilters {
  origin: string;
  destination: string;
  departureDate: string;
  price: string;
  seats: string;
}
