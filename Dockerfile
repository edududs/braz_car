# syntax=docker/dockerfile:1.7

FROM node:22-bookworm-slim AS frontend-deps

WORKDIR /app

COPY package.json yarn.lock ./
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile


FROM frontend-deps AS frontend-build

COPY vite.config.mjs ./
COPY static ./static
COPY frontend ./frontend
COPY braz_car/templates ./braz_car/templates
COPY locations/templates ./locations/templates
COPY rides/templates ./rides/templates
COPY users/templates ./users/templates
COPY vehicles/templates ./vehicles/templates
COPY templates ./templates
RUN yarn build


FROM python:3.13-slim AS python-deps

WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install --require-hashes -r requirements.txt


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings.production \
    PORT=8000

WORKDIR /app

COPY --from=python-deps /install /usr/local

RUN useradd --create-home --shell /usr/sbin/nologin appuser
RUN mkdir -p /app/staticfiles \
    && chown appuser:appuser /app/staticfiles

COPY --chown=appuser:appuser . .
COPY --chown=appuser:appuser --from=frontend-build /app/assets ./assets

USER appuser

RUN SECRET_KEY=build-only \
    DATABASE_URL=sqlite:///build.sqlite3 \
    DEBUG=false \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["granian", "--interface", "wsgi", "core.wsgi:application", "--host", "0.0.0.0", "--port", "8000"]
