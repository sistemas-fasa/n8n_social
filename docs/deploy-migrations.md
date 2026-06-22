# Deploy migrations

This project uses Alembic for schema changes. Deploys should keep application
containers and the database revision in sync without running ad hoc SQL.

## Scope

This runbook covers the repeatable migration step for the Docker deployment. It
does not deploy new images, restart services, publish social content, or call n8n.

## Before running

- Confirm the branch or release being deployed is already present on the server.
- Confirm the server `.env` has the intended MySQL and port values.
- Confirm the backend image includes `backend/alembic` and `backend/alembic.ini`.
- Do not run against production from a developer machine with copied secrets.

## Standard command

On `fasa_195`, run:

```bash
cd /opt/fasa-social-dashboard
./scripts/run-migrations.sh
```

If the backend is published on the validated alternate port:

```bash
cd /opt/fasa-social-dashboard
BACKEND_PORT=18080 ./scripts/run-migrations.sh
```

The script performs these steps:

1. Validates `docker compose config`.
2. Prints Alembic heads.
3. Prints the currently deployed revision if the database is already stamped.
4. Skips `alembic upgrade head` when the current revision already reports `(head)`.
5. Runs `alembic upgrade head` inside the backend container only when needed.
6. Prints the revision after upgrade when migrations were applied.
7. Checks backend `/health` when `curl` is available.

## Manual equivalent

Use this only when the script is unavailable:

```bash
cd /opt/fasa-social-dashboard
docker compose config >/dev/null
docker compose exec -T backend alembic heads
docker compose exec -T backend alembic current || true
# Run only when the current revision is not already marked as (head).
docker compose exec -T backend alembic upgrade head
docker compose exec -T backend alembic current
curl --fail --silent --show-error http://localhost:${BACKEND_PORT:-8000}/health >/dev/null
```

## Rollback note

The current policy is forward-only migration deploys. If a migration fails, stop
the deploy and inspect the Alembic error before changing services. Do not run a
downgrade in production unless a separate rollback plan names the exact revision
and database impact.

## PR checklist

For PRs that add or change migrations:

- Run backend tests.
- Run `python -m alembic upgrade head --sql` from `backend`.
- Run `docker compose config`.
- Mention whether the migration is forward-only and whether it needs downtime.
