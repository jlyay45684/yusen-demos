from __future__ import annotations

import pandas as pd


def generate_decision_suggestions(df: pd.DataFrame) -> list[str]:
    suggestions: list[str] = []

    cost_by_category = (
        df.groupby("category", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
    )
    if not cost_by_category.empty:
        category = cost_by_category.iloc[0]["category"]
        suggestions.append(f"Reduce cost in category {category} by optimizing supplier mix and discounts.")

    profit_by_category = (
        df.groupby("category", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
    )
    if not profit_by_category.empty:
        category = profit_by_category.iloc[0]["category"]
        suggestions.append(f"Increase investment in category {category} to accelerate profitable growth.")

    high_risk_rows = df[df["risk_level"] == "High Risk"]
    if not high_risk_rows.empty:
        high_risk_categories = ", ".join(sorted(high_risk_rows["category"].dropna().unique()))
        suggestions.append(f"Monitor high-risk segments in: {high_risk_categories}.")
    else:
        suggestions.append("Risk profile is stable; continue weekly monitoring for early anomaly detection.")

    return suggestions
