# 🌍 Earth System Trend Detective

**NASA Space Apps GO 2026** — _Be An Earth System Trend Detective!_

> Change is always occurring in Earth's interconnected environmental system.
> A variable can trend one way in one region and the opposite way in another,
> even when the same process drives both.

## What This App Does

An interactive web application that lets you explore how Earth system variables
trend over time and space, and discover whether those trends are **statistically
significant** using the Mann-Kendall test.

### Features

- 🌐 **3D Interactive Globe** — Rotatable Earth with color-coded trend magnitudes
- 📈 **Time-Series Analysis** — Monthly data with Sen's slope trend lines
- 📊 **Statistical Significance** — Mann-Kendall test with p-value overlays
- 🔀 **Dual-Region Comparison** — See opposite trends driven by the same process

### Variables

| Variable | Source | Time Range |
|---|---|---|
| Surface Temperature | NASA POWER | 1981–present |
| Sea Ice Extent | NSIDC Sea Ice Index | 1979–present |
| Sea Level Anomaly | NASA/JPL PODAAC | 1993–present |

---

## Quick Start

### Option 1: Docker (recommended — works on any machine)

```bash
docker compose up --build
# Open http://localhost:8501
```

### Option 2: Local Python

```bash
pip install -r requirements.txt
streamlit run app/main.py
# Open http://localhost:8501
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your NASA Earthdata credentials:

```bash
cp .env.example .env
```

---

## Project Structure

```
earth-trend-detective/
├── app/                    # Streamlit UI
│   ├── main.py             # Landing page
│   ├── pages/              # Multi-page app
│   │   ├── 1_🌡️_Temperature.py
│   │   ├── 2_🌊_Sea_Level.py
│   │   ├── 3_🧊_Ice_Extent.py
│   │   └── 4_🔀_Compare.py
│   ├── components/         # Reusable visualization components
│   │   ├── globe.py
│   │   ├── timeseries.py
│   │   └── significance.py
│   └── config.py
├── engine/                 # Data fetching + analysis
│   ├── data_fetcher.py
│   ├── trend_engine.py
│   └── region_compare.py
├── data/cache/             # Cached API responses (gitignored)
├── tests/                  # Unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── Makefile
```

---

## NASA Dataset Citations

1. **NASA POWER Project** — Prediction of Worldwide Energy Resources.
   NASA Langley Research Center.
   https://power.larc.nasa.gov/

2. **NSIDC Sea Ice Index, Version 3** — Fetterer, F., K. Knowles,
   W. N. Meier, M. Savoie, and A. K. Windnagel.
   National Snow and Ice Data Center.
   https://nsidc.org/data/seaice_index/

3. **NASA/JPL PODAAC** — Sea Level data from satellite altimetry.
   https://podaac.jpl.nasa.gov/

---

## License

Built for NASA Space Apps GO 2026. Open source for educational purposes.
