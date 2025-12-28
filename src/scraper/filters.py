"""
Vehicle filtering logic for Renault scraper
"""

import re
from typing import Optional


class VehicleFilters:
    """Encapsulates filtering logic for vehicles"""

    # Colors to exclude
    EXCLUDED_COLORS = {'rouge', 'flamme', 'noir'}

    @staticmethod
    def check_charge_type(full_text: str) -> bool:
        """Check if vehicle has Optimum Charge"""
        return any(x in full_text for x in ["optimum charge", "ac22", "22kw", "22 kw"])

    @staticmethod
    def check_f1_blade(full_text: str) -> bool:
        """
        Check if vehicle should be filtered due to F1 blade
        Returns True if vehicle should be kept, False if filtered out
        """
        if "lame f1" not in full_text:
            return True  # Keep - no F1 blade mentioned

        # Has F1 blade - keep only if "ton caisse" is mentioned
        if "ton caisse" in full_text:
            return True

        # Has F1 blade without "ton caisse" - check color
        if "gris schiste" in full_text or "gris rafale" in full_text:
            return False  # Filter out

        return True  # Keep

    @staticmethod
    def check_color(color: str) -> bool:
        """
        Check if color is acceptable
        Returns True if color is acceptable, False if should be excluded
        """
        color_lower = color.strip().lower()

        for excluded in VehicleFilters.EXCLUDED_COLORS:
            if excluded in color_lower:
                return False

        return True

    @staticmethod
    def check_price(price: int, price_min: int = 19000, price_max: int = 25000) -> bool:
        """Check if price is within acceptable range"""
        return price_min <= price <= price_max
