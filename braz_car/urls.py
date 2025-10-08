from django.urls import path

from . import views

app_name = "braz_car"

urlpatterns = [
    path("", views.index, name="index"),
]
