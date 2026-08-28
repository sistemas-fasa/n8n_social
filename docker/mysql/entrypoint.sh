#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${FASA_SOCIAL_ENV_FILE:-/run/secrets/fasa-social.env}"
if [[ -r "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"
