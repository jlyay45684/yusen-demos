from dataclasses import dataclass
import io

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Yusen AI Decision Intelligence Console",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --bg: #0b0f17;
    --panel: #111827;
    --panel-2: #0f172a;
    --border: #253046;
    --text: #f3f4f6;
    --muted: #cbd5e1;
    --subtle: #94a3b8;
    --green: #0f9d58;
    --green-2: #16a34a;
    --red: #ef4444;
    --yellow: #f59e0b;
}

/* global */
.stApp {
    background-color: var(--bg);
    color: var(--text);
}

html, body, p, div, span, label, li, h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}

/* main width */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* top hero */
.hero-wrap {
    background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 24px 24px 16px 24px;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1rem;
    color: var(--muted);
    margin-bottom: 0;
}

/* section */
.section-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #e5e7eb;
    margin-top: 1.25rem;
    margin-bottom: 0.75rem;
}

.section-note {
    color: var(--subtle);
    margin-bottom: 0.75rem;
}

/* cards */
.card {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.18);
}

.kpi-row {
    margin-bottom: 0.25rem;
}

/* metric */
[data-testid="stMetric"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    min-height: 120px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 800 !important;
}

[data-testid="stMetricDelta"] {
    color: var(--green-2) !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
}

/* sidebar select/radio */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span {
    color: #e5e7eb !important;
}

