"""
Tests for engine/trend_engine.py

Validates Mann-Kendall + Sen's slope on synthetic data
with known properties:
- Linear increasing → detected as significant increasing
- Linear decreasing → detected as significant decreasing
- Pure random noise → no significant trend
- Known slope → Sen's slope matches within tolerance
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np
import pandas as pd

from engine.trend_engine import compute_trend, TrendResult


def _make_monthly_dates(n_years: int = 20):
    """Generate monthly dates starting from 2000."""
    return pd.date_range("2000-01-01", periods=n_years * 12, freq="MS")


class TestMannKendall:
    """Tests for Mann-Kendall trend detection."""

    def test_increasing_trend_detected(self):
        """A linearly increasing series should be detected as 'increasing'."""
        dates = _make_monthly_dates(20)
        values = pd.Series(np.arange(len(dates), dtype=float) * 0.01)
        result = compute_trend(dates, values, "test", "test")

        assert result.trend == "increasing"
        assert result.is_significant is True
        assert result.p_value < 0.05

    def test_decreasing_trend_detected(self):
        """A linearly decreasing series should be detected as 'decreasing'."""
        dates = _make_monthly_dates(20)
        values = pd.Series(100.0 - np.arange(len(dates), dtype=float) * 0.01)
        result = compute_trend(dates, values, "test", "test")

        assert result.trend == "decreasing"
        assert result.is_significant is True
        assert result.p_value < 0.05

    def test_no_trend_in_noise(self):
        """Pure random noise should not show a significant trend."""
        np.random.seed(42)
        dates = _make_monthly_dates(20)
        values = pd.Series(np.random.normal(0, 1, len(dates)))
        result = compute_trend(dates, values, "test", "test")

        assert result.p_value > 0.05 or result.trend == "no trend"

    def test_slope_accuracy(self):
        """Sen's slope should match the known slope within tolerance."""
        dates = _make_monthly_dates(20)
        # 0.5°C per year = 0.5/12 per month
        true_slope_per_year = 0.5
        values = pd.Series(
            np.arange(len(dates), dtype=float) * (true_slope_per_year / 12)
        )
        result = compute_trend(dates, values, "test", "test")

        assert abs(result.slope_per_year - true_slope_per_year) < 0.01, (
            f"Expected ~{true_slope_per_year}, got {result.slope_per_year}"
        )

    def test_slope_per_decade_is_10x_per_year(self):
        """slope_per_decade should be exactly 10× slope_per_year."""
        dates = _make_monthly_dates(20)
        values = pd.Series(np.arange(len(dates), dtype=float) * 0.01)
        result = compute_trend(dates, values, "test", "test")

        assert abs(result.slope_per_decade - result.slope_per_year * 10) < 0.001

    def test_too_few_observations_raises(self):
        """Should raise ValueError with fewer than 10 observations."""
        dates = pd.date_range("2020-01-01", periods=5, freq="MS")
        values = pd.Series([1, 2, 3, 4, 5], dtype=float)

        with pytest.raises(ValueError, match="at least 10"):
            compute_trend(dates, values, "test", "test")

    def test_nans_are_handled(self):
        """NaN values should be dropped, not cause errors."""
        dates = _make_monthly_dates(20)
        values = pd.Series(np.arange(len(dates), dtype=float) * 0.01)
        # Insert some NaNs
        values.iloc[5] = np.nan
        values.iloc[100] = np.nan
        values.iloc[200] = np.nan

        result = compute_trend(dates, values, "test", "test")
        assert result.n_observations == len(dates) - 3
        assert result.trend == "increasing"

    def test_result_has_correct_years(self):
        """Start and end years should match the data."""
        dates = _make_monthly_dates(15)
        values = pd.Series(np.arange(len(dates), dtype=float))
        result = compute_trend(dates, values, "test", "test")

        assert result.start_year == 2000
        assert result.end_year == 2014

    def test_tau_in_valid_range(self):
        """Kendall's tau should be between -1 and 1."""
        dates = _make_monthly_dates(20)
        values = pd.Series(np.arange(len(dates), dtype=float))
        result = compute_trend(dates, values, "test", "test")

        assert -1 <= result.tau <= 1

    def test_summary_string(self):
        """The summary property should return a readable string."""
        dates = _make_monthly_dates(20)
        values = pd.Series(np.arange(len(dates), dtype=float))
        result = compute_trend(dates, values, "temp", "north")

        assert "temp" in result.summary
        assert "north" in result.summary
