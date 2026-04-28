from django.apps import AppConfig


class BrazCarConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "braz_car"

    def ready(self) -> None:
        from src.brazcar.bootstrap.runtime import start_runtime

        start_runtime()
