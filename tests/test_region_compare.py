"""
Tests for engine/region_compare.py

Validates:
- Comparison presets are well-formed
- ComparisonResult correctly detects opposite trends
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from engine.region_compare import COMPARISON_PRESETS, ComparisonResult
from engine.trend_engine import TrendResult


class TestComparisonPresets:
    """Validate preset configuration."""

    def test_all_presets_have_required_fields(self):
        for key, preset in COMPARISON_PRESETS.items():
            assert "title" in preset, f"Preset {key} missing 'title'"
            assert "description" in preset, f"Preset {key} missing 'description'"
            assert "type" in preset, f"Preset {key} missing 'type'"

    def test_temperature_presets_have_regions(self):
        for key, preset in COMPARISON_PRESETS.items():
            if preset["type"] == "temperature":
                assert "regions" in preset, f"Temp preset {key} missing 'regions'"
                assert len(preset["regions"]) == 2


class TestComparisonResult:
    """Test the ComparisonResult dataclass."""

    def _make_trend(self, trend_dir: str) -> TrendResult:
        return TrendResult(
            variable="test", region="test", trend=trend_dir,
            slope_per_year=0.1, slope_per_decade=1.0,
            p_value=0.01, is_significant=True, tau=0.5,
            n_observations=100, start_year=2000, end_year=2020,
        )

    def test_opposite_trends_detected(self):
        result = ComparisonResult(
            title="test", description="test",
            region_a_name="A", region_b_name="B",
            trend_a=self._make_trend("increasing"),
            trend_b=self._make_trend("decreasing"),
        )
        assert result.are_opposite is True

    def test_same_trends_not_opposite(self):
        result = ComparisonResult(
            title="test", description="test",
            region_a_name="A", region_b_name="B",
            trend_a=self._make_trend("increasing"),
            trend_b=self._make_trend("increasing"),
        )
        assert result.are_opposite is False

    def test_no_trend_not_opposite(self):
        result = ComparisonResult(
            title="test", description="test",
            region_a_name="A", region_b_name="B",
            trend_a=self._make_trend("increasing"),
            trend_b=self._make_trend("no trend"),
        )
        assert result.are_opposite is False
