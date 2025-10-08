from django.db import models


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("car", "Carro"),
        ("motorcycle", "Moto"),
        ("van", "Van"),
    ]

    owner = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="vehicles")
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    plate = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.plate}"
