from __future__ import annotations

import streamlit as st

from analytics import (
    compute_kpis,
    generate_ai_insights,
    load_data,
    prepare_data,
    profit_trend,
    revenue_by_category,
    risk_table,
)
from decision_engine import generate_decision_suggestions
from ui_components import (
    render_ai_insight_panel,
    render_analytics_charts,
    render_decision_suggestions,
    render_kpi_panel,
    render_risk_heatmap,
)

st.set_page_config(page_title="AI4BI – Decision Intelligence Demo", layout="wide")


def main() -> None:
    st.title("AI4BI – Decision Intelligence Demo")
    st.caption("A portfolio-ready AI Decision Intelligence dashboard built with Streamlit + Plotly")

    raw_df = load_data("sample_data.csv")
    df = prepare_data(raw_df)

    st.subheader("KPI Overview")
    kpis = compute_kpis(df)
    render_kpi_panel(kpis)

    st.subheader("Analytics")
    revenue_df = revenue_by_category(df)
    trend_df = profit_trend(df)
    render_analytics_charts(revenue_df, trend_df)

    st.subheader("Risk Analysis")
    st.caption("Risk Score = Cost / Revenue")
    risk_df = risk_table(df)
    render_risk_heatmap(risk_df)

    insights = generate_ai_insights(df)
    suggestions = generate_decision_suggestions(df)

    with st.sidebar:
        st.header("AI Business Insight")
        for label, value in insights.items():
            st.markdown(f"- **{label}:** {value}")

    col1, col2 = st.columns(2)
    with col1:
        render_ai_insight_panel(insights)
    with col2:
        render_decision_suggestions(suggestions)


if __name__ == "__main__":
    main()
