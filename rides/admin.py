from django.contrib import admin
from django.http import HttpRequest

from .models import Ride, RideListingRecord, RideRequest

admin.site.register(Ride)
admin.site.register(RideRequest)


@admin.register(RideListingRecord)
class RideListingRecordAdmin(admin.ModelAdmin):
    list_display = (
        "ride",
        "origin",
        "destination",
        "departure_date",
        "departure_time",
        "available_seats",
        "price",
    )
    search_fields = ("origin", "destination", "driver_name", "vehicle_model")
    list_filter = ("departure_date",)
    readonly_fields = (
        "ride",
        "origin",
        "destination",
        "available_seats",
        "price",
        "payment_methods",
        "departure_time",
        "departure_date",
        "route_stops",
        "driver_name",
        "driver_rating",
        "driver_total_rides",
        "driver_avatar",
        "vehicle_model",
        "vehicle_color",
        "restrictions",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: RideListingRecord | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: RideListingRecord | None = None) -> bool:
        return False
