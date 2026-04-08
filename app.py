from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AI Decision Intelligence Console", layout="wide")

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


def detect_invalid_numeric(df: pd.DataFrame, numeric_columns: list[str]) -> tuple[pd.DataFrame, int]:
    converted = df.copy()
    invalid_count = 0
    for col in numeric_columns:
        if col in converted.columns:
            coerced = pd.to_numeric(converted[col], errors="coerce")
            invalid_count += ((converted[col].notna()) & (coerced.isna())).sum()
            converted[col] = coerced
    return converted, int(invalid_count)


def detect_date_errors(df: pd.DataFrame, date_col: str) -> tuple[pd.Series, int]:
    if date_col not in df.columns:
        empty = pd.Series([pd.NaT] * len(df), index=df.index)
        return empty, 0
    parsed = pd.to_datetime(df[date_col], errors="coerce")
    errors = ((df[date_col].notna()) & (parsed.isna())).sum()
    return parsed, int(errors)


def detect_outliers(df: pd.DataFrame, numeric_columns: list[str]) -> tuple[pd.DataFrame, int]:
    outlier_flags = pd.DataFrame(False, index=df.index, columns=numeric_columns)
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
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (df[col] < lower) | (df[col] > upper)
        outlier_flags[col] = mask.fillna(False)
        count += int(mask.sum())

    return outlier_flags, count


def quality_assessment(df: pd.DataFrame) -> tuple[pd.DataFrame, QualityMetrics, pd.Series, pd.DataFrame]:
    working_df, invalid_numeric_count = detect_invalid_numeric(df, NUMERIC_COLUMNS)
    parsed_dates, date_errors = detect_date_errors(working_df, DATE_COLUMN)
    working_df["parsed_date"] = parsed_dates

    missing_cells = int(working_df.isna().sum().sum())
    duplicate_rows = int(working_df.duplicated().sum())
    outlier_flags, outlier_count = detect_outliers(working_df, NUMERIC_COLUMNS)

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
        missing_cells=missing_cells,
        duplicate_rows=duplicate_rows,
        outlier_cells=outlier_count,
        invalid_numeric_cells=invalid_numeric_count,
        date_format_errors=date_errors,
        quality_score=quality_score,
    )
    return working_df, metrics, parsed_dates, outlier_flags


