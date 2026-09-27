"""
🌡️ Surface Temperature Trend Explorer

Fetches monthly T2M data from NASA POWER for any location,
runs Mann-Kendall trend analysis, and visualizes the results.
"""
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import pandas as pd

from engine.data_fetcher import fetch_temperature, fetch_temperature_grid
from engine.trend_engine import compute_trend, compute_grid_trends
from app.components.timeseries import render_timeseries
from app.components.globe import render_trend_globe
from app.components.significance import (
    render_trend_metrics,
    render_significance_explainer,
)

st.set_page_config(page_title="🌡️ Temperature Trends", page_icon="🌡️", layout="wide")
st.title("🌡️ Surface Temperature Trends")
st.markdown("*Data: NASA POWER — Monthly mean temperature at 2 meters (T2M)*")

render_significance_explainer()

st.divider()

# --- Single-point analysis ---
st.header("📍 Single Location Analysis")

col_lat, col_lon, col_years = st.columns(3)
with col_lat:
    lat = st.number_input("Latitude", value=28.6, min_value=-90.0, max_value=90.0, step=0.5)
with col_lon:
    lon = st.number_input("Longitude", value=77.2, min_value=-180.0, max_value=180.0, step=0.5)
with col_years:
    year_range = st.slider("Year range", 1981, 2025, (1981, 2024))

if st.button("🔍 Analyze Temperature Trend", type="primary"):
    with st.spinner("Fetching data from NASA POWER..."):
        df = fetch_temperature(lat, lon, start_year=year_range[0], end_year=year_range[1])

    if len(df) < 10:
        st.error("Not enough data for this location/time range.")
    else:
        trend = compute_trend(
            dates=df["date"],
            values=df["temperature_c"],
            variable_name="Surface Temperature (T2M)",
            region_name=f"({lat:.1f}°, {lon:.1f}°)",
        )

        render_trend_metrics(trend)

        fig = render_timeseries(
            dates=df["date"],
            values=df["temperature_c"],
            trend_result=trend,
            y_label="Temperature (°C)",
            title=f"Surface Temperature at ({lat:.1f}°, {lon:.1f}°)",
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Raw data"):
            st.dataframe(df, use_container_width=True)

st.divider()

# --- Global grid analysis ---
st.header("🌐 Global Trend Map")
st.markdown(
    "Sample temperature trends across the globe and display on a 3D interactive map. "
    "This fetches many API calls — use a coarse grid for speed."
)

col_step, col_go = st.columns([3, 1])
with col_step:
    grid_step = st.select_slider(
        "Grid spacing (degrees)",
        options=[10, 15, 20, 30, 45],
        value=30,
        help="Smaller = more detail but slower (more API calls)."
    )
with col_go:
    st.write("")  # spacer
    run_globe = st.button("🌍 Build Globe", type="primary")

if run_globe:
    with st.spinner(f"Fetching temperature data for global {grid_step}° grid... this may take a few minutes"):
        grid_data = fetch_temperature_grid(
            step=grid_step,
            start_year=year_range[0],
            end_year=year_range[1],
        )

    if len(grid_data) == 0:
        st.error("No data returned. Check your network connection.")
    else:
        with st.spinner("Computing Mann-Kendall trends for each grid point..."):
            trend_df = compute_grid_trends(grid_data)

        st.success(f"Analyzed {len(trend_df)} grid points.")

        fig = render_trend_globe(
            trend_df,
            title="Global Surface Temperature Trends",
            colorbar_label="°C / decade",
        )
        st.plotly_chart(fig, use_container_width=True)

        n_sig = trend_df["is_significant"].sum()
        st.info(
            f"**{n_sig} / {len(trend_df)}** grid points show a statistically "
            f"significant trend (p < 0.05)."
        )
