from django.db import models


class Ride(models.Model):
    driver = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rides_as_driver")
    passenger = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="rides_as_passenger")
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="rides")
    location_start = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="rides_start")
    location_end = models.ForeignKey("locations.Location", on_delete=models.CASCADE, related_name="rides_end")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver.get_full_name()} - {self.passenger.get_full_name()}"


class RideRequest(models.Model):
    ride = models.ForeignKey("Ride", on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="ride_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.ride.driver.get_full_name()}"
