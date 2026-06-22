#!/usr/bin/env sh
set -eu

PROJECT_DIR="${PROJECT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
BACKEND_SERVICE="${BACKEND_SERVICE:-backend}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
BACKEND_HEALTH_URL="${BACKEND_HEALTH_URL:-http://localhost:${BACKEND_PORT}/health}"

cd "$PROJECT_DIR"

echo "==> Validating Docker Compose config"
docker compose -f "$COMPOSE_FILE" config >/dev/null

echo "==> Current Alembic heads"
docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" alembic heads

echo "==> Current deployed Alembic revision"
CURRENT_REVISION="$(docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" alembic current || true)"
printf '%s\n' "$CURRENT_REVISION"

case "$CURRENT_REVISION" in
  *"(head)"*)
    echo "==> Database already at Alembic head; skipping upgrade"
    ;;
  *)
    echo "==> Applying Alembic migrations"
    docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" alembic upgrade head

    echo "==> Deployed Alembic revision after upgrade"
    docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" alembic current
    ;;
esac

if command -v curl >/dev/null 2>&1; then
  echo "==> Backend health check: $BACKEND_HEALTH_URL"
  curl --fail --silent --show-error "$BACKEND_HEALTH_URL" >/dev/null
else
  echo "==> curl not available; skipping backend HTTP health check"
fi

echo "==> Migration deploy step completed"
