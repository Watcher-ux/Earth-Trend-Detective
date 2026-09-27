"""
Significance display components — summary cards, metric tables, and
helper functions for rendering Mann-Kendall results in Streamlit.
"""
import streamlit as st
import pandas as pd

from engine.trend_engine import TrendResult


def render_trend_metrics(trend: TrendResult) -> None:
    """
    Display key trend metrics as Streamlit metric cards in a row.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Trend Direction",
            value=trend.trend.title(),
            delta=f"{trend.slope_per_decade:+.4f}/decade",
            delta_color="normal" if trend.trend == "increasing" else "inverse",
        )

    with col2:
        st.metric(
            label="Kendall's τ",
            value=f"{trend.tau:+.4f}",
            help="Correlation coefficient (-1 to +1). Closer to ±1 = stronger trend.",
        )

    with col3:
        st.metric(
            label="p-value",
            value=f"{trend.p_value:.4f}",
            delta="Significant" if trend.is_significant else "Not significant",
            delta_color="normal" if trend.is_significant else "off",
        )

    with col4:
        st.metric(
            label="Observations",
            value=f"{trend.n_observations}",
            help=f"Monthly data points from {trend.start_year} to {trend.end_year}",
        )


def render_significance_explainer() -> None:
    """
    Show a brief explanation of statistical significance for non-experts.
    """
    with st.expander("ℹ️ What does 'statistically significant' mean?"):
        st.markdown("""
        **Mann-Kendall Test** — a standard method used by climate scientists
        to determine if a time series has a real, consistent trend — not just
        random fluctuation.

        - **p-value < 0.05** → the trend is **significant** (less than 5%
          chance it's due to randomness)
        - **p-value ≥ 0.05** → we can't confidently say there's a trend

        **Sen's Slope** — a robust estimate of _how fast_ the variable is
        changing per year (or per decade). Unlike ordinary regression, it
        isn't thrown off by outliers.

        **Kendall's τ (tau)** — a correlation measure from -1 to +1 showing
        how consistently the data moves in one direction.
        """)


def render_comparison_table(trends: list[TrendResult]) -> None:
    """
    Render a side-by-side comparison table for multiple TrendResults.
    """
    rows = []
    for t in trends:
        rows.append({
            "Region": t.region,
            "Trend": t.trend.title(),
            "Slope/Decade": f"{t.slope_per_decade:+.4f}",
            "p-value": f"{t.p_value:.4f}",
            "Significant?": "✅" if t.is_significant else "❌",
            "τ": f"{t.tau:+.4f}",
            "Years": f"{t.start_year}–{t.end_year}",
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )
