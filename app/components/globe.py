"""
3D interactive globe using Plotly Scattergeo with orthographic projection.
Displays trend magnitude as color, significance as opacity.
"""
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from app.config import TREND_COLORSCALE


def render_trend_globe(
    trend_df: pd.DataFrame,
    title: str = "Global Trend Map",
    colorbar_label: str = "Slope (units/decade)",
    slope_col: str = "slope_per_decade",
    sig_col: str = "is_significant",
) -> go.Figure:
    """
    Render an interactive 3D globe showing trend slopes.

    Parameters
    ----------
    trend_df : DataFrame with columns [lat, lon, slope_per_decade, is_significant]
    title : str
    colorbar_label : str
    slope_col : str — column to map to color
    sig_col : str — column for significance masking

    Returns
    -------
    Plotly Figure with orthographic globe projection
    """
    slopes = trend_df[slope_col].values
    significant = trend_df[sig_col].values

    # Symmetric color range centered on zero
    vmax = np.nanpercentile(np.abs(slopes), 95)

    # Opacity: significant = full, non-significant = faded
    opacities = np.where(significant, 0.85, 0.15)

    # Hover text
    hover_text = [
        f"({row.lat:.0f}°, {row.lon:.0f}°)<br>"
        f"Slope: {row[slope_col]:+.4f}/decade<br>"
        f"p = {row.p_value:.4f}<br>"
        f"{'✅ Significant' if row[sig_col] else '❌ Not significant'}"
        for _, row in trend_df.iterrows()
    ]

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lat=trend_df["lat"],
        lon=trend_df["lon"],
        marker=dict(
            size=8,
            color=slopes,
            colorscale=TREND_COLORSCALE,
            cmin=-vmax,
            cmax=vmax,
            opacity=opacities,
            colorbar=dict(
                title=colorbar_label,
                thickness=15,
                len=0.6,
            ),
            line=dict(width=0.3, color="gray"),
        ),
        text=hover_text,
        hoverinfo="text",
        showlegend=False,
    ))

    fig.update_geos(
        projection_type="orthographic",
        showcoastlines=True,
        coastlinecolor="Gray",
        showland=True,
        landcolor="rgb(243, 243, 243)",
        showocean=True,
        oceancolor="rgb(204, 229, 255)",
        showlakes=True,
        lakecolor="rgb(204, 229, 255)",
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        height=650,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            projection_rotation=dict(lon=0, lat=20),
        ),
    )

    return fig
