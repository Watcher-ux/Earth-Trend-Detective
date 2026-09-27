"""
Trend detection engine using Mann-Kendall test and Sen's slope.

The Mann-Kendall test is a non-parametric test for detecting monotonic
trends in time series data. It is the standard method used in climate
science because it:
  - Makes no assumption about data distribution
  - Is robust to outliers
  - Directly tests for significance (p-value)

Sen's slope gives the robust magnitude of the trend (units per time step).
"""
import numpy as np
import pandas as pd
import pymannkendall as mk
from dataclasses import dataclass, asdict
from typing import Optional

from app.config import DEFAULT_ALPHA, STEPS_PER_YEAR


@dataclass
class TrendResult:
    """Result of a trend analysis on a single time series."""
    variable: str
    region: str
    trend: str              # "increasing", "decreasing", "no trend"
    slope_per_year: float   # Sen's slope converted to units/year
    slope_per_decade: float
    p_value: float
    is_significant: bool    # p < alpha
    tau: float              # Kendall's tau correlation (-1 to 1)
    n_observations: int
    start_year: int
    end_year: int

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def summary(self) -> str:
        sig = "✅ Significant" if self.is_significant else "❌ Not significant"
        return (
            f"{self.variable} @ {self.region}: "
            f"{self.trend} ({self.slope_per_decade:+.4f}/decade, "
            f"p={self.p_value:.4f}) — {sig}"
        )


def compute_trend(
    dates: pd.Series,
    values: pd.Series,
    variable_name: str = "",
    region_name: str = "",
    alpha: float = DEFAULT_ALPHA,
    steps_per_year: int = STEPS_PER_YEAR,
) -> TrendResult:
    """
    Run Mann-Kendall trend test on a time series.

    Parameters
    ----------
    dates : pd.Series of datetime
    values : pd.Series of float
    variable_name : str — label for the variable
    region_name : str — label for the location / region
    alpha : float — significance level (default 0.05)
    steps_per_year : int — how many time steps per year (12 for monthly)

    Returns
    -------
    TrendResult with all statistics
    """
    # Ensure inputs are pd.Series (not DatetimeIndex or similar)
    if not isinstance(dates, pd.Series):
        dates = pd.Series(dates)
    if not isinstance(values, pd.Series):
        values = pd.Series(values)

    # Drop NaNs while keeping alignment
    mask = values.notna()
    dates_clean = dates[mask].reset_index(drop=True)
    values_clean = values[mask].reset_index(drop=True)

    if len(values_clean) < 10:
        raise ValueError(
            f"Need at least 10 observations, got {len(values_clean)}"
        )

    result = mk.original_test(values_clean.values, alpha=alpha)

    # Sen's slope is in units-per-timestep → convert to per-year
    slope_per_year = result.slope * steps_per_year
    slope_per_decade = slope_per_year * 10

    return TrendResult(
        variable=variable_name,
        region=region_name,
        trend=result.trend,
        slope_per_year=round(float(slope_per_year), 6),
        slope_per_decade=round(float(slope_per_decade), 4),
        p_value=round(float(result.p), 6),
        is_significant=bool(result.p < alpha),
        tau=round(float(result.Tau), 4),
        n_observations=len(values_clean),
        start_year=int(dates_clean.iloc[0].year),
        end_year=int(dates_clean.iloc[-1].year),
    )


def compute_grid_trends(
    grid_data: list[dict],
    value_col: str = "temperature_c",
    variable_name: str = "T2M",
    alpha: float = DEFAULT_ALPHA,
) -> pd.DataFrame:
    """
    Apply Mann-Kendall trend analysis to a list of grid-point DataFrames.

    Parameters
    ----------
    grid_data : list of dicts with keys {lat, lon, df}
    value_col : str — column name in each df to analyze
    variable_name : str
    alpha : float

    Returns
    -------
    DataFrame with columns: [lat, lon, slope_per_year, slope_per_decade,
                             p_value, is_significant, trend, tau]
    """
    records = []
    for point in grid_data:
        lat, lon, df = point["lat"], point["lon"], point["df"]
        try:
            tr = compute_trend(
                dates=df["date"],
                values=df[value_col],
                variable_name=variable_name,
                region_name=f"({lat:.1f}, {lon:.1f})",
                alpha=alpha,
            )
            records.append({
                "lat": lat,
                "lon": lon,
                "slope_per_year": tr.slope_per_year,
                "slope_per_decade": tr.slope_per_decade,
                "p_value": tr.p_value,
                "is_significant": tr.is_significant,
                "trend": tr.trend,
                "tau": tr.tau,
            })
        except (ValueError, Exception) as e:
            # Skip points with insufficient data
            continue

    return pd.DataFrame(records)
