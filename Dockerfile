FROM node:22-bookworm-slim AS frontend-build
WORKDIR /app
COPY package.json yarn.lock ./
COPY frontend ./frontend
COPY static ./static
COPY vite.config.mjs ./
RUN corepack enable && yarn install --frozen-lockfile && yarn build

FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
COPY --from=frontend-build /app/assets ./assets

RUN chmod +x ./scripts/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=core.settings \
    PORT=10000 \
    STATIC_ROOT=/app/staticfiles \
    MEDIA_ROOT=/app/media

RUN mkdir -p "$STATIC_ROOT" "$MEDIA_ROOT"
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 10000

ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD []
