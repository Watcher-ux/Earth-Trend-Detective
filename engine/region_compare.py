"""
Side-by-side regional trend comparison.

Pre-configured pairs that demonstrate the key challenge insight:
the SAME physical process can drive OPPOSITE trends in different regions.
"""
from engine.data_fetcher import fetch_temperature, fetch_sea_ice_extent
from engine.trend_engine import compute_trend, TrendResult
from dataclasses import dataclass


@dataclass
class ComparisonResult:
    """Result of comparing trends between two regions."""
    title: str
    description: str
    region_a_name: str
    region_b_name: str
    trend_a: TrendResult
    trend_b: TrendResult

    @property
    def are_opposite(self) -> bool:
        """True if one region is increasing and the other decreasing."""
        directions = {self.trend_a.trend, self.trend_b.trend}
        return "increasing" in directions and "decreasing" in directions


# ---------------------------------------------------------------------------
# Pre-built comparison presets
# ---------------------------------------------------------------------------

COMPARISON_PRESETS = {
    "arctic_vs_antarctic_ice": {
        "title": "🧊 Sea Ice: Arctic Decline vs Antarctic Variability",
        "description": (
            "Global warming drives dramatic Arctic sea ice loss, "
            "while Antarctic sea ice has shown more complex behavior "
            "with periods of increase — driven by the same greenhouse "
            "forcing but modulated by ocean circulation and winds."
        ),
        "type": "sea_ice",
    },
    "arctic_amplification": {
        "title": "🌡️ Temperature: Arctic Amplification vs Tropical Stability",
        "description": (
            "The Arctic warms 2–4× faster than the global average "
            "(Arctic amplification), while tropical temperatures "
            "change more slowly — both driven by the same radiative "
            "forcing but amplified by ice-albedo feedback at the poles."
        ),
        "type": "temperature",
        "regions": [
            {"name": "Arctic (75°N, 0°E)", "lat": 75.0, "lon": 0.0},
            {"name": "Tropics (0°N, 0°E)", "lat": 0.0, "lon": 0.0},
        ],
    },
    "hemispheric_warming": {
        "title": "🌡️ Northern vs Southern Hemisphere Warming Rates",
        "description": (
            "The Northern Hemisphere warms faster due to greater "
            "land area (land heats faster than ocean) and ice-albedo "
            "feedbacks. Both hemispheres warm from the same forcing, "
            "but at different rates."
        ),
        "type": "temperature",
        "regions": [
            {"name": "Northern mid-lat (50°N, 10°E)", "lat": 50.0, "lon": 10.0},
            {"name": "Southern mid-lat (50°S, 10°E)", "lat": -50.0, "lon": 10.0},
        ],
    },
}


def run_comparison(preset_key: str) -> ComparisonResult:
    """
    Execute a preset comparison and return trend results for both regions.

    Parameters
    ----------
    preset_key : str — key into COMPARISON_PRESETS

    Returns
    -------
    ComparisonResult with trend analysis for both regions
    """
    preset = COMPARISON_PRESETS[preset_key]

    if preset["type"] == "sea_ice":
        df = fetch_sea_ice_extent()
        trend_a = compute_trend(
            dates=df["date"],
            values=df["arctic_extent_mkm2"],
            variable_name="Sea Ice Extent",
            region_name="Arctic",
        )
        trend_b = compute_trend(
            dates=df["date"],
            values=df["antarctic_extent_mkm2"],
            variable_name="Sea Ice Extent",
            region_name="Antarctic",
        )
        return ComparisonResult(
            title=preset["title"],
            description=preset["description"],
            region_a_name="Arctic",
            region_b_name="Antarctic",
            trend_a=trend_a,
            trend_b=trend_b,
        )

    elif preset["type"] == "temperature":
        regions = preset["regions"]
        trends = []
        for region in regions:
            df = fetch_temperature(region["lat"], region["lon"])
            tr = compute_trend(
                dates=df["date"],
                values=df["temperature_c"],
                variable_name="Surface Temperature",
                region_name=region["name"],
            )
            trends.append(tr)

        return ComparisonResult(
            title=preset["title"],
            description=preset["description"],
            region_a_name=regions[0]["name"],
            region_b_name=regions[1]["name"],
            trend_a=trends[0],
            trend_b=trends[1],
        )

    else:
        raise ValueError(f"Unknown comparison type: {preset['type']}")
