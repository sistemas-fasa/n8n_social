#!/usr/bin/env sh
set -eu

ENV_FILE="${FASA_SOCIAL_ENV_FILE:-/run/secrets/fasa-social.env}"
if [ -r "$ENV_FILE" ]; then
    set -a
    . "$ENV_FILE"
    set +a
fi

exec "$@"
