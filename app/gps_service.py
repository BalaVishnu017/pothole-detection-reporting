"""
InfraVision AI — GPS & Location Service
=========================================
Provides GPS coordinate management, severity-aware location tagging,
Google Maps URL generation, and simulated GPS log reading.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Coordinates:
    """Represents a GPS location."""

    latitude: float
    longitude: float
    place_name: Optional[str] = None

    def __str__(self) -> str:
        if self.place_name:
            return f"{self.place_name} ({self.latitude:.6f}, {self.longitude:.6f})"
        return f"{self.latitude:.6f}, {self.longitude:.6f}"

    def to_google_maps_url(self) -> str:
        """Return a clickable Google Maps search URL for these coordinates."""
        return (
            f"https://www.google.com/maps/search/?api=1" f"&query={self.latitude},{self.longitude}"
        )

    def to_dict(self) -> dict:
        return {"latitude": self.latitude, "longitude": self.longitude}


# =============================================================================
# GPS Functions
# =============================================================================


def get_default_coordinates() -> Coordinates:
    """Return the default fallback coordinates from settings."""
    from config.settings import settings

    return Coordinates(
        latitude=settings.default_latitude,
        longitude=settings.default_longitude,
    )


def parse_coordinates(
    lat_str: str, lon_str: str, place_name: Optional[str] = None
) -> Optional[Coordinates]:
    """
    Parse latitude/longitude strings into a Coordinates object.

    Args:
        lat_str: Latitude as a string.
        lon_str: Longitude as a string.
        place_name: Optional name for the location.

    Returns:
        Coordinates if parsing succeeds, None otherwise.
    """
    try:
        lat = float(lat_str)
        lon = float(lon_str)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Coordinates out of range.")
        return Coordinates(latitude=lat, longitude=lon, place_name=place_name)
    except (ValueError, TypeError) as exc:
        logger.warning("Invalid coordinates (%s, %s): %s", lat_str, lon_str, exc)
        return None


def load_gps_log(csv_path: str = "data/gps_log.csv") -> Optional[pd.DataFrame]:
    """
    Load a GPS route log CSV file.

    Expected columns: lat, lon
    Optional columns: timestamp, speed_kmh

    Args:
        csv_path: Path to the GPS log CSV file.

    Returns:
        DataFrame if file exists and is valid, None otherwise.
    """
    path = Path(csv_path)
    if not path.exists():
        logger.warning("GPS log not found at '%s'.", csv_path)
        return None

    try:
        df = pd.read_csv(path)
        required = {"lat", "lon"}
        if not required.issubset(df.columns):
            logger.error("GPS CSV missing required columns: %s", required)
            return None
        logger.info("GPS log loaded: %d points from '%s'.", len(df), csv_path)
        return df
    except Exception as exc:
        logger.error("Failed to read GPS log: %s", exc)
        return None


def get_route_summary(df: pd.DataFrame) -> dict:
    """
    Compute summary statistics from a GPS route log.

    Args:
        df: DataFrame with 'lat' and 'lon' columns.

    Returns:
        Dictionary with start, end, total points, and bounding box.
    """
    return {
        "total_points": len(df),
        "start": Coordinates(df["lat"].iloc[0], df["lon"].iloc[0]),
        "end": Coordinates(df["lat"].iloc[-1], df["lon"].iloc[-1]),
        "lat_range": (df["lat"].min(), df["lat"].max()),
        "lon_range": (df["lon"].min(), df["lon"].max()),
    }