/* file uploader */
[data-testid="stFileUploader"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 10px;
}

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] div {
    color: #e5e7eb !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: #111827 !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

[data-testid="stFileUploaderDropzone"] * {
    color: #e5e7eb !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: #1f2937 !important;
    color: #f8fafc !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

/* selectbox */
label[data-testid="stWidgetLabel"] {
    color: #e5e7eb !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] * {
    color: #f8fafc !important;
}

div[data-baseweb="popover"] {
    background-color: #111827 !important;
}

ul[role="listbox"] {
    background-color: #111827 !important;
    border: 1px solid var(--border) !important;
}

ul[role="listbox"] li {
    color: #f8fafc !important;
}

/* expander */
details {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}

summary {
    color: #f8fafc !important;
    font-weight: 700 !important;
    padding: 10px 12px !important;
}

details > div {
    background: #111827 !important;
    color: #e5e7eb !important;
}

/* dataframe */
[data-testid="stDataFrame"] {
    background-color: #111827 !important;
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stDataFrame"] * {
    color: #e5e7eb !important;
}

[data-testid="stTable"] * {
    color: #e5e7eb !important;
}

/* tabs */
button[data-baseweb="tab"] {
    color: #cbd5e1 !important;
    background: transparent !important;
}

button[aria-selected="true"][data-baseweb="tab"] {
    color: #f8fafc !important;
    border-bottom: 2px solid var(--green) !important;
}

/* alerts */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* buttons */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(180deg, #166534 0%, #14532d 100%) !important;
    color: #f8fafc !important;
    border: 1px solid #1f7a44 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

/* caption */
[data-testid="stCaptionContainer"] {
    color: var(--subtle) !important;
}

/* horizontal rule */
hr {
    border-color: var(--border) !important;
}
/* =========================
   FIX Selectbox dropdown
   ========================= */

div[data-baseweb="popover"] {
    background: #111827 !important;
}

ul[role="listbox"] {
    background: #111827 !important;
    border: 1px solid #253046 !important;
}

ul[role="listbox"] li {
    background: #111827 !important;
    color: #f8fafc !important;
}

ul[role="listbox"] li:hover {
    background: #1f2937 !important;
}


/* =========================
   FIX Selectbox selected value
   ========================= */

div[data-baseweb="select"] input {
    color: #f8fafc !important;
}

div[data-baseweb="select"] div {
    color: #f8fafc !important;
}


/* =========================
   FIX Expander Header
   ========================= */

summary {
    background: #111827 !important;
    color: #f8fafc !important;
}

summary:hover {
    background: #1f2937 !important;
}

summary span {
    color: #f8fafc !important;
}


/* =========================
   FIX Expander arrow
   ========================= */

summary svg {
    fill: #e5e7eb !important;
}
/* Hide deploy button & menu only */

[data-testid="stToolbar"] {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

/* 保留 header 空間 */
header[data-testid="stHeader"] {
    background: transparent;
}
/* force show file uploader */

[data-testid="stFileUploader"] {
    display: block !important;
    visibility: visible !important;
}

[data-testid="stFileUploaderDropzone"] {
    display: flex !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    display: block !important;
}
/* Selectbox dropdown final fix */

div[data-baseweb="popover"] {
    background: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid #253046 !important;
}

div[data-baseweb="popover"] * {
    color: #f8fafc !important;
}

ul[role="listbox"] {
    background: #111827 !important;
    border: 1px solid #253046 !important;
    border-radius: 10px !important;
}

li[role="option"] {
    background: #111827 !important;
    color: #f8fafc !important;
}

li[role="option"]:hover {
    background: #1f2937 !important;
    color: #ffffff !important;
}

li[role="option"][aria-selected="true"] {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* selected box itself */
div[data-baseweb="select"] > div {
    background: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid #253046 !important;
}

div[data-baseweb="select"] input {
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
}

div[data-baseweb="select"] span {
    color: #f8fafc !important;
}
</style>
""",
    unsafe_allow_html=True,
)

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

    raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    lines = raw.splitlines()

    if lines and all(line.startswith('"') and line.endswith('"') for line in lines[: min(5, len(lines))]):
        cleaned = "\n".join(line[1:-1] for line in lines)
        df = pd.read_csv(io.StringIO(cleaned))
    else:
        df = pd.read_csv(io.StringIO(raw))

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def detect_invalid_numeric(df: pd.DataFrame, numeric_columns: list[str]) -> tuple[pd.DataFrame, int]:
    converted = df.copy()
    invalid_count = 0

    for col in numeric_columns:
        if col in converted.columns:
            coerced = pd.to_numeric(converted[col], errors="coerce")
            invalid_count += int(((converted[col].notna()) & (coerced.isna())).sum())
            converted[col] = coerced

    return converted, invalid_count


def detect_date_errors(df: pd.DataFrame, date_col: str) -> tuple[pd.Series, int]:
    if date_col not in df.columns:
        empty = pd.Series([pd.NaT] * len(df), index=df.index)
        return empty, 0

    parsed = pd.to_datetime(df[date_col], errors="coerce")
    errors = int(((df[date_col].notna()) & (parsed.isna())).sum())
    return parsed, errors


def detect_outliers(df: pd.DataFrame, numeric_columns: list[str]) -> int:
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
        count += int(mask.sum())

    return count


def quality_assessment(df: pd.DataFrame) -> tuple[pd.DataFrame, QualityMetrics]:
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
        missing_cells=missing_cells,
        duplicate_rows=duplicate_rows,
        outlier_cells=outlier_count,
        invalid_numeric_cells=invalid_numeric_count,
        date_format_errors=date_errors,
        quality_score=quality_score,
    )
    return working_df, metrics


def consistency_checks(df: pd.DataFrame) -> dict[str, dict]:
    checks = {}

    if "inventory" in df.columns:
        rows = df[df["inventory"] < 0]
        checks["Negative inventory"] = {
            "status": "Executed",
            "rows": rows,
        }
    else:
        checks["Negative inventory"] = {
            "status": "Not applicable",
            "rows": pd.DataFrame(),
        }

    if {"sales", "inventory", "price"}.issubset(df.columns):
        unreasonable_sales = (df["sales"] > (df["inventory"].clip(lower=0) * 2)) | (df["sales"] > 5000)
        rows = df[unreasonable_sales.fillna(False)]
        checks["Unreasonable sales volume"] = {
            "status": "Executed",
            "rows": rows,
        }
    else:
        checks["Unreasonable sales volume"] = {
            "status": "Not applicable",
            "rows": pd.DataFrame(),
        }

    if {"price", "cost"}.issubset(df.columns):
        rows = df[df["price"] < df["cost"]]
        checks["Price lower than cost"] = {
            "status": "Executed",
            "rows": rows,
        }
    else:
        checks["Price lower than cost"] = {
            "status": "Not applicable",
            "rows": pd.DataFrame(),
        }

    if {"parsed_date", "lead_time"}.issubset(df.columns):
        implied_delivery = df["parsed_date"] + pd.to_timedelta(df["lead_time"].fillna(0), unit="D")
        rows = df[df["parsed_date"].isna() | (df["lead_time"] < 0) | implied_delivery.isna()]
        checks["Date order errors"] = {
            "status": "Executed",
            "rows": rows,
        }
    else:
        checks["Date order errors"] = {
            "status": "Not applicable",
            "rows": pd.DataFrame(),
        }

    return checks


def workflow_mode(metrics: QualityMetrics, consistency_issues: dict[str, dict], total_rows: int) -> str:
    issue_rows = sum(len(v["rows"]) for v in consistency_issues.values())
    if metrics.quality_score < 75 or issue_rows > max(3, int(0.30 * max(total_rows, 1))):
        return "Risk Review"
    if metrics.quality_score < 88 or metrics.outlier_cells > 5:
        return "Priority Decision"
    return "Standard Analysis"


def build_recommendations(metrics: QualityMetrics, consistency_issues: dict[str, dict]) -> pd.DataFrame:
    items = [
        {
            "Area": "Data Cleaning",
            "Data Quality Impact": metrics.missing_cells + metrics.invalid_numeric_cells + metrics.date_format_errors,
            "Risk Level": metrics.duplicate_rows + metrics.date_format_errors,
            "Anomaly Frequency": metrics.outlier_cells,
        },
        {
            "Area": "Inventory & Sales Validation",
            "Data Quality Impact": len(consistency_issues["Negative inventory"]["rows"]),
            "Risk Level": len(consistency_issues["Unreasonable sales volume"]["rows"])
            + len(consistency_issues["Price lower than cost"]["rows"]),
            "Anomaly Frequency": len(consistency_issues["Unreasonable sales volume"]["rows"]),
        },
        {
            "Area": "Manual Business Review",
            "Data Quality Impact": len(consistency_issues["Date order errors"]["rows"]),
            "Risk Level": len(consistency_issues["Date order errors"]["rows"]),
            "Anomaly Frequency": metrics.outlier_cells // 2,
        },
    ]
    rec_df = pd.DataFrame(items)
    rec_df["Priority Score"] = (
        0.45 * rec_df["Data Quality Impact"]
        + 0.35 * rec_df["Risk Level"]
        + 0.20 * rec_df["Anomaly Frequency"]
    )
    return rec_df.sort_values("Priority Score", ascending=False).reset_index(drop=True)


def build_ai_summary(df: pd.DataFrame, metrics: QualityMetrics, consistency: dict[str, dict], mode: str) -> str:
    issue_counts = {k: len(v["rows"]) for k, v in consistency.items()}
    highest_issue_name = max(issue_counts, key=issue_counts.get)
    highest_issue_count = issue_counts[highest_issue_name]

    summary_lines = [
        f"Current workflow mode is {mode}.",
        f"Data quality score is {metrics.quality_score}/100 with {metrics.missing_cells} missing cells and {metrics.invalid_numeric_cells} invalid numeric values.",
    ]

    if highest_issue_count > 0:
        summary_lines.append(
            f"The highest business-rule risk is {highest_issue_name.lower()} with {highest_issue_count} flagged rows."
        )
    else:
        summary_lines.append("No major business-rule breaches were detected in the current dataset.")

    if "sales" in df.columns:
        total_sales = pd.to_numeric(df["sales"], errors="coerce").fillna(0).sum()
        summary_lines.append(f"Total observed sales volume is {total_sales:,.0f}.")

    summary_lines.append("Recommended first action: resolve validation failures first, then review high-risk rule breaches before downstream reporting.")
    return " ".join(summary_lines)


def build_risk_issue_export(consistency: dict[str, dict]) -> pd.DataFrame:
    frames = []
    for name, payload in consistency.items():
        rows = payload["rows"]
        if not rows.empty:
            temp = rows.copy()
            temp.insert(0, "issue_type", name)
            frames.append(temp)

    if frames:
        return pd.concat(frames, ignore_index=True)

    return pd.DataFrame({"issue_type": [], "message": []})


def main() -> None:
    st.sidebar.markdown("## Yusen AI")
    st.sidebar.caption("Decision Intelligence")
    st.sidebar.markdown("---")

    uploaded_file = st.file_uploader(
    "Upload CSV dataset",
    type=["csv"]
    )

    st.sidebar.markdown("### View Mode")

    view_mode = st.sidebar.radio(
        "Select section",
        [
            "Overview",
            "Validation",
            "Consistency",
            "Analytics",
            "Decision Support",
            "AI Summary"
        ],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Enterprise AI4BI Demo")

    df = load_data(uploaded_file)
    working_df, metrics = quality_assessment(df)
    consistency = consistency_checks(working_df)
    rec_df = build_recommendations(metrics, consistency)
    mode = workflow_mode(metrics, consistency, len(working_df))
    ai_summary = build_ai_summary(working_df, metrics, consistency, mode)
    risk_export_df = build_risk_issue_export(consistency)

    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-title">Yusen AI Decision Intelligence Console</div>
            <div class="hero-subtitle">Enterprise AI4BI Dashboard Demo</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_c1, top_c2, top_c3, top_c4 = st.columns(4)
    top_c1.metric("Rows", f"{df.shape[0]:,}")
    top_c2.metric("Columns", f"{df.shape[1]:,}")
    top_c3.metric("Quality Score", f"{metrics.quality_score}")
    total_alerts = sum(len(v["rows"]) for v in consistency.values())
    top_c4.metric("Risk Alerts", f"{total_alerts:,}")

    tabs = st.tabs(["Overview", "Validation", "Consistency", "Analytics", "Decision Support", "AI Summary"])

    with tabs[0]:
        st.markdown('<div class="section-title">1) Data Upload Summary</div>', unsafe_allow_html=True)
        st.caption("Current dataset health and structural profile")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing", int(df.isna().sum().sum()))
        c4.metric("Duplicates", int(df.duplicated().sum()))

        with st.expander("Column Types", expanded=False):
            st.dataframe(
                pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str)}),
                use_container_width=True,
            )

        with st.expander("Preview Data", expanded=False):
            st.dataframe(df.head(30), use_container_width=True)

    with tabs[1]:
        st.markdown('<div class="section-title">2) Data Validation</div>', unsafe_allow_html=True)
        st.caption("Validation signals for reliability before downstream decisions")

        q1, q2, q3 = st.columns(3)
        q1.metric("Quality Score", metrics.quality_score)
        q2.metric("Invalid Numbers", metrics.invalid_numeric_cells)
        q3.metric("Date Errors", metrics.date_format_errors)

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
        st.download_button(
            "Download validation_summary.csv",
            validation_table.to_csv(index=False).encode("utf-8"),
            file_name="validation_summary.csv",
            mime="text/csv",
        )

    with tabs[2]:
        st.markdown('<div class="section-title">3) Consistency Check</div>', unsafe_allow_html=True)
        st.caption("Business rule checks and exception review")

        for check_name, payload in consistency.items():
            bad_rows = payload["rows"]
            status = payload["status"]
            status_text = (
                f"{check_name}: {len(bad_rows)} problematic rows"
                if status == "Executed"
                else f"{check_name}: not applicable"
            )
            with st.expander(status_text, expanded=False):
                if status != "Executed":
                    st.warning("Missing required columns. Rule not executed.")
                elif bad_rows.empty:
                    st.success("Rule executed with zero issues.")
                else:
                    st.dataframe(bad_rows, use_container_width=True)

        st.download_button(
            "Download risk_issues.csv",
            risk_export_df.to_csv(index=False).encode("utf-8"),
            file_name="risk_issues.csv",
            mime="text/csv",
        )

    with tabs[3]:
        st.markdown('<div class="section-title">4) Analytics Dashboard</div>', unsafe_allow_html=True)
        st.caption("Distribution, trend, and category-level aggregation")

        numeric_options = [
            c for c in NUMERIC_COLUMNS
            if c in working_df.columns and pd.api.types.is_numeric_dtype(working_df[c])
        ]

        if numeric_options:
            selected_metric = st.selectbox("Distribution Metric", options=numeric_options)

            col_a, col_b = st.columns(2)
            with col_a:
                safe_df = working_df.dropna(subset=[selected_metric])
                fig_dist = px.histogram(
                    safe_df,
                    x=selected_metric,
                    nbins=20,
                    title=f"Distribution of {selected_metric}",
                    template="plotly_dark",
                )
                fig_dist.update_layout(
                    paper_bgcolor="#111827",
                    plot_bgcolor="#111827",
                    font_color="#f3f4f6",
                )
                st.plotly_chart(fig_dist, use_container_width=True)

            with col_b:
                if {"parsed_date", "sales"}.issubset(working_df.columns):
                    trend_df = (
                        working_df.dropna(subset=["parsed_date", "sales"])
                        .groupby("parsed_date", as_index=False)["sales"]
                        .sum()
                        .sort_values("parsed_date")
                    )
                    fig_trend = px.line(
                        trend_df,
                        x="parsed_date",
                        y="sales",
                        title="Sales Trend Over Time",
                        template="plotly_dark",
                    )
                    fig_trend.update_layout(
                        paper_bgcolor="#111827",
                        plot_bgcolor="#111827",
                        font_color="#f3f4f6",
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.warning("No numeric columns available for analytics.")

        if CATEGORY_COLUMN in working_df.columns and "sales" in working_df.columns:
            agg_df = (
                working_df.groupby(CATEGORY_COLUMN, as_index=False)["sales"]
                .sum()
                .sort_values("sales", ascending=False)
            )
            fig_cat = px.bar(
                agg_df,
                x=CATEGORY_COLUMN,
                y="sales",
                title="Category Sales Aggregation",
                template="plotly_dark",
            )
            fig_cat.update_layout(
                paper_bgcolor="#111827",
                plot_bgcolor="#111827",
                font_color="#f3f4f6",
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    with tabs[4]:
        st.markdown('<div class="section-title">5) Decision Support</div>', unsafe_allow_html=True)
        st.caption("Priority ranking for remediation and review")

        st.dataframe(rec_df, use_container_width=True)

        if not rec_df.empty:
            top_area = rec_df.iloc[0]["Area"]
            st.success(
                f"Top recommendation: prioritize {top_area}. Start with validation failures, then review business-rule exceptions and unresolved date issues."
            )

        st.download_button(
            "Download recommendations.csv",
            rec_df.to_csv(index=False).encode("utf-8"),
            file_name="recommendations.csv",
            mime="text/csv",
        )

        st.markdown('<div class="section-title">6) Workflow Router</div>', unsafe_allow_html=True)
        st.info(f"Current Mode: {mode}")

    with tabs[5]:
        st.markdown('<div class="section-title">AI Summary</div>', unsafe_allow_html=True)
        st.caption("Business-facing summary generated from current validation and risk signals")
        st.markdown(f'<div class="card">{ai_summary}</div>', unsafe_allow_html=True)

    if view_mode != "Overview":
        st.caption(f"Sidebar view selection: {view_mode}")


if __name__ == "__main__":
    main() 