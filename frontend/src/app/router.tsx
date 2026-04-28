import { type RouteObject } from "react-router";

import { RideDashboardPage } from "../features/rides/pages/RideDashboardPage";
import { RideDetailPage } from "../features/rides/pages/RideDetailPage";

export function createAppRouter(): RouteObject[] {
  return [
    {
      path: "/",
      element: <RideDashboardPage />,
    },
    {
      path: "/rides/:rideId",
      element: <RideDetailPage />,
    },
  ];
}
