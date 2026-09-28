# 🚀 Drishti — Predictive Crime Hotspot Mapping Assistant

> **IBM Bob AI Hackathon 2026 Submission** | **Track 4: AI & Predictive**

---

## 👥 Team Ananta

| Field | Value |
|---|---|
| **Team Name** | Ananta |
| **Track** | AI & Predictive |
| **Team Lead** | Lakshay Sunil Jatawat — lakshayjatawat25@gmail.com |
| **Members** | Kunj Buddhdev, Deeksha, Jiya Joshi |

---

## 🎯 Problem Statement

Indian police stations, like those using Delhi's ZIPNET system, sit on years of geo-tagged crime data but have zero predictive intelligence layer. Beat officers patrol static, fixed routes regardless of emerging spatial-temporal crime patterns. District Station House Officers (SHOs) lack accessible tools to anticipate where crime may spike next week, how upcoming events could shift risk, or how to optimally redeploy limited patrol units. 

*(See [`docs/problem-statement.md`](docs/problem-statement.md) for full details)*

---

## 💡 Solution

**Drishti** is an explainable AI-powered crime intelligence assistant built with IBM Bob for district-level police stations. It ingests historical crime data, performs spatial-temporal pattern analysis using near-repeat theory, predicts the top 5 at-risk areas for the coming week, and simulates the impact of upcoming events. Finally, it generates optimized patrol redeployment recommendations and a downloadable SHO intelligence brief.

*(See [`docs/solution-overview.md`](docs/solution-overview.md) for full details)*

---

## ✨ Key Features

- **Spatial-Temporal Pattern Detection**: Analyzes near-repeat crime patterns and recency-weighted scoring across micro-zones.
- **Top-5 At-Risk Zone Prediction**: Explains exactly *why* zones are flagged using plain-language rationale.
- **What-If Event Simulator**: Allows officers to proactively model how festivals, markets, or rallies will shift crime risk.
- **Automated Patrol Planning**: Recommends optimal deployment time-windows based on zone-specific historical data.
- **SHO Intelligence Brief**: Generates a professional, one-page PDF report ready for daily roll call.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | Streamlit, Pandas, Plotly, NumPy |
| **IBM Technologies** | IBM Bob |
| **Reporting** | ReportLab, Matplotlib |

---

## 📁 Repository Structure

```
├── src/                  # All source code (Streamlit app, Analytics Engine, Simulator)
│   ├── app.py            # Main Streamlit Dashboard
│   ├── analytics.py      # Risk scoring & patrol logic
│   ├── simulator.py      # What-If event engine
│   ├── report_generator.py # PDF export logic
│   ├── generate_data.py  # Synthetic data creator
│   ├── crime_data.csv    # Generated synthetic dataset
│   └── requirements.txt  # Python dependencies
├── docs/                 # Written documentation
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/                 # Demo artifacts
│   ├── screenshots/      # App screenshots
│   ├── demo-video-link.txt  # Link to demo video
│   └── live-demo-url.txt    # Optional live deployment link
├── presentation/         # Slide deck
└── submission.yaml       # Structured submission metadata
```

---

## ⚡ How to Run

> **Copy these exact steps from your [`docs/setup-guide.md`](docs/setup-guide.md)**

```bash
# 1. Clone the repo
git clone https://github.com/your-github-username/bob-ai-hackathon-ananta.git
cd bob-ai-hackathon-ananta/src

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run the project
streamlit run app.py
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | NOT DEPLOYED |
| 🌐 Live Demo | NOT DEPLOYED |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations

- **Synthetic Data**: The MVP uses 1000+ generated mock crime records rather than real police records (due to data access limitations).
- **Heuristic Model**: The risk scoring model is a weighted heuristic demonstration rather than a fully calibrated probabilistic forecast (like LightGBM).
- **Grid Mapping**: Map visualization uses a grid-based layout rather than real GIS/H3 hexagonal spatial indexing.
- **Access Control**: Role-based access control (SHO vs. Beat Officer views) is not implemented in this MVP.

---

## 🏅 What We're Most Proud Of

We are most proud of the **complete end-to-end intelligence pipeline** tailored specifically for law enforcement end-users. Instead of black-box predictions, Drishti provides plain-language explanations that a non-technical Station House Officer can immediately understand and trust. Furthermore, the **What-If Event Simulator** shifts the paradigm from reactive policing to proactive planning, allowing commanders to test deployment strategies before events occur.
