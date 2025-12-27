#!/usr/bin/env python3
"""
Database Migration Script
Adds latitude and longitude columns to existing databases
"""

import sqlite3
import os


def migrate_database(db_path='renault_vehicles.db'):
    """Add latitude and longitude columns if they don't exist"""

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False

    print(f"🔧 Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = [column[1] for column in cursor.fetchall()]

        needs_migration = False

        if 'latitude' not in columns:
            print("   Adding 'latitude' column...")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN latitude REAL")
            needs_migration = True

        if 'longitude' not in columns:
            print("   Adding 'longitude' column...")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN longitude REAL")
            needs_migration = True

        if needs_migration:
            conn.commit()
            print("✅ Migration completed successfully!")
            print("ℹ️  Run the scraper again to populate coordinates for existing vehicles.")
        else:
            print("✅ Database already up to date - no migration needed.")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    # Migrate both possible database locations
    paths = [
        'renault_vehicles.db',
        '/app/data/renault_vehicles.db'
    ]

    for path in paths:
        if os.path.exists(path):
            migrate_database(path)
