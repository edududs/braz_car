import type { CurrentUserContext, RideListing } from "../types";

interface RideDetailProps {
  ride: RideListing;
  currentUser: CurrentUserContext | null;
}

function formatPrice(price: string): string {
  return `R$ ${price}`;
}

function formatDateTime(ride: RideListing): string {
  const datePart = ride.departure_date ?? "Sem data definida";
  return `${datePart} às ${ride.departure_time.slice(0, 5)}`;
}

export function RideDetail({ ride, currentUser }: RideDetailProps) {
  return (
    <article className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">
          {ride.origin} → {ride.destination}
        </h1>
        <p className="text-lg text-teal-700">{formatPrice(ride.price)}</p>
        <p className="text-sm text-gray-600">{formatDateTime(ride)}</p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Motorista</h2>
          <p className="mt-2 text-lg font-semibold text-gray-900">{ride.driver.name}</p>
          <p className="text-sm text-gray-600">{ride.driver.rating} de avaliação</p>
          <p className="text-sm text-gray-600">{ride.driver.total_rides} viagens</p>
        </div>

        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Veículo</h2>
          <p className="mt-2 text-sm text-gray-700">
            {ride.vehicle ? `${ride.vehicle.model} • ${ride.vehicle.color}` : "Não informado"}
          </p>
          <p className="mt-2 text-sm text-gray-700">Vagas disponíveis: {ride.available_seats}</p>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Paradas</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
          {ride.route_stops.map((stop) => (
            <li key={stop}>{stop}</li>
          ))}
        </ul>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Pagamento</h2>
          <p className="mt-2 text-sm text-gray-700">{ride.payment_methods.join(", ")}</p>
        </div>
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Restrições</h2>
          <p className="mt-2 text-sm text-gray-700">{ride.restrictions ?? "Nenhuma restrição informada"}</p>
        </div>
      </section>

      {currentUser?.is_authenticated ? (
        <section className="rounded-xl border border-dashed border-teal-300 bg-teal-50 p-4">
          <h2 className="text-lg font-semibold text-teal-900">Ações futuras</h2>
          <p className="mt-2 text-sm text-teal-800">
            Em breve você poderá reservar e conversar por aqui.
          </p>
        </section>
      ) : null}
    </article>
  );
}
