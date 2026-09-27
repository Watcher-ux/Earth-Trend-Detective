"""
🌊 Sea Level Trend Explorer

Placeholder page — will be activated once NASA Earthdata auth
is wired up for PODAAC sea level data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

st.set_page_config(page_title="🌊 Sea Level Trends", page_icon="🌊", layout="wide")
st.title("🌊 Sea Level Trends")
st.markdown("*Data: NASA/JPL PODAAC — Satellite altimetry sea level anomaly*")

st.divider()

st.warning(
    "⚠️ **Coming Soon** — This page requires NASA Earthdata authentication "
    "to access PODAAC sea level data.\n\n"
    "**Setup steps:**\n"
    "1. Create an account at https://urs.earthdata.nasa.gov/\n"
    "2. Copy `.env.example` → `.env` and fill in your credentials\n"
    "3. Restart the app\n\n"
    "The Temperature and Ice Extent pages work without authentication."
)

st.divider()

st.markdown("""
### What this page will show

- 📈 **Global Mean Sea Level** time series (1993–present)
- 🌐 **Regional sea level trends** on the 3D globe
- 📊 **Significance testing** — regional differences in sea level rise rates
- 🔀 **Opposite trends** — some regions rise faster due to ocean dynamics,
  while others rise slower or even show temporary decreases

### Why sea level matters for this challenge

Sea level rise is one of the clearest integrated signals of climate change,
combining thermal expansion, ice sheet melt, and ocean dynamics. Different
regions experience different rates — a perfect example of the challenge's
"same process, opposite trends" theme.
""")
