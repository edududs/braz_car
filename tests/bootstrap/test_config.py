from pathlib import Path

import pytest

from src.brazcar.bootstrap.config import load_app_config


def test_load_app_config_reads_required_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    monkeypatch.setenv("CSRF_TRUSTED_ORIGINS", "https://example.com")
    monkeypatch.delenv("DEBUG", raising=False)

    config = load_app_config()

    assert config.secret_key == "test-secret"
    assert config.python_version == "3.13"
    assert config.database_url.startswith("postgresql://postgres:")
    assert config.allowed_hosts == ["localhost", "127.0.0.1"]
    assert config.csrf_trusted_origins == ["https://example.com"]
    assert config.debug is False


def test_load_app_config_reads_debug_flag(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost")
    monkeypatch.setenv("DEBUG", "true")

    config = load_app_config()

    assert config.debug is True


def test_load_app_config_uses_debug_defaults_for_local_bootstrap(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    monkeypatch.delenv("CSRF_TRUSTED_ORIGINS", raising=False)
    monkeypatch.setenv("DEBUG", "true")

    config = load_app_config()

    expected_database_url = f"sqlite:///{(Path(__file__).resolve().parents[2] / 'db.sqlite3').as_posix()}"

    assert config.secret_key == "dev-only-secret-key-not-for-production"
    assert config.database_url == expected_database_url
    assert config.allowed_hosts == ["localhost", "127.0.0.1", "[::1]"]
    assert config.csrf_trusted_origins == []
    assert config.debug is True


def test_load_app_config_requires_secret_key_outside_debug(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.delenv("DEBUG", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_app_config()


def test_load_app_config_requires_database_url_outside_debug(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    monkeypatch.delenv("DEBUG", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        load_app_config()


def test_load_app_config_requires_allowed_hosts_outside_debug(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)

    with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
        load_app_config()


def test_load_app_config_rejects_blank_values_outside_debug(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)

    monkeypatch.setenv("SECRET_KEY", "   ")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "example.com")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        load_app_config()

    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "   ")
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        load_app_config()

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", "   ")
    with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
        load_app_config()


def test_load_app_config_rejects_empty_allowed_hosts_after_parsing(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", ", ,")
    monkeypatch.delenv("DEBUG", raising=False)

    with pytest.raises(RuntimeError, match="ALLOWED_HOSTS must include at least one hostname"):
        load_app_config()


def test_load_app_config_strips_whitespace_values(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", " test-secret ")
    monkeypatch.setenv(
        "DATABASE_URL",
        " postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres ",
    )
    monkeypatch.setenv("ALLOWED_HOSTS", " example.com , api.example.com ")
    monkeypatch.delenv("DEBUG", raising=False)

    config = load_app_config()

    assert config.secret_key == "test-secret"
    assert config.database_url == "postgresql://postgres:test@db.olkwvnkzoxhtxbpynkvj.supabase.co:5432/postgres"
    assert config.allowed_hosts == ["example.com", "api.example.com"]
