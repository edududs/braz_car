from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50, default="Brasília")
    state = models.CharField(max_length=2, default="DF")
    reference = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Address(models.Model):
    neighborhood = models.CharField(max_length=100, default="Brasília")
    street = models.CharField(max_length=100, default="Brasília")
    number = models.CharField(max_length=10, default="Brasília")
    complement = models.CharField(max_length=100, default="Brasília")
    zip_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.neighborhood}, {self.street}, {self.number}, {self.complement}, {self.zip_code}"
