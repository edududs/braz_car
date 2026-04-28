#!/usr/bin/env sh
set -eu

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput

if [ "$#" -eq 0 ]; then
  set -- granian --interface asginl --host 0.0.0.0 --port "${PORT:-10000}" core.asgi:application
fi

exec "$@"
