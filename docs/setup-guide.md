# Setup Guide

This guide provides step-by-step instructions to get the Drishti Predictive Crime Hotspot Mapping Assistant running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.9+** (Tested on Python 3.11/3.12)
- **Git** (to clone the repository)

## Step-by-Step Installation

### 1. Clone the Repository
Clone the project to your local machine and navigate into the project directory:

```bash
git clone https://github.com/your-github-username/bob-ai-hackathon-ananta.git
cd bob-ai-hackathon-ananta/src
```

> **Note:** All application code is located inside the `src/` directory.

### 2. Set Up a Virtual Environment (Recommended)
It is highly recommended to use a virtual environment to manage dependencies:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install Streamlit, Pandas, Plotly, ReportLab, and other required libraries.

### 4. Environment Variables
This MVP does not require API keys or external database connections to run. The `.env.example` file is provided for structural completeness. 

```bash
cp .env.example .env
```
*(No edits to `.env` are required for the standard demo).*

## Running the Application

### 1. Generate Synthetic Data (Optional)
We have provided a pre-generated 6-month synthetic crime dataset (`crime_data.csv`). However, if you wish to generate a fresh dataset with new patterns:

```bash
python generate_data.py
```
*This will create a new `crime_data.csv` file with 1,150 synthetic records.*

### 2. Launch the Streamlit Dashboard
Start the application by running:

```bash
streamlit run app.py
```

### 3. Access the App
Once started, Streamlit will provide a local URL in your terminal. Open your browser and navigate to:
```
http://localhost:8501
```

## How to Test the Demo

1. **Upload Data**: By default, the app uses the `crime_data.csv` in the `src/` folder. You can also manually upload it using the sidebar.
2. **View Insights**: Click through the 5 tabs at the top (Hotspot Map, Zone Analysis, What-If Simulator, Patrol Plan, SHO Report).
3. **Run a Scenario**: Go to the "What-If Simulator" tab, select "Festival" and a high-risk zone (e.g., Area-12), and click "Run Simulation".
4. **Download Report**: Go to the "SHO Report" tab and click "Generate SHO Report" to test the PDF export functionality.

## Troubleshooting

| Error | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | Ensure you have activated your virtual environment and run `pip install -r requirements.txt`. |
| `FileNotFoundError: [Errno 2] No such file or directory: 'crime_data.csv'` | Ensure you are running the `streamlit run app.py` command from *inside* the `src/` directory. |
| Plotly `ValueError: Invalid property specified for object` | Ensure you are using the versions specified in `requirements.txt`. We fixed a known issue with older Plotly syntax. |
