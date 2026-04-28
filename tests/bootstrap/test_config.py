from pathlib import Path
import os
import subprocess
import time

import pytest

from src.brazcar.bootstrap.config import load_app_config

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


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


def test_runtime_artifacts_exist():
    dockerfile = _PROJECT_ROOT / "Dockerfile"
    entrypoint = _PROJECT_ROOT / "scripts" / "entrypoint.sh"
    render_descriptor = _PROJECT_ROOT / "render.yaml"

    assert dockerfile.exists()
    dockerfile_text = dockerfile.read_text(encoding="utf-8")
    assert "FROM node:22-bookworm-slim AS frontend-build" in dockerfile_text
    assert "FROM python:3.13-slim AS runtime" in dockerfile_text
    assert "corepack enable && yarn install --frozen-lockfile && yarn build" in dockerfile_text
    assert "COPY --from=frontend-build /app/assets ./assets" in dockerfile_text
    assert 'ENTRYPOINT ["./scripts/entrypoint.sh"]' in dockerfile_text
    assert 'CMD []' in dockerfile_text
    assert 'ENV PATH="/app/.venv/bin:$PATH" \\' in dockerfile_text
    assert 'DJANGO_SETTINGS_MODULE=core.settings \\' in dockerfile_text
    assert 'PORT=10000 \\' in dockerfile_text
    assert 'STATIC_ROOT=/app/staticfiles \\' in dockerfile_text
    assert 'MEDIA_ROOT=/app/media' in dockerfile_text
    assert 'RUN mkdir -p "$STATIC_ROOT" "$MEDIA_ROOT"' in dockerfile_text
    assert 'chown -R appuser:appuser /app' in dockerfile_text
    assert 'USER appuser' in dockerfile_text

    assert entrypoint.exists()
    entrypoint_text = entrypoint.read_text(encoding="utf-8")
    assert entrypoint_text.startswith("#!/usr/bin/env sh\n")
    assert "uv run python manage.py migrate --noinput" in entrypoint_text
    assert 'set -- granian --interface asginl --host 0.0.0.0 --port "${PORT:-10000}" core.asgi:application' in entrypoint_text
    assert 'exec "$@"' in entrypoint_text

    assert render_descriptor.exists()
    render_text = render_descriptor.read_text(encoding="utf-8")
    assert "runtime: docker" in render_text
    assert "dockerfilePath: ./Dockerfile" in render_text
    assert "healthCheckPath: /" in render_text
    assert "SECRET_KEY" in render_text
    assert "DATABASE_URL" in render_text
    assert "ALLOWED_HOSTS" in render_text
    assert "CSRF_TRUSTED_ORIGINS" in render_text

    asgi_text = (_PROJECT_ROOT / "core" / "asgi.py").read_text(encoding="utf-8")
    assert "os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"core.settings.production\")" in asgi_text
    assert "os.environ.setdefault(\"GRANIAN_APP\", \"core.asgi:application\")" in asgi_text
    assert "application = get_asgi_application()" in asgi_text


def test_runtime_entrypoint_and_granian_command_are_executable():
    entrypoint = _PROJECT_ROOT / "scripts" / "entrypoint.sh"
    assert entrypoint.exists()
    assert os.access(entrypoint, os.X_OK)

    dockerfile_text = (_PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    entrypoint_text = (_PROJECT_ROOT / "scripts" / "entrypoint.sh").read_text(encoding="utf-8")
    assert "core.asgi:application" in entrypoint_text
    assert "granian" in entrypoint_text
    assert '${PORT:-10000}' in entrypoint_text
    assert '/app/.venv/bin:$PATH' in dockerfile_text


def test_runtime_entrypoint_smoke_starts_granian():
    entrypoint = _PROJECT_ROOT / "scripts" / "entrypoint.sh"
    env = os.environ.copy()
    env.update(
        {
            "DEBUG": "true",
            "ALLOWED_HOSTS": "localhost",
            "PORT": "10001",
            "PATH": f"{_PROJECT_ROOT / '.venv' / 'bin'}:{env.get('PATH', '')}",
        }
    )

    process = subprocess.Popen(
        [str(entrypoint)],
        cwd=_PROJECT_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output = ""
    try:
        deadline = time.time() + 10
        while time.time() < deadline:
            assert process.stdout is not None
            line = process.stdout.readline()
            if line:
                output += line
                if "Listening at: http://0.0.0.0:10001" in output:
                    break
            elif process.poll() is not None:
                break
        assert "Listening at: http://0.0.0.0:10001" in output
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
