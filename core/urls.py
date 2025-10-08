from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("braz_car.urls", namespace="braz_car")),
    path("users/", include("users.urls", namespace="users")),
    path("vehicles/", include("vehicles.urls", namespace="vehicles")),
    path("locations/", include("locations.urls", namespace="locations")),
    path("rides/", include("rides.urls", namespace="rides")),
]
