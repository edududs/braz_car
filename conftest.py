from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.testing")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///db.sqlite3")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
os.environ.setdefault("CSRF_TRUSTED_ORIGINS", "http://localhost,http://127.0.0.1")
