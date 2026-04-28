from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")
os.environ.setdefault("GRANIAN_APP", "core.asgi:application")

application = get_asgi_application()