def consistency_checks(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    checks = {}

    if "inventory" in df.columns:
        checks["Negative inventory"] = df[df["inventory"] < 0]

    if {"sales", "inventory", "price"}.issubset(df.columns):
        unreasonable_sales = (df["sales"] > (df["inventory"].clip(lower=0) * 2)) | (df["sales"] > 5000)
        checks["Unreasonable sales volume"] = df[unreasonable_sales.fillna(False)]

    if {"price", "cost"}.issubset(df.columns):
        checks["Price lower than cost"] = df[df["price"] < df["cost"]]

    if {"parsed_date", "lead_time"}.issubset(df.columns):
        implied_delivery = df["parsed_date"] + pd.to_timedelta(df["lead_time"].fillna(0), unit="D")
        checks["Date order errors (invalid date or lead_time < 0)"] = df[df["parsed_date"].isna() | (df["lead_time"] < 0) | implied_delivery.isna()]

    return checks


def workflow_mode(metrics: QualityMetrics, consistency_issues: dict[str, pd.DataFrame], total_rows: int) -> str:
    issue_rows = sum(len(v) for v in consistency_issues.values())
    if metrics.quality_score < 75 or issue_rows > max(3, int(0.30 * total_rows)):
        return "Risk Review"
    if metrics.quality_score < 88 or metrics.outlier_cells > 5:
        return "Priority Decision"
    return "Standard Analysis"


def build_recommendations(metrics: QualityMetrics, consistency_issues: dict[str, pd.DataFrame]) -> pd.DataFrame:
    items = [
        {
            "Area": "Data Cleaning",
            "Data Quality Impact": metrics.missing_cells + metrics.invalid_numeric_cells + metrics.date_format_errors,
            "Risk Level": metrics.duplicate_rows + metrics.date_format_errors,
            "Anomaly Frequency": metrics.outlier_cells,
        },
        {
            "Area": "Inventory & Sales Validation",
            "Data Quality Impact": len(consistency_issues.get("Negative inventory", [])),
            "Risk Level": len(consistency_issues.get("Unreasonable sales volume", [])) + len(consistency_issues.get("Price lower than cost", [])),
            "Anomaly Frequency": len(consistency_issues.get("Unreasonable sales volume", [])),
        },
        {
            "Area": "Manual Business Review",
            "Data Quality Impact": len(consistency_issues.get("Date order errors (invalid date or lead_time < 0)", [])),
            "Risk Level": len(consistency_issues.get("Date order errors (invalid date or lead_time < 0)", [])),
            "Anomaly Frequency": metrics.outlier_cells // 2,
        },
    ]
    rec_df = pd.DataFrame(items)
    rec_df["Priority Score"] = (
        0.45 * rec_df["Data Quality Impact"] + 0.35 * rec_df["Risk Level"] + 0.20 * rec_df["Anomaly Frequency"]
    )
    rec_df = rec_df.sort_values("Priority Score", ascending=False).reset_index(drop=True)
    return rec_df


def main() -> None:
    st.title("AI Decision Intelligence Console")
    st.caption("A compact AI-for-BI demo for data validation, anomaly detection, analytics, and decision support")

    uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])
    df = load_data(uploaded_file)

    st.subheader("1) Data Upload Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", int(df.isna().sum().sum()))
    c4.metric("Duplicate Rows", int(df.duplicated().sum()))

    with st.expander("Column Types"):
        st.dataframe(pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str)}), use_container_width=True)

    working_df, metrics, _, _ = quality_assessment(df)

    st.subheader("2) Data Validation")
    q1, q2, q3 = st.columns(3)
    q1.metric("Data Quality Score", f"{metrics.quality_score}/100")
    q2.metric("Invalid Numbers", metrics.invalid_numeric_cells)
    q3.metric("Date Format Errors", metrics.date_format_errors)

    validation_table = pd.DataFrame(
        {
            "Issue": [
                "Missing values",
                "Duplicate rows",
                "Outliers",
                "Invalid numeric values",
                "Date format errors",
            ],
            "Count": [
                metrics.missing_cells,
                metrics.duplicate_rows,
                metrics.outlier_cells,
                metrics.invalid_numeric_cells,
                metrics.date_format_errors,
            ],
        }
    )
    st.dataframe(validation_table, use_container_width=True)

    st.subheader("3) Consistency Check")
    consistency = consistency_checks(working_df)
    for check_name, bad_rows in consistency.items():
        with st.expander(f"{check_name}: {len(bad_rows)} problematic rows"):
            st.dataframe(bad_rows, use_container_width=True)

    mode = workflow_mode(metrics, consistency, len(working_df))
    st.subheader("6) Workflow Router")
    st.info(f"Current Mode: **{mode}**")

    st.subheader("4) Analytics")
    numeric_options = [c for c in NUMERIC_COLUMNS if c in working_df.columns]
    selected_metric = st.selectbox("Distribution metric", options=numeric_options, index=1 if len(numeric_options) > 1 else 0)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_dist = px.histogram(working_df, x=selected_metric, nbins=20, title=f"Distribution of {selected_metric}")
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_b:
        if {"parsed_date", "sales"}.issubset(working_df.columns):
            trend_df = (
                working_df.dropna(subset=["parsed_date", "sales"])
                .groupby("parsed_date", as_index=False)["sales"]
                .sum()
                .sort_values("parsed_date")
            )
            fig_trend = px.line(trend_df, x="parsed_date", y="sales", title="Sales Trend Over Time")
            st.plotly_chart(fig_trend, use_container_width=True)

    if CATEGORY_COLUMN in working_df.columns and "sales" in working_df.columns:
        agg_df = working_df.groupby(CATEGORY_COLUMN, as_index=False)["sales"].sum().sort_values("sales", ascending=False)
        fig_cat = px.bar(agg_df, x=CATEGORY_COLUMN, y="sales", title="Category Sales Aggregation")
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("5) Decision Support")
    rec_df = build_recommendations(metrics, consistency)
    st.dataframe(rec_df, use_container_width=True)

    top_area = rec_df.iloc[0]["Area"]
    st.success(
        f"Top recommendation: prioritize **{top_area}**. Start with rows failing validation checks, then investigate"
        " high-risk anomalies and assign manual review for unresolved date/business-rule issues."
    )

    with st.expander("Preview data"):
        st.dataframe(df.head(30), use_container_width=True)


if __name__ == "__main__":
    main()
