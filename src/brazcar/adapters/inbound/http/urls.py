from __future__ import annotations

from django.urls import path

from src.brazcar.adapters.inbound.http.api_views import api
from src.brazcar.adapters.inbound.http.page_views import app_shell
from src.brazcar.adapters.inbound.http.sse_views import ride_listing_events_stream

urlpatterns = [
    path("", app_shell, name="brazcar-app-shell"),
    path("rides/<int:ride_id>/", app_shell, name="brazcar-ride-detail-shell"),
    path("api/", api.urls),
    path("events/ride-listings/", ride_listing_events_stream, name="ride-listing-events"),
]
