"""
NASA data fetchers with local disk caching.
Each fetcher returns a pandas DataFrame or xarray Dataset.
"""
import os
import json
import hashlib
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

from app.config import CACHE_DIR, NASA_POWER_BASE


def _cache_path(key: str, ext: str = "json") -> Path:
    """Generate a deterministic cache file path."""
    h = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{h}.{ext}"


def _get_cached_or_fetch(url: str, params: dict) -> dict:
    """Fetch JSON from URL with disk caching."""
    key = url + json.dumps(params, sort_keys=True)
    path = _cache_path(key)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


# ---------------------------------------------------------------------------
# 1. SURFACE TEMPERATURE — NASA POWER (no auth required)
# ---------------------------------------------------------------------------

def fetch_temperature(lat: float, lon: float,
                      start_year: int = 1981,
                      end_year: int = None) -> pd.DataFrame:
    """
    Fetch monthly mean surface temperature (T2M) from NASA POWER.

    Parameters
    ----------
    lat, lon : float — coordinates
    start_year, end_year : int — year range (inclusive)

    Returns
    -------
    DataFrame with columns: [date, temperature_c]
    """
    if end_year is None:
        end_year = datetime.now().year

    url = f"{NASA_POWER_BASE}/monthly/point"
    params = {
        "parameters": "T2M",
        "community": "RE",
        "longitude": round(lon, 4),
        "latitude": round(lat, 4),
        "start": str(start_year),
        "end": str(end_year),
        "format": "JSON",
    }
    data = _get_cached_or_fetch(url, params)
    temps = data["properties"]["parameter"]["T2M"]

    records = []
    for k, v in temps.items():
        if v == -999.0:
            continue  # missing data sentinel
        # Key format: "YYYYMM" or "YYYY13" (annual avg)
        if k.endswith("13"):
            continue  # skip annual summary rows
        try:
            dt = pd.to_datetime(k, format="%Y%m")
            records.append({"date": dt, "temperature_c": v})
        except ValueError:
            continue

    df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    return df


def fetch_temperature_grid(
    lat_range: tuple = (-60, 75),
    lon_range: tuple = (-180, 180),
    step: float = 15.0,
    start_year: int = 1981,
    end_year: int = None,
) -> list[dict]:
    """
    Sample temperature trends across a grid of global points.
    Returns a list of dicts: [{lat, lon, df}, ...]
    """
    import numpy as np

    lats = np.arange(lat_range[0], lat_range[1] + step, step)
    lons = np.arange(lon_range[0], lon_range[1] + step, step)

    results = []
    for lat in lats:
        for lon in lons:
            try:
                df = fetch_temperature(lat, lon, start_year, end_year)
                if len(df) > 24:  # at least 2 years of data
                    results.append({"lat": lat, "lon": lon, "df": df})
            except Exception as e:
                print(f"  Skipping ({lat}, {lon}): {e}")
                continue
    return results


# ---------------------------------------------------------------------------
# 2. SEA ICE EXTENT — NSIDC (no auth required)
# ---------------------------------------------------------------------------

NSIDC_NORTH_URL = (
    "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/"
    "N_seaice_extent_monthly_v3.0.csv"
)
NSIDC_SOUTH_URL = (
    "https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/data/"
    "S_seaice_extent_monthly_v3.0.csv"
)


def _fetch_nsidc_csv(url: str, cache_key: str) -> pd.DataFrame:
    """Download and cache an NSIDC CSV file."""
    cache_file = CACHE_DIR / f"{cache_key}.csv"
    if not cache_file.exists():
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)

    # NSIDC CSVs have variable whitespace — handle gracefully
    df = pd.read_csv(
        cache_file,
        skipinitialspace=True,
        comment="#",
        on_bad_lines="skip",
    )
    # Normalize column names
    df.columns = df.columns.str.strip()
    return df


def fetch_sea_ice_extent() -> pd.DataFrame:
    """
    Fetch Arctic + Antarctic monthly sea ice extent from NSIDC Sea Ice Index v3.

    Returns
    -------
    DataFrame with columns: [date, arctic_extent_mkm2, antarctic_extent_mkm2]
    (extent in millions of km²)
    """
    dfs = {}
    for url, key, label in [
        (NSIDC_NORTH_URL, "nsidc_north_monthly", "arctic"),
        (NSIDC_SOUTH_URL, "nsidc_south_monthly", "antarctic"),
    ]:
        df = _fetch_nsidc_csv(url, key)

        # Build date from Year + Mo columns
        year_col = [c for c in df.columns if "year" in c.lower()][0]
        month_col = [c for c in df.columns if "mo" in c.lower()][0]
        extent_col = [c for c in df.columns if "extent" in c.lower()][0]

        df["date"] = pd.to_datetime(
            df[[year_col, month_col]].rename(
                columns={year_col: "year", month_col: "month"}
            ).assign(day=1)
        )
        df[f"{label}_extent_mkm2"] = pd.to_numeric(
            df[extent_col], errors="coerce"
        )
        dfs[label] = df[["date", f"{label}_extent_mkm2"]].dropna()

    merged = pd.merge(dfs["arctic"], dfs["antarctic"], on="date", how="outer")
    return merged.sort_values("date").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. SEA LEVEL — Placeholder (requires Earthdata login or pre-downloaded CSV)
# ---------------------------------------------------------------------------

def fetch_sea_level() -> pd.DataFrame:
    """
    Fetch global mean sea level anomaly.

    TODO: Implement using earthaccess or pre-downloaded PODAAC data.
    For now returns a placeholder DataFrame.
    """
    # Placeholder — will be implemented once Earthdata auth is wired up
    raise NotImplementedError(
        "Sea level data fetcher not yet implemented. "
        "Requires NASA Earthdata login — see .env.example"
    )
