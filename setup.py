from setuptools import setup, find_packages

setup(
    name="earth-trend-detective",
    version="0.1.0",
    description="NASA Space Apps GO 2026 — Earth System Trend Detective",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "streamlit>=1.35.0",
        "plotly>=5.22.0",
        "pandas>=2.2.0",
        "numpy>=1.26.0",
        "requests>=2.31.0",
        "pymannkendall>=1.4.3",
        "xarray>=2024.1.0",
        "netcdf4>=1.6.0",
        "pydeck>=0.9.0",
        "scipy>=1.12.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "earth-trend-detective=app.main:main",
        ],
    },
)
