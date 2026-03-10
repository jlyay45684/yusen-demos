from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Yusen AI Decision Intelligence Console", layout="wide")

st.markdown("""
<style>

.stApp {
    background-color: #0f1115;
    color: #e6e6e6;
}

.main-header {
    font-size: 30px;
    font-weight: 700;
    color: #d1d5db;
    padding-bottom: 10px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #9ca3af;
    margin-top: 25px;
}

.metric-card {
    background: #1a1d23;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #2c2f36;
}

</style>
""", unsafe_allow_html=True)

NUMERIC_COLUMNS = ["inventory", "sales", "price", "cost", "defect_rate", "lead_time"]
DATE_COLUMN = "date"
CATEGORY_COLUMN = "category"


@dataclass
class QualityMetrics:
    missing_cells: int
    duplicate_rows: int
    outlier_cells: int
    invalid_numeric_cells: int
    date_format_errors: int
    quality_score: float


def load_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        return pd.read_csv("sample_data.csv")
    return pd.read_csv(uploaded_file)


def detect_invalid_numeric(df, numeric_columns):
    converted = df.copy()
    invalid_count = 0

    for col in numeric_columns:
        if col in converted.columns:
            coerced = pd.to_numeric(converted[col], errors="coerce")
            invalid_count += ((converted[col].notna()) & (coerced.isna())).sum()
            converted[col] = coerced

    return converted, int(invalid_count)


def detect_date_errors(df, date_col):
    if date_col not in df.columns:
        empty = pd.Series([pd.NaT] * len(df), index=df.index)
        return empty, 0

    parsed = pd.to_datetime(df[date_col], errors="coerce")
    errors = ((df[date_col].notna()) & (parsed.isna())).sum()

    return parsed, int(errors)


def detect_outliers(df, numeric_columns):
    count = 0

    for col in numeric_columns:

        if col not in df.columns:
            continue

        series = df[col].dropna()

        if len(series) < 4:
            continue

        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask = (df[col] < lower) | (df[col] > upper)

        count += int(mask.sum())

    return count


def quality_assessment(df):

    working_df, invalid_numeric_count = detect_invalid_numeric(df, NUMERIC_COLUMNS)

    parsed_dates, date_errors = detect_date_errors(working_df, DATE_COLUMN)

    working_df["parsed_date"] = parsed_dates

    missing_cells = int(working_df.isna().sum().sum())
    duplicate_rows = int(working_df.duplicated().sum())

    outlier_count = detect_outliers(working_df, NUMERIC_COLUMNS)

    total_cells = max(1, working_df.shape[0] * working_df.shape[1])

    penalty = (
        0.40 * (missing_cells / total_cells)
        + 0.15 * (duplicate_rows / max(1, len(working_df)))
        + 0.20 * (outlier_count / total_cells)
        + 0.15 * (invalid_numeric_count / total_cells)
        + 0.10 * (date_errors / max(1, len(working_df)))
    )

    quality_score = round(max(0.0, 100 * (1 - penalty)), 2)

    metrics = QualityMetrics(
        missing_cells,
        duplicate_rows,
        outlier_count,
        invalid_numeric_count,
        date_errors,
        quality_score,
    )

    return working_df, metrics


def main():

    st.markdown('<div class="main-header">Yusen AI Decision Intelligence Console</div>', unsafe_allow_html=True)
    st.caption("Enterprise AI4BI Dashboard Demo")

    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])

    df = load_data(uploaded_file)

    st.markdown('<div class="section-title">Dataset Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", int(df.isna().sum().sum()))
    c4.metric("Duplicates", int(df.duplicated().sum()))

    working_df, metrics = quality_assessment(df)

    st.markdown('<div class="section-title">Data Quality</div>', unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)

    q1.metric("Quality Score", metrics.quality_score)
    q2.metric("Invalid Numbers", metrics.invalid_numeric_cells)
    q3.metric("Date Errors", metrics.date_format_errors)

    st.markdown('<div class="section-title">Analytics Dashboard</div>', unsafe_allow_html=True)

    numeric_options = [c for c in NUMERIC_COLUMNS if c in working_df.columns]

    metric = st.selectbox("Distribution Metric", numeric_options)

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(working_df, x=metric)

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        if {"parsed_date", "sales"}.issubset(working_df.columns):

            trend = (
                working_df.dropna(subset=["parsed_date", "sales"])
                .groupby("parsed_date", as_index=False)["sales"]
                .sum()
            )

            fig2 = px.line(trend, x="parsed_date", y="sales")

            st.plotly_chart(fig2, use_container_width=True)

    if CATEGORY_COLUMN in working_df.columns:

        agg = working_df.groupby(CATEGORY_COLUMN, as_index=False)["sales"].sum()

        fig3 = px.bar(agg, x=CATEGORY_COLUMN, y="sales")

        st.plotly_chart(fig3, use_container_width=True)


if __name__ == "__main__":
    main()