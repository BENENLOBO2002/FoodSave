#!/bin/bash
set -e

cd /var/app/staging

VENV_DIR=$(find /var/app/venv -mindepth 1 -maxdepth 1 -type d -name 'staging-*' -print -quit)

if [ -z "$VENV_DIR" ]; then
    echo "ERROR: Python virtual environment not found"
    exit 1
fi

"$VENV_DIR/bin/python" manage.py collectstatic --noinput
