"""
🔀 Dual-Region Trend Comparison

Pre-built scenarios that demonstrate the challenge's core insight:
the same physical process can drive opposite trends in different regions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from engine.region_compare import COMPARISON_PRESETS, run_comparison
from app.components.timeseries import render_timeseries
from app.components.significance import (
    render_comparison_table,
    render_significance_explainer,
)
from engine.data_fetcher import fetch_temperature, fetch_sea_ice_extent

st.set_page_config(page_title="🔀 Compare Regions", page_icon="🔀", layout="wide")
st.title("🔀 Dual-Region Trend Comparison")
st.markdown(
    "*The same physical process can drive opposite trends in different regions. "
    "Select a preset scenario below to explore this.*"
)

render_significance_explainer()

st.divider()

# --- Preset selector ---
preset_key = st.selectbox(
    "Choose a comparison scenario",
    options=list(COMPARISON_PRESETS.keys()),
    format_func=lambda k: COMPARISON_PRESETS[k]["title"],
)

preset = COMPARISON_PRESETS[preset_key]
st.info(preset["description"])

if st.button("🔍 Run Comparison", type="primary"):
    with st.spinner("Fetching data and computing trends..."):
        result = run_comparison(preset_key)

    st.divider()
    st.header(result.title)

    # Comparison table
    render_comparison_table([result.trend_a, result.trend_b])

    # Opposite trend callout
    if result.are_opposite:
        st.success(
            "🎯 **Opposite trends detected!** — These two regions show "
            "trends in opposite directions, both driven by the same "
            "underlying process."
        )
    else:
        rate_a = abs(result.trend_a.slope_per_decade)
        rate_b = abs(result.trend_b.slope_per_decade)
        if rate_a > 0 and rate_b > 0:
            ratio = max(rate_a, rate_b) / min(rate_a, rate_b)
            st.info(
                f"📊 Both regions trend in the same direction, but at "
                f"**{ratio:.1f}× different rates** — showing how the same "
                f"process affects regions differently."
            )

    # Side-by-side time series
    col_a, col_b = st.columns(2)

    if preset["type"] == "sea_ice":
        df = fetch_sea_ice_extent()
        with col_a:
            st.subheader(result.region_a_name)
            fig_a = render_timeseries(
                df["date"], df["arctic_extent_mkm2"],
                result.trend_a,
                y_label="Extent (M km²)",
                title=result.region_a_name,
                color="#1f77b4",
            )
            st.plotly_chart(fig_a, use_container_width=True)
        with col_b:
            st.subheader(result.region_b_name)
            fig_b = render_timeseries(
                df["date"], df["antarctic_extent_mkm2"],
                result.trend_b,
                y_label="Extent (M km²)",
                title=result.region_b_name,
                color="#ff7f0e",
            )
            st.plotly_chart(fig_b, use_container_width=True)

    elif preset["type"] == "temperature":
        regions = preset["regions"]
        for col, region, trend in [
            (col_a, regions[0], result.trend_a),
            (col_b, regions[1], result.trend_b),
        ]:
            with col:
                st.subheader(region["name"])
                df = fetch_temperature(region["lat"], region["lon"])
                fig = render_timeseries(
                    df["date"], df["temperature_c"],
                    trend,
                    y_label="Temperature (°C)",
                    title=region["name"],
                )
                st.plotly_chart(fig, use_container_width=True)
