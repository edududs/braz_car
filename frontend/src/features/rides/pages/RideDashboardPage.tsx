import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router";

import {
  buildSearchParams,
  createDefaultFilters,
  fetchRideListings,
  parseFilters,
} from "../api";
import { RideCard } from "../components/RideCard";
import { RideFilters } from "../components/RideFilters";
import { subscribeToRideListingEvents } from "../sse";
import type { RideDashboardFilters, RideListing } from "../types";

type LoadState = "idle" | "loading" | "success" | "error";

export function RideDashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const filters = useMemo(() => parseFilters(searchParams.toString()), [searchParams]);
  const [rides, setRides] = useState<RideListing[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const requestSequence = useRef(0);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      const currentRequest = ++requestSequence.current;
      setLoadState("loading");
      try {
        const nextRides = await fetchRideListings(filters);
        if (!cancelled && currentRequest === requestSequence.current) {
          setRides(nextRides);
          setLoadState("success");
        }
      } catch {
        if (!cancelled && currentRequest === requestSequence.current) {
          setLoadState("error");
        }
      }
    }

    void loadDashboard();
    return () => {
      cancelled = true;
    };
  }, [filters]);

  useEffect(() => {
    let cancelled = false;

    const unsubscribe = subscribeToRideListingEvents(() => {
      const currentRequest = ++requestSequence.current;
      void fetchRideListings(filters)
        .then((nextRides) => {
          if (!cancelled && currentRequest === requestSequence.current) {
            setRides(nextRides);
            setLoadState("success");
          }
        })
        .catch(() => {
          if (!cancelled && currentRequest === requestSequence.current) {
            setLoadState("error");
          }
        });
    });

    return () => {
      cancelled = true;
      unsubscribe();
    };
  }, [filters]);

  const handleApplyFilters = (nextFilters: RideDashboardFilters) => {
    const nextSearchParams = buildSearchParams(nextFilters);
    setSearchParams(nextSearchParams, { replace: false });
  };

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal-700">BrazCar</p>
        <h1 className="text-3xl font-bold text-gray-900">Caronas disponíveis</h1>
        <p className="text-base text-gray-600">
          Explore rotas públicas do DF sem perder seus filtros enquanto novas caronas entram no ar.
        </p>
      </header>

      <RideFilters filters={filters ?? createDefaultFilters()} onApply={handleApplyFilters} />

      {loadState === "loading" ? <p className="text-sm text-gray-500">Carregando caronas...</p> : null}

      {loadState === "error" ? (
        <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          Não foi possível carregar as caronas.
        </p>
      ) : null}

      {loadState === "success" && rides.length === 0 ? (
        <p className="rounded-lg border border-gray-200 bg-white px-4 py-6 text-sm text-gray-500">
          Nenhuma carona encontrada.
        </p>
      ) : null}

      {loadState === "success" && rides.length > 0 ? (
        <div className="grid gap-4">
          {rides.map((ride) => (
            <RideCard key={ride.ride_id} ride={ride} filters={filters} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
