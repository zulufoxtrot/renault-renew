"""
Renault Renew Scraper - Main scraping logic
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Optional, Callable, List
from urllib.parse import urljoin
from dataclasses import asdict
import pandas as pd

from src.models import Vehicle
from src.database import Database
from .extractors import DataExtractor
from .filters import VehicleFilters
from src import config


class RenaultScraper:
    """Main scraper class for Renault Renew listings"""

    def __init__(
            self,
            use_database: bool = True,
            db_path: str = None,
            progress_callback: Optional[Callable] = None
    ):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://fr.renew.auto/',
        })

        self.base_url = config.BASE_URL
        self.search_url = config.SEARCH_URL
        self.vehicles: List[Vehicle] = []
        self.use_database = use_database

        # Database setup
        if db_path is None:
            db_path = config.DB_PATH
        self.db = Database(db_path) if use_database else None

        # Callbacks and tracking
        self.progress_callback = progress_callback
        self.pages_processed = 0
        self.ads_processed = 0
        self.ads_added = 0

        # Extractors and filters
        self.extractor = DataExtractor(self.base_url)
        self.filters = VehicleFilters()

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a URL"""
        try:
            time.sleep(config.REQUEST_DELAY)
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"    ⚠️ Error fetching: {e}")
            return None

    def parse_detail_page(self, url: str) -> Optional[Vehicle]:
        """Parse a vehicle detail page"""
        soup = self.get_soup(url)
        if not soup:
            return None

        full_text = soup.get_text(" ", strip=True).lower()

        # 1. CHARGE CHECK
        if not self.filters.check_charge_type(full_text):
            return None

        # 2. F1 BLADE FILTER
        if not self.filters.check_f1_blade(full_text):
            return None

        # 3. COLOR FILTER
        raw_color = self.extractor.extract_color(soup).strip().lower()
        if not self.filters.check_color(raw_color):
            return None

        # 4. Extract data
        title = self.extractor.extract_title(soup)
        price = self.extractor.extract_price(soup)
        location = self.extractor.extract_location(soup)
        packs = self.extractor.extract_packs(soup)
        photo_url = self.extractor.extract_photo_url(soup)
        latitude, longitude = self.extractor.extract_coordinates(soup)
        seat_type = self.extractor.extract_seat_type(full_text)

        # Debug coordinates
        if latitude is None or longitude is None:
            maps_links = soup.find_all('a', href=re.compile(r'maps', re.I))
            if maps_links:
                print(f"    ⚠️  No coordinates extracted but found {len(maps_links)} maps link(s)")

        return Vehicle(
            title=title,
            price=price,
            trim=config.TRIM_FILTER,
            charge_type=config.CHARGE_FILTER,
            exterior_color=raw_color.title(),
            location=location,
            packs=packs,
            url=url,
            seat_type=seat_type,
            photo_url=photo_url,
            latitude=latitude,
            longitude=longitude
        )

    def _update_progress(self):
        """Update progress via callback"""
        if self.progress_callback:
            self.progress_callback({
                'pages_processed': self.pages_processed,
                'ads_processed': self.ads_processed,
                'ads_added': self.ads_added
            })

    def run(self):
        """Run the scraper"""
        print(f"🔎 Starting Scrape")
        print(f"   Target: {config.TRIM_FILTER} + {config.CHARGE_FILTER}")
        print(f"   Filter: No generic F1 Blades")
        if self.use_database:
            print(f"   Database: ENABLED (tracking price history)")
        print()

        self._update_progress()

        for page in range(1, config.MAX_PAGES):
            print(f"\n--- Page {page} ---")
            separator = "&" if "?" in self.search_url else "?"
            current_url = f"{self.search_url}{separator}page={page}"

            soup = self.get_soup(current_url)
            if not soup:
                break

            self.pages_processed = page
            self._update_progress()

            # Find all listing links
            links = soup.find_all('a', href=re.compile(r'(detail|product)', re.IGNORECASE))

            # Check if we've reached the end
            if not links:
                if "aucun r" in soup.get_text().lower() or "0 r" in soup.get_text().lower():
                    print("    ℹ️ Page says '0 Results'. End of search.")
                    break
                else:
                    print(f"    ⚠️ WARNING: No links found, but page doesn't say '0 Results'.")
                    print(f"    ⚠️ Saving debug file to: debug_fail_page.html")
                    with open("debug_fail_page.html", "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    break

            # Extract unique URLs
            unique_urls = set()
            skip_keywords = ["super charge", "standard charge"]

            for link in links:
                link_text = link.get_text(" ", strip=True).lower()
                if any(bad_word in link_text for bad_word in skip_keywords):
                    continue
                unique_urls.add(urljoin(self.base_url, link['href']))

            if not unique_urls:
                print("    ℹ️ Listings found but filtered (Super Charge). Checking next page...")
                continue

            print(f"    Found {len(unique_urls)} candidates. Checking details...")

            # Process each listing
            for url in unique_urls:
                self.ads_processed += 1
                self._update_progress()

                vehicle = self.parse_detail_page(url)
                if vehicle:
                    photo_indicator = "📷" if vehicle.photo_url else "📷❌"
                    coord_indicator = "🗺️" if vehicle.latitude and vehicle.longitude else "🗺️❌"
                    print(
                        f"    ✅ {photo_indicator} {coord_indicator} MATCH: {vehicle.price}€ | "
                        f"{vehicle.exterior_color} | {vehicle.location}"
                    )
                    self.vehicles.append(vehicle)

                    # Add to database
                    if self.use_database and self.db:
                        vehicle_dict = asdict(vehicle)
                        is_new, price_changed = self.db.add_or_update_vehicle(vehicle_dict)
                        if is_new:
                            self.ads_added += 1
                            self._update_progress()
                        if price_changed:
                            print(f"         💰 Price changed!")

        # Mark unavailable vehicles
        if self.use_database and self.db:
            current_urls = [v.url for v in self.vehicles]
            self.db.mark_unavailable_vehicles(current_urls)

        # Save CSV
        if self.vehicles:
            df = pd.DataFrame([asdict(v) for v in self.vehicles])
            df = df.drop('title', axis=1)
            df.to_csv(config.CSV_OUTPUT_FILE, index=False)
            print(f"\n💾 CSV saved to {config.CSV_OUTPUT_FILE}")

        # Close database
        if self.db:
            self.db.close()

        if not self.vehicles:
            print("\n😔 No vehicles found matching all criteria in this scrape.")
