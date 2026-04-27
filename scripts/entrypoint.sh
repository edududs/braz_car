#!/bin/sh
set -eu

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi

if [ "${PORT:-8000}" != "8000" ] && [ "$#" -ge 7 ] && [ "$1" = "granian" ]; then
  set -- granian --interface wsgi core.wsgi:application --host 0.0.0.0 --port "${PORT}"
fi

exec "$@"
