import streamlit as st

st.set_page_config(
    page_title="🌍 Earth Trend Detective",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌍 Earth System Trend Detective")
st.markdown("""
**NASA Space Apps GO 2026** — *Be An Earth System Trend Detective!*

> Change is always occurring in Earth's interconnected system.
> A variable can trend one way in one region and the opposite in another,
> even when the same process drives both.

---

### What This App Does

Pick an Earth system variable, explore how it trends across **time and space**,
and discover whether those trends are **statistically significant**.

| Feature | Description |
|---|---|
| 🌐 **3D Globe** | Rotatable Earth with color-coded trend magnitudes |
| 📈 **Time Series** | Monthly data with Sen's slope trend lines |
| 📊 **Significance** | Mann-Kendall p-value — solid = significant, faded = not |
| 🔀 **Compare** | See opposite trends driven by the same process |

👈 **Select a variable from the sidebar** to begin exploring.

---

### Data Sources

| Variable | Source | Coverage |
|---|---|---|
| Surface Temperature (T2M) | [NASA POWER](https://power.larc.nasa.gov/) | 1981–present |
| Sea Ice Extent | [NSIDC Sea Ice Index v3](https://nsidc.org/data/seaice_index/) | 1979–present |
| Sea Level Anomaly | [NASA/JPL PODAAC](https://podaac.jpl.nasa.gov/) | 1993–present |

---

*Built for NASA Space Apps GO 2026 · Data: NASA POWER, NSIDC, PODAAC*
""")
