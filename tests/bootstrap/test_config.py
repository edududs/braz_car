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
    monkeypatch.setenv("DEBUG", "true")

    config = load_app_config()

    assert config.debug is True
