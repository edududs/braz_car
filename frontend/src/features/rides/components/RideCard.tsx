import { Link, createSearchParams } from "react-router";

import type { RideDashboardFilters, RideListing } from "../types";

interface RideCardProps {
  ride: RideListing;
  filters: RideDashboardFilters;
}

function formatPrice(price: string): string {
  return `R$ ${price}`;
}

function formatDateTime(ride: RideListing): string {
  const datePart = ride.departure_date ?? "Sem data definida";
  const timePart = ride.departure_time.slice(0, 5);
  return `${datePart} às ${timePart}`;
}

export function RideCard({ ride, filters }: RideCardProps) {
  const search = createSearchParams(
    Object.entries(filters).filter(([, value]) => value.trim() !== ""),
  ).toString();

  return (
    <article className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            {ride.origin} → {ride.destination}
          </h2>
          <p className="mt-1 text-sm text-gray-600">{formatDateTime(ride)}</p>
        </div>
        <p className="text-lg font-semibold text-teal-700">{formatPrice(ride.price)}</p>
      </div>

      <dl className="mt-4 grid gap-3 text-sm text-gray-700 md:grid-cols-2">
        <div>
          <dt className="font-semibold">Motorista</dt>
          <dd>{ride.driver.name}</dd>
        </div>
        <div>
          <dt className="font-semibold">Vagas</dt>
          <dd>{ride.available_seats}</dd>
        </div>
        <div>
          <dt className="font-semibold">Pagamentos</dt>
          <dd>{ride.payment_methods.join(", ")}</dd>
        </div>
        <div>
          <dt className="font-semibold">Paradas</dt>
          <dd>{ride.route_stops.length > 0 ? ride.route_stops.join(", ") : "Sem paradas"}</dd>
        </div>
      </dl>

      <div className="mt-4 flex items-center justify-between gap-3">
        <p className="text-sm text-gray-500">
          {ride.driver.rating} de avaliação • {ride.driver.total_rides} viagens
        </p>
        <Link
          className="rounded-lg border border-teal-700 px-4 py-2 text-sm font-semibold text-teal-700"
          to={{
            pathname: `/rides/${ride.ride_id}`,
            search: search ? `?${search}` : "",
          }}
        >
          Ver detalhes
        </Link>
      </div>
    </article>
  );
}
