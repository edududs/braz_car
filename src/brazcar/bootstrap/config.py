from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

_DEV_SECRET_KEY = "dev-only-secret-key-not-for-production"
_DEV_DATABASE_PATH = Path(__file__).resolve().parents[3] / "db.sqlite3"
_DEV_ALLOWED_HOSTS = "localhost,127.0.0.1,[::1]"


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


def _is_debug_enabled() -> bool:
    return os.getenv("DEBUG", "false").strip().lower() == "true"


def _local_database_url() -> str:
    return f"sqlite:///{_DEV_DATABASE_PATH.as_posix()}"


def _read_setting(name: str, *, debug: bool, dev_default: str | None = None) -> str:
    value = os.getenv(name)
    if value is not None:
        trimmed_value = value.strip()
        if trimmed_value:
            return trimmed_value
    if debug and dev_default is not None:
        return dev_default
    raise RuntimeError(f"{name} must be set unless DEBUG=true for local development.")


def load_app_config() -> AppConfig:
    debug = _is_debug_enabled()
    allowed_hosts = _split_csv(
        _read_setting("ALLOWED_HOSTS", debug=debug, dev_default=_DEV_ALLOWED_HOSTS)
    )
    if not allowed_hosts:
        raise RuntimeError("ALLOWED_HOSTS must include at least one hostname.")
    return AppConfig(
        secret_key=_read_setting("SECRET_KEY", debug=debug, dev_default=_DEV_SECRET_KEY),
        database_url=_read_setting("DATABASE_URL", debug=debug, dev_default=_local_database_url()),
        allowed_hosts=allowed_hosts,
        csrf_trusted_origins=_split_csv(os.getenv("CSRF_TRUSTED_ORIGINS", "")),
        debug=debug,
    )
