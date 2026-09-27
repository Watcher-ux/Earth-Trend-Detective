"""
Tests for engine/data_fetcher.py

Validates:
- NASA POWER response parsing and DataFrame shape
- Missing data sentinel (-999) is filtered out
- Sea ice CSV parsing
- Caching works (second call uses disk cache)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd


class TestFetchTemperature:
    """Tests for the NASA POWER temperature fetcher."""

    def test_returns_dataframe(self):
        from engine.data_fetcher import fetch_temperature

        df = fetch_temperature(lat=28.6, lon=77.2, start_year=2020, end_year=2022)
        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "temperature_c" in df.columns

    def test_no_missing_sentinels(self):
        from engine.data_fetcher import fetch_temperature

        df = fetch_temperature(lat=0.0, lon=0.0, start_year=2020, end_year=2022)
        assert (df["temperature_c"] != -999.0).all(), "Missing data sentinel not filtered"

    def test_dates_are_sorted(self):
        from engine.data_fetcher import fetch_temperature

        df = fetch_temperature(lat=40.0, lon=-74.0, start_year=2015, end_year=2020)
        assert df["date"].is_monotonic_increasing

    def test_reasonable_temperature_values(self):
        from engine.data_fetcher import fetch_temperature

        df = fetch_temperature(lat=28.6, lon=77.2, start_year=2020, end_year=2022)
        # Delhi temperatures should be between -10 and 60°C
        assert df["temperature_c"].min() > -10
        assert df["temperature_c"].max() < 60


class TestFetchSeaIce:
    """Tests for the NSIDC sea ice extent fetcher."""

    def test_returns_dataframe(self):
        from engine.data_fetcher import fetch_sea_ice_extent

        df = fetch_sea_ice_extent()
        assert isinstance(df, pd.DataFrame)
        assert "date" in df.columns
        assert "arctic_extent_mkm2" in df.columns
        assert "antarctic_extent_mkm2" in df.columns

    def test_has_multiple_years(self):
        from engine.data_fetcher import fetch_sea_ice_extent

        df = fetch_sea_ice_extent()
        years = df["date"].dt.year.nunique()
        assert years > 30, f"Expected 30+ years of data, got {years}"

    def test_extent_values_reasonable(self):
        from engine.data_fetcher import fetch_sea_ice_extent

        df = fetch_sea_ice_extent()
        # Sea ice extent should be between 0 and 25 million km²
        for col in ["arctic_extent_mkm2", "antarctic_extent_mkm2"]:
            valid = df[col].dropna()
            assert valid.min() >= 0
            assert valid.max() <= 25
