import { render, screen } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createAppRouter } from "../../../app/router";
import type { RideListing } from "../types";

const DETAIL_RIDE: RideListing = {
  ride_id: 7,
  origin: "Brazlândia",
  destination: "Plano Piloto",
  available_seats: 3,
  price: "7.00",
  payment_methods: ["PIX", "Dinheiro"],
  departure_time: "19:30:00",
  departure_date: "2026-04-20",
  route_stops: ["Taguatinga", "Eixo Monumental"],
  driver: {
    name: "João Silva",
    rating: "4.50",
    total_rides: 127,
    avatar: null,
  },
  vehicle: {
    model: "Honda Civic",
    color: "Branco",
  },
  restrictions: "Sem animais",
};

function renderDetail(initialEntry = "/rides/7") {
  const router = createMemoryRouter(createAppRouter(), {
    initialEntries: [initialEntry],
  });

  render(<RouterProvider router={router} />);
  return router;
}

describe("RideDetailPage", () => {
  beforeEach(() => {
    vi.stubGlobal("EventSource", class {
      close(): void {
        return undefined;
      }

      addEventListener(): void {
        return undefined;
      }

      removeEventListener(): void {
        return undefined;
      }
    } as unknown as typeof EventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders ride details and hides future actions when the user is anonymous", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([DETAIL_RIDE]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: null, is_authenticated: false }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    vi.stubGlobal("fetch", fetchMock);

    renderDetail();

    expect(await screen.findByRole("heading", { name: /brazlândia → plano piloto/i })).toBeInTheDocument();
    expect(screen.getByText(/7.00/)).toBeInTheDocument();
    expect(screen.getByText(/joão silva/i)).toBeInTheDocument();
    expect(screen.getByText(/127 viagens/i)).toBeInTheDocument();
    expect(screen.getByText(/taguatinga/i)).toBeInTheDocument();
    expect(screen.getByText(/sem animais/i)).toBeInTheDocument();
    expect(screen.queryByText(/ações futuras/i)).not.toBeInTheDocument();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/ride-listings",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/me",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
  });

  it("shows the authenticated placeholder for future actions", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([DETAIL_RIDE]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: 11, is_authenticated: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    vi.stubGlobal("fetch", fetchMock);

    renderDetail();

    expect(await screen.findByText(/ações futuras/i)).toBeInTheDocument();
    expect(screen.getByText(/em breve você poderá reservar e conversar por aqui/i)).toBeInTheDocument();
  });

  it("keeps the detail page public when the auth lookup fails", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([DETAIL_RIDE]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockRejectedValueOnce(new Error("auth down"));

    vi.stubGlobal("fetch", fetchMock);

    renderDetail();

    expect(await screen.findByRole("heading", { name: /brazlândia → plano piloto/i })).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(screen.queryByText(/ações futuras/i)).not.toBeInTheDocument();
  });

  it("shows loading, not-found, and error states on the detail page", async () => {
    const notFoundFetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: null, is_authenticated: false }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    vi.stubGlobal("fetch", notFoundFetchMock);

    renderDetail("/rides/999");

    expect(screen.getByText(/carregando detalhes da carona/i)).toBeInTheDocument();
    expect(await screen.findByText(/carona não encontrada/i)).toBeInTheDocument();

    vi.unstubAllGlobals();
    vi.stubGlobal("EventSource", class {
      close(): void {
        return undefined;
      }

      addEventListener(): void {
        return undefined;
      }

      removeEventListener(): void {
        return undefined;
      }
    } as unknown as typeof EventSource);

    const errorFetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(new Response("boom", { status: 500 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ user_id: null, is_authenticated: false }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    vi.stubGlobal("fetch", errorFetchMock);

    renderDetail("/rides/7");

    expect(await screen.findByRole("alert")).toHaveTextContent(/não foi possível carregar a carona/i);
  });
});
