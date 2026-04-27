from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    secret_key: str
    database_url: str
    allowed_hosts: list[str]
    csrf_trusted_origins: list[str]
    debug: bool
    python_version: str = "3.13"


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_app_config() -> AppConfig:
    return AppConfig(
        secret_key=os.environ["SECRET_KEY"],
        database_url=os.environ["DATABASE_URL"],
        allowed_hosts=_split_csv(os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")),
        csrf_trusted_origins=_split_csv(os.getenv("CSRF_TRUSTED_ORIGINS", "")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )
