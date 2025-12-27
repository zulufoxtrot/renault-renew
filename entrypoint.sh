#!/bin/bash
# Docker entrypoint script
# Handles database migrations and starts the application

set -e

echo "🚀 Starting Renault Scraper..."

# Database path
DB_PATH="${DB_PATH:-/app/data/renault_vehicles.db}"

# Check if database exists
if [ -f "$DB_PATH" ]; then
    echo "📊 Existing database found: $DB_PATH"
    echo "🔄 Migrations will be applied automatically on startup"
else
    echo "🆕 No existing database - will be created on first run"
fi

# Start the application
echo "▶️  Starting Flask application..."
exec python app.py
