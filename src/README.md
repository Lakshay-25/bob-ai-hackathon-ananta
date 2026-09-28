# Source Code — Drishti

All application source code for the **Drishti Predictive Crime Hotspot Mapping Assistant** lives in this directory.

## Structure

```
src/
├── app.py               ← Main Streamlit dashboard (entry point)
├── analytics.py         ← Risk scoring engine, patrol optimizer, zone explainer
├── simulator.py         ← What-If event simulator (festivals, markets, rallies)
├── report_generator.py  ← PDF SHO Intelligence Brief generator (ReportLab)
├── generate_data.py     ← Synthetic crime dataset generator (run once to refresh data)
├── crime_data.csv       ← Pre-generated 6-month synthetic crime dataset (1,150 records)
├── .env.example         ← Template for environment variables (copy to .env)
└── requirements.txt     ← Python dependency manifest
```

## How to Run

From inside this `src/` directory:

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit dashboard
streamlit run app.py
```

See [`../docs/setup-guide.md`](../docs/setup-guide.md) for the full step-by-step setup guide including virtual environment setup and troubleshooting.

## Module Descriptions

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI — renders all 5 tabs: Hotspot Map, Zone Analysis, What-If Simulator, Patrol Plan, SHO Report |
| `analytics.py` | Multi-factor risk scoring (recency + trend + baseline), plain-language zone explanations, patrol window optimizer |
| `simulator.py` | Historical event multiplier calculator; applies event-type impacts (Festival, Rally, etc.) to baseline risk scores |
| `report_generator.py` | Compiles top-5 zones, evidence, patrol recommendations, and simulator results into a downloadable PDF brief |
| `generate_data.py` | Generates a synthetic 1,150-record crime dataset across 50 micro-zones with realistic temporal patterns |
| `crime_data.csv` | Pre-generated dataset — used by default so judges can run the app without regenerating data |
