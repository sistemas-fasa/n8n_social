#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${FASA_SOCIAL_ENV_FILE:-/run/secrets/fasa-social.env}"
if [[ -r "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

exec mysqladmin ping -h 127.0.0.1 -u root -p"${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD is required}"
