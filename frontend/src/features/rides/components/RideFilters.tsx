import { useEffect, useState, type FormEvent } from "react";

import type { RideDashboardFilters } from "../types";

interface RideFiltersProps {
  filters: RideDashboardFilters;
  onApply: (filters: RideDashboardFilters) => void;
}

export function RideFilters({ filters, onApply }: RideFiltersProps) {
  const [draft, setDraft] = useState<RideDashboardFilters>(filters);

  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const nextFilters: RideDashboardFilters = {
      origin: String(formData.get("origin") ?? ""),
      destination: String(formData.get("destination") ?? ""),
      departureDate: String(formData.get("departureDate") ?? ""),
      price: String(formData.get("price") ?? ""),
      seats: String(formData.get("seats") ?? ""),
    };

    setDraft(nextFilters);
    onApply(nextFilters);
  };

  return (
    <form
      aria-label="Filtrar caronas"
      className="grid gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:grid-cols-5"
      onSubmit={handleSubmit}
    >
      <label className="flex flex-col gap-2 text-sm font-medium text-gray-700">
        Origem
        <input
          className="rounded-lg border border-gray-300 px-3 py-2"
          name="origin"
          type="text"
          value={draft.origin}
          onChange={(event) => setDraft((current) => ({ ...current, origin: event.target.value }))}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-gray-700">
        Destino
        <input
          className="rounded-lg border border-gray-300 px-3 py-2"
          name="destination"
          type="text"
          value={draft.destination}
          onChange={(event) => setDraft((current) => ({ ...current, destination: event.target.value }))}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-gray-700">
        Data e hora
        <input
          className="rounded-lg border border-gray-300 px-3 py-2"
          name="departureDate"
          type="date"
          value={draft.departureDate}
          onChange={(event) => setDraft((current) => ({ ...current, departureDate: event.target.value }))}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-gray-700">
        Preço máximo
        <input
          className="rounded-lg border border-gray-300 px-3 py-2"
          inputMode="decimal"
          name="price"
          type="text"
          value={draft.price}
          onChange={(event) => setDraft((current) => ({ ...current, price: event.target.value }))}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium text-gray-700">
        Vagas mínimas
        <input
          className="rounded-lg border border-gray-300 px-3 py-2"
          inputMode="numeric"
          min="1"
          name="seats"
          type="number"
          value={draft.seats}
          onChange={(event) => setDraft((current) => ({ ...current, seats: event.target.value }))}
        />
      </label>

      <div className="md:col-span-5 flex justify-end">
        <button
          className="rounded-lg bg-teal-700 px-4 py-2 text-sm font-semibold text-white"
          type="submit"
        >
          Aplicar filtros
        </button>
      </div>
    </form>
  );
}
