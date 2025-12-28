"""
Data extraction logic for Renault scraper
"""

import re
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class DataExtractor:
    """Handles extraction of vehicle data from HTML"""

    def __init__(self, base_url: str = "https://fr.renew.auto"):
        self.base_url = base_url

    def extract_location(self, soup: BeautifulSoup) -> str:
        """Extract dealer location from detail page"""
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
        """Extract option packs from detail page"""
        headers = soup.find_all(string=re.compile(r'options', re.IGNORECASE))
        found_packs = []

        for header in headers:
            if len(header) > 50:
                continue
            parent = header.find_parent()
            if not parent:
                continue

            container = parent.find_parent('div') or parent
            ul = container.find_next('ul')
            if ul:
                items = ul.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if any(k in text.lower() for k in ["pack", "vision", "driving", "augment", "harman"]):
                        found_packs.append(text)

        return ", ".join(sorted(list(set(found_packs)))) if found_packs else "None"

    def extract_color(self, soup: BeautifulSoup) -> str:
        """Extract exterior color from detail page"""
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

    def extract_price(self, soup: BeautifulSoup) -> int:
        """Extract price from detail page"""
        price_tag = soup.find(string=re.compile(r'^\s*\d{2}[\s\.]?\d{3}\s*€'))
        if price_tag:
            return int(re.sub(r'[^\d]', '', price_tag))
        return 0

    def extract_photo_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract main photo URL from vehicle detail page"""
        # Method 1: Look for main product image
        img = soup.find('img', class_=re.compile(r'(product|vehicle|main|hero)', re.I))
        if img and img.get('src'):
            return urljoin(self.base_url, img['src'])

        # Method 2: Look for image in picture tag
        picture = soup.find('picture')
        if picture:
            img = picture.find('img')
            if img and img.get('src'):
                return urljoin(self.base_url, img['src'])

        # Method 3: Look for any image with vehicle keywords
        for img in soup.find_all('img'):
            alt = img.get('alt', '').lower()
            src = img.get('src', '')
            if src and any(keyword in alt for keyword in ['megane', 'véhicule', 'vehicle', 'voiture']):
                return urljoin(self.base_url, src)

        # Method 4: Find largest image (likely the main product photo)
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                width = img.get('width', '')
                if width and isinstance(width, str) and width.isdigit() and int(width) > 200:
                    return urljoin(self.base_url, src)
                elif not width:
                    return urljoin(self.base_url, src)

        return None

    def extract_coordinates(self, soup: BeautifulSoup) -> tuple[Optional[float], Optional[float]]:
        """Extract GPS coordinates from Google Maps link"""
        # Method 1: Find by href pattern
        maps_link = soup.find('a', href=re.compile(r'google\.com/maps', re.I))

        if maps_link:
            href = maps_link.get('href', '')
            patterns = [
                r'/maps/dir//([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                r'@([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                r'q=([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, href)
                if match:
                    latitude = float(match.group(1))
                    longitude = float(match.group(2))
                    return latitude, longitude

        # Method 2: Search all links containing 'maps' or 'itinéraire'
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()

            if 'google.com/maps' in href or ('maps' in href and ('itinéraire' in text or 'direction' in text)):
                for pattern in [
                    r'/maps/dir//([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                    r'@([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                    r'q=([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                    r'([-+]?\d+\.\d+),([-+]?\d+\.\d+)',
                ]:
                    match = re.search(pattern, href)
                    if match:
                        try:
                            latitude = float(match.group(1))
                            longitude = float(match.group(2))
                            # Validate coordinates are in France
                            if 41 <= latitude <= 51 and -5 <= longitude <= 10:
                                return latitude, longitude
                        except (ValueError, IndexError):
                            continue

        return None, None

    def extract_seat_type(self, full_text: str) -> str:
        """Detect seat type from page text"""
        if "alcantara" in full_text or "tissu" in full_text:
            return "alcantara"
        elif "sellerie cuir riviera gris" in full_text:
            return "cuir blanc"
        else:
            return "unsure"

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        title = soup.find('title')
        if title:
            return title.get_text(strip=True)

        return "Unknown Vehicle"
