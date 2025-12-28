"""
Database Manager for Renault Scraper
Handles SQLite storage of vehicles and price history
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class VehicleRecord:
    """Vehicle database record"""
    url: str
    title: str
    price: int
    trim: str
    charge_type: str
    exterior_color: str
    seat_type: str
    packs: str
    location: str
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    original_price: Optional[int] = None
    is_new: bool = False
    is_sold: bool = False


class Database:
    """Database interface for vehicle storage"""

    def __init__(self, db_path: str = "renault_vehicles.db"):
        self.db_path = db_path
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Create vehicles table with is_sold column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                current_price INTEGER NOT NULL,
                original_price INTEGER,
                trim TEXT,
                charge_type TEXT,
                exterior_color TEXT,
                seat_type TEXT,
                packs TEXT,
                location TEXT,
                photo_url TEXT,
                latitude REAL,
                longitude REAL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP NOT NULL,
                is_available BOOLEAN NOT NULL DEFAULT 1,
                is_sold BOOLEAN NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_url TEXT NOT NULL,
                price INTEGER NOT NULL,
                scraped_at TIMESTAMP NOT NULL,
                FOREIGN KEY (vehicle_url) REFERENCES vehicles(url)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_url
            ON price_history(vehicle_url)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_date
            ON price_history(scraped_at)
        """)

        self.conn.commit()
        print(f"✅ Database initialized: {self.db_path}")

    def add_or_update_vehicle(self, vehicle_data: Dict) -> Tuple[bool, bool]:
        """
        Add or update a vehicle in the database
        Returns: (is_new, price_changed)
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        # Check if vehicle exists
        cursor.execute("SELECT url, current_price, original_price FROM vehicles WHERE url = ?",
                       (vehicle_data['url'],))
        existing = cursor.fetchone()

        is_new = existing is None
        price_changed = False

        if is_new:
            # New vehicle - insert
            cursor.execute("""
                INSERT INTO vehicles (
                    url, title, current_price, original_price, trim, charge_type,
                    exterior_color, seat_type, packs, location, photo_url,
                    latitude, longitude, first_seen, last_seen, is_available, is_sold
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """, (
                vehicle_data['url'],
                vehicle_data['title'],
                vehicle_data['price'],
                vehicle_data['price'],  # original_price = first price
                vehicle_data['trim'],
                vehicle_data['charge_type'],
                vehicle_data['exterior_color'],
                vehicle_data['seat_type'],
                vehicle_data['packs'],
                vehicle_data['location'],
                vehicle_data.get('photo_url'),
                vehicle_data.get('latitude'),
                vehicle_data.get('longitude'),
                now,
                now
            ))

            # Add first price to history
            cursor.execute("""
                INSERT INTO price_history (vehicle_url, price, scraped_at)
                VALUES (?, ?, ?)
            """, (vehicle_data['url'], vehicle_data['price'], now))

            print(f"   🆕 NEW vehicle added: {vehicle_data['url']}")
        else:
            # Existing vehicle - update
            old_price = existing['current_price']
            new_price = vehicle_data['price']

            if old_price != new_price:
                price_changed = True
                print(f"   💰 PRICE CHANGE: {old_price}€ → {new_price}€ for {vehicle_data['url']}")

                # Add price change to history
                cursor.execute("""
                    INSERT INTO price_history (vehicle_url, price, scraped_at)
                    VALUES (?, ?, ?)
                """, (vehicle_data['url'], new_price, now))

            # Update vehicle record
            cursor.execute("""
                UPDATE vehicles SET
                    title = ?,
                    current_price = ?,
                    trim = ?,
                    charge_type = ?,
                    exterior_color = ?,
                    seat_type = ?,
                    packs = ?,
                    location = ?,
                    photo_url = ?,
                    latitude = ?,
                    longitude = ?,
                    last_seen = ?,
                    is_available = 1
                WHERE url = ?
            """, (
                vehicle_data['title'],
                vehicle_data['price'],
                vehicle_data['trim'],
                vehicle_data['charge_type'],
                vehicle_data['exterior_color'],
                vehicle_data['seat_type'],
                vehicle_data['packs'],
                vehicle_data['location'],
                vehicle_data.get('photo_url'),
                vehicle_data.get('latitude'),
                vehicle_data.get('longitude'),
                now,
                vehicle_data['url']
            ))

        self.conn.commit()
        return is_new, price_changed

    def mark_unavailable_vehicles(self, current_urls: List[str]):
        """Mark vehicles not in current scrape as unavailable"""
        cursor = self.conn.cursor()

        if current_urls:
            placeholders = ','.join('?' * len(current_urls))
            cursor.execute(f"""
                UPDATE vehicles
                SET is_available = 0
                WHERE url NOT IN ({placeholders})
                AND is_available = 1
            """, current_urls)
        else:
            cursor.execute("""
                UPDATE vehicles
                SET is_available = 0
                WHERE is_available = 1
            """)

        self.conn.commit()

    def get_all_vehicles(self) -> List[VehicleRecord]:
        """Get all vehicles with their data"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
                url, title, current_price, original_price, trim, charge_type,
                exterior_color, seat_type, packs, location, photo_url,
                latitude, longitude, first_seen, last_seen, is_available
            FROM vehicles
            ORDER BY last_seen DESC, current_price ASC
        """)

        vehicles = []
        for row in cursor.fetchall():
            # Check if vehicle is new (first seen in last 24 hours)
            first_seen = datetime.fromisoformat(row['first_seen'])
            now = datetime.now()
            is_new = (now - first_seen).total_seconds() < 86400  # 24 hours

            vehicles.append(VehicleRecord(
                url=row['url'],
                title=row['title'],
                price=row['current_price'],
                original_price=row['original_price'],
                trim=row['trim'],
                charge_type=row['charge_type'],
                exterior_color=row['exterior_color'],
                seat_type=row['seat_type'],
                packs=row['packs'],
                location=row['location'],
                photo_url=row['photo_url'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                first_seen=row['first_seen'],
                last_seen=row['last_seen'],
                is_new=is_new and row['is_available'] == 1
            ))

        return vehicles

    def get_price_history(self, vehicle_url: str) -> List[Dict]:
        """Get price history for a specific vehicle"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT price, scraped_at
            FROM price_history
            WHERE vehicle_url = ?
            ORDER BY scraped_at ASC
        """, (vehicle_url,))

        return [{'price': row['price'], 'date': row['scraped_at']}
                for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Total vehicles
        cursor.execute("SELECT COUNT(*) as count FROM vehicles")
        stats['total_vehicles'] = cursor.fetchone()['count']

        # Available vehicles
        cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE is_available = 1")
        stats['available_vehicles'] = cursor.fetchone()['count']

        # Sold vehicles
        cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE is_sold = 1")
        stats['sold_vehicles'] = cursor.fetchone()['count']

        # New vehicles (last 24h)
        cursor.execute("""
            SELECT COUNT(*) as count FROM vehicles
            WHERE datetime(first_seen) > datetime('now', '-1 day')
            AND is_available = 1 AND is_sold = 0
        """)
        stats['new_vehicles_24h'] = cursor.fetchone()['count']

        # Price changes
        cursor.execute("""
            SELECT COUNT(DISTINCT vehicle_url) as count
            FROM price_history
        """)
        stats['vehicles_with_price_history'] = cursor.fetchone()['count']
        return stats

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup"""
        self.close()
