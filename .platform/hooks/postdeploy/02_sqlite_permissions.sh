#!/bin/bash
set -e

APP_DIR="/var/app/current"
DB="$APP_DIR/db.sqlite3"

echo "Checking SQLite database permissions..."

if [ ! -f "$DB" ]; then
    echo "SQLite database not found. Skipping permissions setup."
    exit 0
fi

chown webapp:webapp "$DB"
chmod 664 "$DB"

chgrp webapp "$APP_DIR"
chmod 775 "$APP_DIR"

for SUFFIX in -journal -wal -shm; do
    if [ -f "${DB}${SUFFIX}" ]; then
        chown webapp:webapp "${DB}${SUFFIX}"
    fi
done

echo "SQLite permissions updated successfully."
ls -l "$DB"
ls -ld "$APP_DIR"
