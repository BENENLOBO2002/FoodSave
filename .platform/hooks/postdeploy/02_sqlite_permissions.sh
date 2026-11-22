
#!/bin/bash
set -e

APP_DIR="/var/app/current"
DB="$APP_DIR/db.sqlite3"

echo "Fixing SQLite permissions..."

if [ ! -f "$DB" ]; then
    echo "ERROR: SQLite database not found at $DB"
    exit 1
fi

# Allow the webapp process to write to the database
chown webapp:webapp "$DB"
chmod 664 "$DB"

# Allow SQLite to create journal/WAL files in the application directory
chgrp webapp "$APP_DIR"
chmod 775 "$APP_DIR"

echo "SQLite permissions updated successfully."
ls -l "$DB"
ls -ld "$APP_DIR"
