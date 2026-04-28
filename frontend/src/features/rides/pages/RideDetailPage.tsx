import { Link, useParams, useSearchParams } from "react-router";
import { useEffect, useMemo, useState } from "react";

import { buildSearchParams, createDefaultFilters, fetchCurrentUser, fetchRideListings, parseFilters } from "../api";
import { RideDetail } from "../components/RideDetail";
import type { CurrentUserContext, RideListing } from "../types";

type LoadState = "loading" | "success" | "error" | "not-found";

export function RideDetailPage() {
  const { rideId } = useParams();
  const [searchParams] = useSearchParams();
  const filters = useMemo(() => parseFilters(searchParams.toString()), [searchParams]);
  const [ride, setRide] = useState<RideListing | null>(null);
  const [currentUser, setCurrentUser] = useState<CurrentUserContext | null>({
    user_id: null,
    is_authenticated: false,
  });
  const [loadState, setLoadState] = useState<LoadState>("loading");

  useEffect(() => {
    let cancelled = false;
    const numericRideId = Number(rideId);

    async function loadDetail() {
      setLoadState("loading");
      try {
        const rides = await fetchRideListings(createDefaultFilters());
        if (cancelled) {
          return;
        }

        const matchingRide = rides.find((item) => item.ride_id === numericRideId) ?? null;
        if (!matchingRide) {
          setRide(null);
          setLoadState("not-found");
          return;
        }

        setRide(matchingRide);
        setLoadState("success");

        try {
          const user = await fetchCurrentUser();
          if (!cancelled) {
            setCurrentUser(user);
          }
        } catch {
          if (!cancelled) {
            setCurrentUser({ user_id: null, is_authenticated: false });
          }
        }
      } catch {
        if (!cancelled) {
          setLoadState("error");
        }
      }
    }

    if (!Number.isFinite(numericRideId)) {
      setLoadState("not-found");
      return () => {
        cancelled = true;
      };
    }

    void loadDetail();
    return () => {
      cancelled = true;
    };
  }, [rideId]);

  const backSearch = buildSearchParams(filters).toString();

  return (
    <section className="space-y-6">
      <div>
        <Link
          className="text-sm font-semibold text-teal-700"
          to={{ pathname: "/", search: backSearch ? `?${backSearch}` : "" }}
        >
          ← Voltar para o dashboard
        </Link>
      </div>

      {loadState === "loading" ? <p className="text-sm text-gray-500">Carregando detalhes da carona...</p> : null}

      {loadState === "not-found" ? (
        <p className="rounded-lg border border-gray-200 bg-white px-4 py-6 text-sm text-gray-500">
          Carona não encontrada.
        </p>
      ) : null}

      {loadState === "error" ? (
        <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
          Não foi possível carregar a carona.
        </p>
      ) : null}

      {loadState === "success" && ride ? <RideDetail ride={ride} currentUser={currentUser} /> : null}
    </section>
  );
}
