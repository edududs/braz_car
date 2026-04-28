import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createAppRouter } from "../../../app/router";
import type { RideListing } from "../types";

class EventSourceStub {
  static instances: EventSourceStub[] = [];

  readonly url: string;
  readonly listeners = new Map<string, Set<(event: MessageEvent<string>) => void>>();
  closed = false;

  constructor(url: string) {
    this.url = url;
    EventSourceStub.instances.push(this);
  }

  addEventListener(type: string, listener: (event: MessageEvent<string>) => void): void {
    const handlers = this.listeners.get(type) ?? new Set();
    handlers.add(listener);
    this.listeners.set(type, handlers);
  }

  removeEventListener(type: string, listener: (event: MessageEvent<string>) => void): void {
    this.listeners.get(type)?.delete(listener);
  }

  close(): void {
    this.closed = true;
  }

  dispatch(type: string, payload: unknown): void {
    const event = { data: JSON.stringify(payload) } as MessageEvent<string>;
    this.listeners.get(type)?.forEach((listener) => listener(event));
  }
}

const FIRST_RIDE: RideListing = {
  ride_id: 7,
  origin: "Brazlândia",
  destination: "Plano Piloto",
  available_seats: 3,
  price: "7.00",
  payment_methods: ["PIX", "Dinheiro"],
  departure_time: "19:30:00",
  departure_date: "2026-04-20",
  route_stops: ["Taguatinga"],
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

const SECOND_RIDE: RideListing = {
  ride_id: 9,
  origin: "Ceilândia",
  destination: "Asa Sul",
  available_seats: 2,
  price: "12.50",
  payment_methods: ["PIX"],
  departure_time: "08:15:00",
  departure_date: "2026-04-21",
  route_stops: ["Taguatinga", "Eixo Monumental"],
  driver: {
    name: "Maria Souza",
    rating: "4.90",
    total_rides: 212,
    avatar: null,
  },
  vehicle: {
    model: "Gol",
    color: "Prata",
  },
  restrictions: null,
};

function renderDashboard(initialEntry = "/") {
  const router = createMemoryRouter(createAppRouter(), {
    initialEntries: [initialEntry],
  });

  render(<RouterProvider router={router} />);
  return router;
}

function createDeferredResponse(data: RideListing[]) {
  let resolvePromise: ((value: Response) => void) | undefined;
  const promise = new Promise<Response>((resolve) => {
    resolvePromise = resolve;
  });

  return {
    promise,
    resolve() {
      resolvePromise?.(
        new Response(JSON.stringify(data), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    },
  };
}

describe("RideDashboardPage", () => {
  beforeEach(() => {
    EventSourceStub.instances = [];
    vi.stubGlobal("EventSource", EventSourceStub as unknown as typeof EventSource);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads the dashboard, preserves URL filters, and refreshes results after SSE without clearing filters", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([FIRST_RIDE]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify([FIRST_RIDE, SECOND_RIDE]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    vi.stubGlobal("fetch", fetchMock);

    renderDashboard(
      "/?origin=Brazl%C3%A2ndia&destination=Plano+Piloto&departureDate=2026-04-20&price=7.00&seats=3",
    );

    expect(screen.getByText(/carregando caronas/i)).toBeInTheDocument();

    expect(await screen.findByRole("heading", { name: /caronas disponíveis/i })).toBeInTheDocument();
    expect(screen.getByDisplayValue("Brazlândia")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Plano Piloto")).toBeInTheDocument();
    expect(screen.getByDisplayValue("2026-04-20")).toBeInTheDocument();
    expect(screen.getByDisplayValue("7.00")).toBeInTheDocument();
    expect(screen.getByDisplayValue("3")).toBeInTheDocument();
    expect(screen.getByText(/joão silva/i)).toBeInTheDocument();
    expect(screen.getByText(/r\$ 7.00/i)).toBeInTheDocument();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "/api/ride-listings?origin=Brazl%C3%A2ndia&destination=Plano+Piloto&departure_date=2026-04-20&price=7.00&seats=3",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );

    const events = EventSourceStub.instances.at(0);
    expect(events?.url).toBe("/events/ride-listings/");

    events?.dispatch("ride_listing_changed", {
      event_type: "ride_listing_changed",
      ride_id: SECOND_RIDE.ride_id,
    });

    await screen.findByText(/maria souza/i);
    expect(screen.getByDisplayValue("Brazlândia")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Plano Piloto")).toBeInTheDocument();
    expect(screen.getByDisplayValue("2026-04-20")).toBeInTheDocument();
    expect(screen.getByDisplayValue("7.00")).toBeInTheDocument();
    expect(screen.getByDisplayValue("3")).toBeInTheDocument();

    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/ride-listings?origin=Brazl%C3%A2ndia&destination=Plano+Piloto&departure_date=2026-04-20&price=7.00&seats=3",
      expect.objectContaining({ headers: { Accept: "application/json" } }),
    );
  });

  it("shows empty and error states for the dashboard", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      )
      .mockResolvedValueOnce(new Response("boom", { status: 500 }));

    vi.stubGlobal("fetch", fetchMock);

    renderDashboard();

    expect(await screen.findByText(/nenhuma carona encontrada/i)).toBeInTheDocument();

    renderDashboard("/?origin=Gama");

    expect(await screen.findByRole("alert")).toHaveTextContent(/não foi possível carregar as caronas/i);
  });

  it("updates URL params when filters are submitted", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify([FIRST_RIDE]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    vi.stubGlobal("fetch", fetchMock);

    const router = renderDashboard();

    await screen.findByText(/joão silva/i);

    const filters = screen.getByRole("form", { name: /filtrar caronas/i });
    const originInput = within(filters).getByLabelText(/origem/i);
    const destinationInput = within(filters).getByLabelText(/destino/i);
    const dateInput = within(filters).getByLabelText(/data e hora/i);
    const priceInput = within(filters).getByLabelText(/preço máximo/i);
    const seatsInput = within(filters).getByLabelText(/vagas mínimas/i);

    fireEvent.change(originInput, { target: { value: "Gama" } });
    fireEvent.change(destinationInput, { target: { value: "Asa Norte" } });
    fireEvent.change(dateInput, { target: { value: "2026-04-30" } });
    fireEvent.change(priceInput, { target: { value: "1.000,00" } });
    fireEvent.change(seatsInput, { target: { value: "2" } });

    fireEvent.submit(filters);

    await waitFor(() => {
      expect(router.state.location.search).toContain("origin=Gama");
      expect(router.state.location.search).toContain("destination=Asa+Norte");
      expect(router.state.location.search).toContain("departureDate=2026-04-30");
      expect(router.state.location.search).toContain("price=1000.00");
      expect(router.state.location.search).toContain("seats=2");
    });

    await waitFor(() => {
      expect(fetchMock).toHaveBeenLastCalledWith(
        "/api/ride-listings?origin=Gama&destination=Asa+Norte&departure_date=2026-04-30&price=1000.00&seats=2",
        expect.objectContaining({ headers: { Accept: "application/json" } }),
      );
    });
  });

  it("ignores stale listing responses that resolve after a newer request", async () => {
    const firstDeferred = createDeferredResponse([FIRST_RIDE]);
    const secondDeferred = createDeferredResponse([SECOND_RIDE]);

    const fetchMock = vi
      .fn<typeof fetch>()
      .mockImplementationOnce(() => firstDeferred.promise)
      .mockImplementationOnce(() => secondDeferred.promise);

    vi.stubGlobal("fetch", fetchMock);

    const router = renderDashboard("/?origin=Brazl%C3%A2ndia");

    const filters = await screen.findByRole("form", { name: /filtrar caronas/i });
    const originInput = within(filters).getByLabelText(/origem/i);
    fireEvent.change(originInput, { target: { value: "Ceilândia" } });
    fireEvent.submit(filters);

    await waitFor(() => {
      expect(router.state.location.search).toContain("origin=Ceil%C3%A2ndia");
    });

    await act(async () => {
      secondDeferred.resolve();
    });

    expect(await screen.findByText(/maria souza/i)).toBeInTheDocument();
    expect(screen.queryByText(/joão silva/i)).not.toBeInTheDocument();

    await act(async () => {
      firstDeferred.resolve();
    });

    await waitFor(() => {
      expect(screen.getByText(/maria souza/i)).toBeInTheDocument();
      expect(screen.queryByText(/joão silva/i)).not.toBeInTheDocument();
    });
  });
});
