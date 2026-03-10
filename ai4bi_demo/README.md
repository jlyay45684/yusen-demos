# AI Decision Intelligence Console

A lightweight, professional AI + BI demo built with **Python, Pandas, Streamlit, and Plotly**.

This project demonstrates practical data intelligence workflows that are relevant for **AI4BI, AI/ML, and Data Analysis** roles:
- data validation
- anomaly detection
- consistency checks
- analytics dashboards
- recommendation-driven decision support

## Features

### 1) Data Upload
- Upload any CSV file (or use the built-in sample dataset).
- Instant profile summary:
  - row count
  - column count
  - missing values
  - column data types

### 2) Data Validation
Detects and reports:
- missing values
- duplicate rows
- outliers (IQR method)
- invalid numeric values
- date format errors

Outputs a simple **Data Quality Score (0–100)**.

### 3) Consistency Check
Flags business logic issues such as:
- negative inventory
- unreasonable sales levels
- price lower than cost
- date/lead-time order errors

Shows problematic rows for quick review.

### 4) Analytics (Plotly)
Interactive charts:
- numeric distribution
- sales trend over time
- category-level aggregation

### 5) Decision Support
Builds a priority ranking based on:
- data quality impact
- risk level
- anomaly frequency

Generates practical recommendations:
- what to clean first
- what anomalies to investigate
- what requires manual review

### 6) Workflow Router
Automatically sets the analysis mode based on data condition:
- **Standard Analysis**
- **Risk Review**
- **Priority Decision**

## Project Structure

```text
app.py
requirements.txt
sample_data.csv
README.md
```

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
streamlit run app.py
```

Then open the Streamlit URL shown in terminal (usually `http://localhost:8501`).

## Dataset Included

`sample_data.csv` includes intentional issues for demo realism:
- missing values
- invalid numeric values
- negative numbers
- inconsistent/invalid dates
- duplicate row
- unreasonable sales outlier

## Why This Fits AI4BI / AI-ML Roles

This demo reflects real workplace tasks where AI is applied to business data quality and decision workflows:
- **Data reliability first**: validates data before modeling or reporting.
- **Explainable anomaly detection**: simple, transparent rules and outlier methods.
- **Business-aware logic checks**: goes beyond pure statistics into domain consistency.
- **Decision-oriented output**: turns diagnostics into ranked actions.
- **Production-friendly simplicity**: no external APIs, easy to run and extend.

## Next Enhancements (Optional)
- Add downloadable validation report (CSV/PDF).
- Add model-based anomaly scoring (Isolation Forest) as an optional mode.
- Add role-based KPI presets by business domain.
