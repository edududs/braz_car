import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "../../static/css/main.css";
import { App } from "./app/App";

const rootElement = document.getElementById("app-shell");

if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}
