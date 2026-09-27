"""
Application configuration and constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --- NASA Earthdata credentials (for PODAAC sea level data) ---
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME", "")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD", "")

# --- API endpoints ---
NASA_POWER_BASE = "https://power.larc.nasa.gov/api/temporal"

# --- Analysis defaults ---
DEFAULT_ALPHA = 0.05          # significance level for Mann-Kendall
STEPS_PER_YEAR = 12           # monthly data

# --- UI constants ---
APP_TITLE = "🌍 Earth System Trend Detective"
APP_ICON = "🌍"

# --- Color scales ---
TREND_COLORSCALE = "RdBu_r"   # red = warming/increasing, blue = cooling/decreasing
