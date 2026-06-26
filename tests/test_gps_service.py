"""
Tests — GPS Service Module
============================
Unit tests for coordinate parsing, validation, and route summary.
"""

import pandas as pd
import pytest

from app.gps_service import (
    Coordinates,
    get_route_summary,
    parse_coordinates,
)


class TestCoordinateParsing:

    def test_valid_coordinates(self):
        coords = parse_coordinates("17.3913", "78.3206")
        assert coords is not None
        assert coords.latitude == pytest.approx(17.3913)
        assert coords.longitude == pytest.approx(78.3206)

    def test_invalid_latitude_out_of_range(self):
        assert parse_coordinates("91.0", "78.0") is None

    def test_invalid_longitude_out_of_range(self):
        assert parse_coordinates("17.0", "181.0") is None

    def test_non_numeric_string(self):
        assert parse_coordinates("abc", "78.0") is None

    def test_empty_string(self):
        assert parse_coordinates("", "") is None

    def test_negative_valid_coordinates(self):
        coords = parse_coordinates("-33.8688", "151.2093")  # Sydney
        assert coords is not None

    def test_str_format(self):
        coords = Coordinates(17.3913, 78.3206)
        s = str(coords)
        assert "17.391300" in s or "17.3913" in s
        assert "78.320600" in s or "78.3206" in s

    def test_google_maps_url_contains_coords(self):
        coords = Coordinates(17.3913, 78.3206)
        url = coords.to_google_maps_url()
        assert "maps" in url and "17.3913" in url


class TestRouteSummary:

    def test_route_summary_keys(self):
        df = pd.DataFrame({"lat": [17.0, 17.1, 17.2], "lon": [78.0, 78.1, 78.2]})
        summary = get_route_summary(df)
        assert "total_points" in summary
        assert "start" in summary
        assert "end" in summary

    def test_total_points_count(self):
        df = pd.DataFrame({"lat": [1.0, 2.0, 3.0], "lon": [1.0, 2.0, 3.0]})
        summary = get_route_summary(df)
        assert summary["total_points"] == 3

    def test_start_end_coordinates(self):
        df = pd.DataFrame({"lat": [10.0, 20.0], "lon": [30.0, 40.0]})
        summary = get_route_summary(df)
        assert summary["start"].latitude == 10.0
        assert summary["end"].latitude == 20.0
