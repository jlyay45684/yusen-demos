from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

RISK_LOW_THRESHOLD = 0.45
RISK_MEDIUM_THRESHOLD = 0.7


@dataclass
class KPIBundle:
    total_revenue: float
    total_cost: float
    profit: float
    profit_margin: float


def load_data(csv_path: str = "sample_data.csv") -> pd.DataFrame:
    """Load source data for the dashboard."""
    return pd.read_csv(csv_path)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich raw data for analytics and decisioning."""
    prepared = df.copy()

    for column in ["sales", "price", "cost", "lead_time"]:
        if column in prepared.columns:
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    if "date" in prepared.columns:
        prepared["date"] = pd.to_datetime(prepared["date"], errors="coerce")

    prepared["revenue"] = prepared["sales"].fillna(0) * prepared["price"].fillna(0)
    prepared["total_cost"] = prepared["sales"].fillna(0) * prepared["cost"].fillna(0)
    prepared["profit"] = prepared["revenue"] - prepared["total_cost"]

    safe_revenue = prepared["revenue"].replace(0, pd.NA)
    prepared["risk_score"] = (prepared["total_cost"] / safe_revenue).fillna(0)

    prepared["risk_level"] = prepared["risk_score"].apply(classify_risk_level)
    return prepared


def classify_risk_level(risk_score: float) -> str:
    if risk_score < RISK_LOW_THRESHOLD:
        return "Low Risk"
    if risk_score < RISK_MEDIUM_THRESHOLD:
        return "Medium Risk"
    return "High Risk"


def compute_kpis(df: pd.DataFrame) -> KPIBundle:
    total_revenue = float(df["revenue"].sum())
    total_cost = float(df["total_cost"].sum())
    profit = float(df["profit"].sum())
    profit_margin = (profit / total_revenue) if total_revenue else 0.0

    return KPIBundle(
        total_revenue=total_revenue,
        total_cost=total_cost,
        profit=profit,
        profit_margin=profit_margin,
    )


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    return grouped


def profit_trend(df: pd.DataFrame) -> pd.DataFrame:
    trend = (
        df.dropna(subset=["date"])
        .groupby("date", as_index=False)["profit"]
        .sum()
        .sort_values("date")
    )
    return trend


def generate_ai_insights(df: pd.DataFrame) -> dict[str, str]:
    category_performance = (
        df.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    top_category = category_performance.iloc[0]["category"] if not category_performance.empty else "N/A"

    cost_driver = (
        df.groupby("category", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
    )
    top_cost_driver = cost_driver.iloc[0]["category"] if not cost_driver.empty else "N/A"

    profitable_segment = (
        df.groupby("region", as_index=False)["profit"]
        .sum()
        .sort_values("profit", ascending=False)
    )
    top_segment = profitable_segment.iloc[0]["region"] if not profitable_segment.empty else "N/A"

    return {
        "Top performing category": top_category,
        "Highest cost driver": top_cost_driver,
        "Most profitable segment": top_segment,
    }


def risk_table(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "date",
        "product_id",
        "category",
        "region",
        "revenue",
        "total_cost",
        "profit",
        "risk_score",
        "risk_level",
    ]
    available_cols = [col for col in columns if col in df.columns]
    table = df[available_cols].copy()
    table["risk_score"] = table["risk_score"].round(2)
    return table
