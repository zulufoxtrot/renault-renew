#!/usr/bin/env python3
"""
Renault Renew Scraper v14 (Robust Pagination + Debug Dump)
- Filters: Iconic + Optimum Charge + Price (€19k-25k)
- Server-Side Filter: "Iconic" (saves bandwidth)
- F1 Logic: Excludes "Lame F1" UNLESS "Ton Caisse"
- Fix: Saves 'debug_fail_page.html' if it stops prematurely
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from urllib.parse import urljoin
from typing import List, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class Vehicle:
    title: str
    price: int
    trim: str
    charge_type: str
    exterior_color: str
    seat_type: str
    packs: str
    location: str
    url: str


class RenaultScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://fr.renew.auto/',
        })
        self.base_url = "https://fr.renew.auto"
        self.vehicles = []

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            # Increased sleep to 2.0s to avoid "Page 5" blocking
            time.sleep(0.5)
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"    ⚠️ Error fetching: {e}")
            return None

    def extract_location(self, soup: BeautifulSoup) -> str:
        dealer_link = soup.find('a', class_=re.compile(r'dealerInfos', re.I))
        if dealer_link:
            text = dealer_link.get_text(strip=True)
            clean_city = re.sub(r'^renault\s+', '', text, flags=re.IGNORECASE).strip()
            return clean_city.title()

        full_text = soup.get_text(" ", strip=True)
        match = re.search(r'Vendu par\s*:\s*(.*?)(?:\d{5}|-)', full_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:30].replace("RENAULT ", "").title()

        return "Unknown Location"

    def extract_packs(self, soup: BeautifulSoup) -> str:
        headers = soup.find_all(string=re.compile(r'options', re.IGNORECASE))
        found_packs = []

        for header in headers:
            if len(header) > 50: continue
            parent = header.find_parent()
            if not parent: continue

            container = parent.find_parent('div') or parent
            ul = container.find_next('ul')
            if ul:
                items = ul.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if any(k in text.lower() for k in ["pack", "vision", "driving", "augment", "harman"]):
                        found_packs.append(text)

        return ", ".join(sorted(list(set(found_packs)))) if found_packs else "None"

    def extract_color_precise(self, soup: BeautifulSoup) -> str:
        list_items = soup.find_all('li')
        for li in list_items:
            text = li.get_text(strip=True).lower()
            if "couleur" in text:
                strong_tag = li.find('strong')
                if strong_tag:
                    return strong_tag.get_text(strip=True).lower()
                if ":" in text:
                    return text.split(":")[-1].strip()
        return "inconnu"

    def parse_detail_page(self, url: str) -> Optional[Vehicle]:
        soup = self.get_soup(url)
        if not soup: return None

        full_text = soup.get_text(" ", strip=True).lower()
        title = (soup.find('h1') or soup.find('title')).get_text(strip=True)

        # 1. CHARGE CHECK (Optimum Charge / AC22)
        is_optimum = any(x in full_text for x in ["optimum charge", "ac22", "22kw", "22 kw"])
        if not is_optimum: return None

        # 2. F1 BLADE FILTER
        # Keep if "ton caisse", otherwise exclude if "lame f1" is mentioned
        if "lame f1" in full_text:
            if "ton caisse" not in full_text and ("gris schiste" in full_text or "gris rafale" in full_text):
                return None

        # 3. SIMPLIFIED COLOR FILTER
        raw_color = self.extract_color_precise(soup).strip().lower()

        # Exclude RED (Rouge Flamme / Rouge)
        if 'rouge' in raw_color or 'flamme' in raw_color or raw_color == 'noir':
            return None

        # 4. PRICE & EXTRAS
        price = 0
        price_tag = soup.find(string=re.compile(r'^\s*\d{2}[\s\.]?\d{3}\s*€'))
        if price_tag:
            price = int(re.sub(r'[^\d]', '', price_tag))

        location = self.extract_location(soup)
        packs = self.extract_packs(soup)

        # SEAT TYPE DETECTION
        seat_type = "unknown"
        if "alcantara" in full_text or "tissu" in full_text:
            seat_type = "alcantara"
        elif "sellerie cuir riviera gris" in full_text:
            seat_type = "cuir blanc"
        else:
            seat_type = "unsure"
        return Vehicle(
            title=title,
            price=price,
            trim="Iconic",
            charge_type="Optimum Charge",
            exterior_color=raw_color.title(),
            location=location,
            packs=packs,
            url=url,
            seat_type=seat_type  # Add seat type to the returned Vehicle
        )

    def run(self):
        start_url = (
        "https://fr.renew.auto/achat-vehicules-occasions.html?prices.customerDisplayPrice=19000-25000&query=renault%20megane%20e-tech%20electrique&finishing.label.raw=Iconic"
        )

        print(f"🔎 Starting Scrape v14")
        print(f"   Target: Iconic (URL Filter) + Optimum Charge")
        print(f"   Filter: No generic F1 Blades")

        for page in range(1, 20):
            print(f"\n--- Page {page} ---")
            separator = "&" if "?" in start_url else "?"
            current_url = f"{start_url}{separator}page={page}"

            soup = self.get_soup(current_url)
            if not soup: break

            # --- ROBUST LINK SEARCH ---
            # Using a broader Regex to catch '/detail', '/product', etc.
            links = soup.find_all('a', href=re.compile(r'(detail|product)', re.IGNORECASE))

            # --- DEBUG DUMP IF EMPTY ---
            if not links:
                # Check if it's a genuine "No Results" page
                if "aucun r" in soup.get_text().lower() or "0 r" in soup.get_text().lower():
                    print("    ℹ️ Page says '0 Results'. End of search.")
                    break
                else:
                    # If it's NOT a "0 results" page but we found no links, something is wrong (Captcha/Block)
                    print(f"    ⚠️ WARNING: No links found, but page doesn't say '0 Results'.")
                    print(f"    ⚠️ Saving debug file to: debug_fail_page.html")
                    with open("debug_fail_page.html", "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    print(f"    ℹ️ Please open 'debug_fail_page.html' to see what the scraper saw.")
                    break

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

            for url in unique_urls:
                vehicle = self.parse_detail_page(url)
                if vehicle:
                    print(
                        f"    ✅ MATCH: {vehicle.price}€ | {vehicle.exterior_color} | {vehicle.location} | {vehicle.packs} | {vehicle.url}")
                    self.vehicles.append(vehicle)

        if self.vehicles:
            df = pd.DataFrame([asdict(v) for v in self.vehicles])
            df = df.drop('title', axis=1)
            filename = "renault_megane_v14.csv"
            df.to_csv(filename, index=False)
            print(f"    💾 Saved to {filename}")
        else:
            print("\n😔 No vehicles found matching all criteria.")


if __name__ == "__main__":
    scraper = RenaultScraper()
    scraper.run()