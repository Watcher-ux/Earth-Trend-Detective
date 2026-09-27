"""
Interactive time-series chart with linear trend overlay and significance annotation.
"""
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from engine.trend_engine import TrendResult


def render_timeseries(
    dates: pd.Series,
    values: pd.Series,
    trend_result: TrendResult,
    y_label: str = "Value",
    title: str = "",
    color: str = "steelblue",
) -> go.Figure:
    """
    Render time series with:
    - Raw data (scatter markers)
    - 12-month moving average (solid line)
    - Sen's slope trend line (dashed red)
    - Significance annotation box

    Parameters
    ----------
    dates : pd.Series of datetime
    values : pd.Series of float
    trend_result : TrendResult from trend engine
    y_label : str — y-axis label
    title : str — chart title
    color : str — base color for data points/line

    Returns
    -------
    Plotly Figure
    """
    fig = go.Figure()

    # Raw monthly data (subtle markers)
    fig.add_trace(go.Scatter(
        x=dates, y=values,
        mode="markers",
        marker=dict(size=3, color=color, opacity=0.35),
        name="Monthly data",
    ))

    # 12-month centered moving average
    ma = values.rolling(12, center=True, min_periods=6).mean()
    fig.add_trace(go.Scatter(
        x=dates, y=ma,
        mode="lines",
        line=dict(color=color, width=2.5),
        name="12-month moving avg",
    ))

    # Sen's slope trend line
    x_numeric = np.arange(len(values), dtype=float)
    slope_per_step = trend_result.slope_per_year / 12  # per month
    intercept = np.nanmedian(values.values - slope_per_step * x_numeric)
    trend_line = intercept + slope_per_step * x_numeric

    fig.add_trace(go.Scatter(
        x=dates, y=trend_line,
        mode="lines",
        line=dict(color="red", width=2, dash="dash"),
        name=f"Trend: {trend_result.slope_per_decade:+.3f}/decade",
    ))

    # Significance annotation
    if trend_result.is_significant:
        sig_text = f"✅ Significant (p = {trend_result.p_value:.4f})"
        sig_color = "green"
    else:
        sig_text = f"❌ Not significant (p = {trend_result.p_value:.4f})"
        sig_color = "gray"

    fig.add_annotation(
        x=0.02, y=0.98,
        xref="paper", yref="paper",
        text=(
            f"<b>{sig_text}</b><br>"
            f"τ = {trend_result.tau:+.3f} | "
            f"n = {trend_result.n_observations} | "
            f"{trend_result.start_year}–{trend_result.end_year}"
        ),
        showarrow=False,
        font=dict(size=12, color=sig_color),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor=sig_color,
        borderwidth=1,
        align="left",
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title="Date",
        yaxis_title=y_label,
        height=420,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
        ),
    )

    return fig
