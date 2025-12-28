#!/usr/bin/env python3
"""
Database schema migration script
Checks and upgrades existing databases to the correct schema
"""

import sqlite3
import os
from datetime import datetime


def migrate_database(db_path: str):
    """Migrate database to latest schema"""
    print(f"🔍 Checking database schema at: {db_path}")

    if not os.path.exists(db_path):
        print(f"✅ Database doesn't exist yet, it will be created with correct schema on first run")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if vehicles table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles'")
        if not cursor.fetchone():
            print("❌ Vehicles table doesn't exist - reinitializing database")
            cursor.execute("DROP TABLE IF EXISTS price_history")
            cursor.execute("DROP TABLE IF EXISTS vehicles")
            conn.commit()
            conn.close()
            return

        # Check if all required columns exist
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = {row['name'] for row in cursor.fetchall()}

        required_columns = {
            'url', 'title', 'current_price', 'original_price', 'trim',
            'charge_type', 'exterior_color', 'seat_type', 'packs', 'location',
            'photo_url', 'latitude', 'longitude', 'first_seen', 'last_seen',
            'is_available', 'is_sold'
        }

        missing_columns = required_columns - columns

        if missing_columns:
            print(f"⚠️  Missing columns detected: {missing_columns}")
            print("🔄 Backing up old database and creating new one...")

            # Backup old database
            backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            conn.close()
            os.rename(db_path, backup_path)
            print(f"✅ Old database backed up to: {backup_path}")
        else:
            print("✅ Database schema is correct")
            conn.close()

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        conn.close()
        raise


if __name__ == '__main__':
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    db_path = '/app/data/renault_vehicles.db' if os.path.exists('/app/data') else 'renault_vehicles.db'
    migrate_database(db_path)
    print("\n✅ Migration complete!")
