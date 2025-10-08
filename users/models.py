from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=15)
    birth_date = models.DateField()
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.ForeignKey("locations.Address", on_delete=models.CASCADE, related_name="users", null=True)

    def __str__(self):
        return self.get_full_name().capitalize()

    def clean(self):
        super().clean()
        from utils.validations.cpf import normalize_cpf, validate_cpf

        validate_cpf(self.cpf)
        self.cpf = normalize_cpf(self.cpf)

    def get_rating_as_driver(self): ...

    def get_rating_as_passenger(self): ...
