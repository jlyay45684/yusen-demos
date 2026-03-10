from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import KPIBundle


def render_kpi_panel(kpis: KPIBundle) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${kpis.total_revenue:,.0f}")
    c2.metric("Total Cost", f"${kpis.total_cost:,.0f}")
    c3.metric("Profit", f"${kpis.profit:,.0f}")
    c4.metric("Profit Margin", f"{kpis.profit_margin:.1%}")


def render_analytics_charts(revenue_df: pd.DataFrame, trend_df: pd.DataFrame) -> None:
    chart_left, chart_right = st.columns(2)

    with chart_left:
        fig_revenue = px.bar(
            revenue_df,
            x="category",
            y="revenue",
            title="Revenue by Category",
            color="category",
        )
        fig_revenue.update_layout(showlegend=False)
        st.plotly_chart(fig_revenue, use_container_width=True)

    with chart_right:
        fig_profit = px.line(
            trend_df,
            x="date",
            y="profit",
            title="Profit Trend",
            markers=True,
        )
        st.plotly_chart(fig_profit, use_container_width=True)


def render_risk_heatmap(risk_df: pd.DataFrame) -> None:
    def risk_style(row: pd.Series) -> list[str]:
        level = row.get("risk_level", "")
        color_map = {
            "Low Risk": "#d1f5d3",
            "Medium Risk": "#fff4c2",
            "High Risk": "#ffd6d6",
        }
        color = color_map.get(level, "")
        return [f"background-color: {color}"] * len(row)

    styled = risk_df.style.apply(risk_style, axis=1)
    st.dataframe(styled, use_container_width=True, height=360)


def render_ai_insight_panel(insights: dict[str, str]) -> None:
    st.subheader("AI Insight")
    for label, value in insights.items():
        st.markdown(f"- **{label}:** {value}")


def render_decision_suggestions(suggestions: list[str]) -> None:
    st.subheader("Decision Suggestions")
    for suggestion in suggestions:
        st.info(suggestion)
