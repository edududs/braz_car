import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

const NativeRequest = globalThis.Request;

class TestRequest extends NativeRequest {
  constructor(input: RequestInfo | URL, init?: RequestInit) {
    const nextInit = init && "signal" in init ? { ...init, signal: undefined } : init;
    super(input, nextInit);
  }
}

globalThis.Request = TestRequest as typeof Request;

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  document.body.innerHTML = "";
});

beforeEach(() => {
  document.body.innerHTML = `
    <div
      id="app-shell"
      data-api-base-url="/api"
      data-ride-listings-url="/api/ride-listings"
      data-ride-listing-events-url="/events/ride-listings/"
      data-current-user-url="/api/me"
    ></div>
    <div id="root"></div>
  `;
});
