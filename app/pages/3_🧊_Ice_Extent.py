"""
🧊 Sea Ice Extent Trend Explorer

Fetches Arctic and Antarctic monthly sea ice extent from NSIDC,
runs Mann-Kendall analysis on both hemispheres, and shows how the
same greenhouse forcing drives very different ice trends at each pole.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from engine.data_fetcher import fetch_sea_ice_extent
from engine.trend_engine import compute_trend
from app.components.timeseries import render_timeseries
from app.components.significance import (
    render_trend_metrics,
    render_significance_explainer,
    render_comparison_table,
)

st.set_page_config(page_title="🧊 Sea Ice Trends", page_icon="🧊", layout="wide")
st.title("🧊 Sea Ice Extent Trends")
st.markdown("*Data: NSIDC Sea Ice Index v3 — Monthly Arctic & Antarctic sea ice extent*")

render_significance_explainer()

st.divider()

if st.button("🔍 Analyze Sea Ice Trends", type="primary"):
    with st.spinner("Fetching sea ice data from NSIDC..."):
        df = fetch_sea_ice_extent()

    if len(df) < 10:
        st.error("Could not fetch sea ice data. Check your connection.")
    else:
        st.success(f"Loaded {len(df)} months of data ({df['date'].min().year}–{df['date'].max().year})")

        # --- Arctic ---
        st.header("🏔️ Arctic Sea Ice")
        arctic_trend = compute_trend(
            dates=df["date"],
            values=df["arctic_extent_mkm2"],
            variable_name="Sea Ice Extent",
            region_name="Arctic",
        )
        render_trend_metrics(arctic_trend)
        fig_arctic = render_timeseries(
            dates=df["date"],
            values=df["arctic_extent_mkm2"],
            trend_result=arctic_trend,
            y_label="Extent (million km²)",
            title="Arctic Sea Ice Extent",
            color="#1f77b4",
        )
        st.plotly_chart(fig_arctic, use_container_width=True)

        st.divider()

        # --- Antarctic ---
        st.header("🐧 Antarctic Sea Ice")
        antarctic_trend = compute_trend(
            dates=df["date"],
            values=df["antarctic_extent_mkm2"],
            variable_name="Sea Ice Extent",
            region_name="Antarctic",
        )
        render_trend_metrics(antarctic_trend)
        fig_antarctic = render_timeseries(
            dates=df["date"],
            values=df["antarctic_extent_mkm2"],
            trend_result=antarctic_trend,
            y_label="Extent (million km²)",
            title="Antarctic Sea Ice Extent",
            color="#ff7f0e",
        )
        st.plotly_chart(fig_antarctic, use_container_width=True)

        st.divider()

        # --- Side-by-side comparison ---
        st.header("🔀 Arctic vs Antarctic — Same Forcing, Different Trends")
        st.markdown("""
        > Both poles experience the same increase in greenhouse gases, yet Arctic
        > sea ice shows **dramatic decline** while Antarctic ice has shown more
        > complex, variable behavior. This is because:
        > - The **Arctic** is an ocean surrounded by land → direct ice-albedo feedback
        > - The **Antarctic** is a continent surrounded by ocean → wind and current
        >   patterns can temporarily *increase* ice extent even as the planet warms
        """)

        render_comparison_table([arctic_trend, antarctic_trend])

        if arctic_trend.is_significant or antarctic_trend.is_significant:
            st.info(
                "💡 This is a textbook example of the challenge theme: "
                "the *same process* (greenhouse warming) driving *different trends* "
                "in different regions."
            )
