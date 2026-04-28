from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.brazcar.bootstrap.container import get_container


def app_shell(request: HttpRequest, **_: Any) -> HttpResponse:
    get_container()
    return render(
        request,
        "app_shell.html",
        {
            "api_base_url": "/api",
            "ride_listings_url": "/api/ride-listings",
            "ride_listing_events_url": "/events/ride-listings/",
            "current_user_url": "/api/me",
        },
    )
