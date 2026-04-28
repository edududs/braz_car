import { RouterProvider, createBrowserRouter } from "react-router";

import { createAppRouter } from "./router";

const router = createBrowserRouter(createAppRouter());

export function App() {
  return <RouterProvider router={router} />;
}
