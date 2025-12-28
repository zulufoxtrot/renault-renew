"""
Centralized configuration for Renault Scraper
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Database configuration
DB_PATH = os.environ.get(
    'DATABASE_PATH',
    '/app/data/renault_vehicles.db' if os.path.exists('/app/data') else 'renault_vehicles.db'
)

# API configuration
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Scraper configuration
BASE_URL = "https://fr.renew.auto"
SEARCH_URL = (
    "https://fr.renew.auto/achat-vehicules-occasions.html"
    "?prices.customerDisplayPrice=19000-25000"
    "&query=renault%20megane%20e-tech%20electrique"
    "&finishing.label.raw=Iconic"
)

# Scraper filters
PRICE_MIN = 19000
PRICE_MAX = 25000
TRIM_FILTER = "Iconic"
CHARGE_FILTER = "Optimum Charge"

# Scraper behavior
MAX_PAGES = 20
REQUEST_TIMEOUT = 15
REQUEST_DELAY = 0.5  # seconds between requests

# User agent
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# Report configuration
REPORT_OUTPUT_FILE = 'vehicle_report.html'
CSV_OUTPUT_FILE = 'renault_megane_v15.csv'

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', 'scraper.log')
