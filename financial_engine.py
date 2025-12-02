"""
Core analysis and recommendation utilities for the
AI-Powered Hyper-Personalized Financial Life Coach demo.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import json
import math
import os

import pandas as pd

# Optional .env support so you can keep keys outside the shell
try:  # pragma: no cover - soft dependency
    from dotenv import load_dotenv, find_dotenv  # type: ignore[import]

    # Load variables from a local .env file if present (does nothing if file missing)
    load_dotenv(find_dotenv(), override=False)
except Exception:  # pragma: no cover
    pass

try:  # optional: only needed when you actually enable LLM explanations
    import openai  # type: ignore[import]
except ImportError:  # pragma: no cover - soft dependency
    openai = None

try:  # optional: only needed when you point to a live DB
    from sqlalchemy import create_engine  # type: ignore[import]
except ImportError:  # pragma: no cover
    create_engine = None

try:  # optional: only needed for HTTP-based RAG / product APIs
    import requests  # type: ignore[import]
except ImportError:  # pragma: no cover
    requests = None


CATALOG_PATH = Path("data") / "products.json"
TRANSACTION_SAMPLE_PATH = Path("data") / "sample_transactions.csv"


@dataclass
class GoalPlan:
    name: str
    target_amount: float
    years: float
    priority: str
    monthly_investment: float
    projected_value: float
    explanation: str


def _use_llm_explanations() -> bool:
    """
    Toggle for LLM-based explainability.

    Controlled via env var:
    - USE_LLM_EXPLAIN=1 enables OpenAI calls (if openai is installed and key is set)
    """
    return os.getenv("USE_LLM_EXPLAIN", "0") == "1"


def explain_plan_with_llm(plan: GoalPlan, profile: Dict[str, Any]) -> Optional[str]:
    """
    Optional OpenAI-backed explanation generator.

    - Requires `openai` Python package and OPENAI_API_KEY env var.
    - If anything is missing or errors, returns None so caller can fall back
      to the deterministic rule-based explanation.
    """
    if openai is None:
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        # New-style OpenAI client (>=1.0)
        from openai import OpenAI  # type: ignore[import]

        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a transparent financial coach. "
            "Explain in 2–3 short, simple sentences why this SIP plan is suitable, "
            "without giving tax advice.\n\n"
            f"User profile: {profile}\n"
            f"Goal: {plan.name}\n"
            f"Target amount (INR): {plan.target_amount}\n"
            f"Horizon (years): {plan.years}\n"
            f"Monthly SIP (INR): {plan.monthly_investment:.0f}\n"
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()  # type: ignore[union-attr]
    except Exception:
        # Never break the app because of LLM issues
        return None


def load_product_catalog(path: Path = CATALOG_PATH) -> Dict[str, List[Dict[str, Any]]]:
    """
    Product intelligence layer.

    Priority order (no UI changes required):
    1. If PRODUCT_DB_URL is set and SQLAlchemy is available → load from DB.
       Expected tables/columns (example):
         - mutual_funds(name, risk_score, expected_return, ideal_horizon_years, goal_alignment, why)
         - credit_cards(name, best_for, min_income, annual_fee, why)
         - savings(name, interest_rate, min_amount, lock_in, why)
    2. If PRODUCT_RAG_ENDPOINT is set and `requests` is available → call HTTP API
       that returns the same JSON shape as data/products.json.
    3. Fallback → read static JSON file in data/products.json.
    """
    # 1) DB-backed catalog
    db_url = os.getenv("PRODUCT_DB_URL")
    if db_url and create_engine is not None:
        engine = create_engine(db_url)
        with engine.begin() as conn:
            catalog: Dict[str, List[Dict[str, Any]]] = {}
            for table in ("mutual_funds", "credit_cards", "savings"):
                try:
                    df = pd.read_sql_table(table, conn)
                    catalog[table] = df.to_dict("records")
                except Exception:
                    # If any table is missing, silently fall back to file for that section
                    catalog[table] = []
        # If we managed to load at least one section from DB, use it
        if any(catalog.values()):
            return catalog

    # 2) HTTP / RAG-backed catalog
    rag_endpoint = os.getenv("PRODUCT_RAG_ENDPOINT")
    if rag_endpoint and requests is not None:
        try:
            resp = requests.get(rag_endpoint, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data  # must match the original catalog structure
        except Exception:
            # Non-fatal – fall back to file
            pass

    # 3) Static JSON fallback
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Product catalog not found at {path}. Please add data/products.json or configure PRODUCT_DB_URL."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def load_sample_transactions(path: Path = TRANSACTION_SAMPLE_PATH) -> pd.DataFrame:
    """
    Transaction feed.

    Priority order:
    1. If BANK_DB_URL is set and SQLAlchemy is available → query a `transactions` table.
       Required columns: date, category, amount, type (credit/debit).
    2. Fallback → sample CSV in data/sample_transactions.csv.
    """
    db_url = os.getenv("BANK_DB_URL")
    if db_url and create_engine is not None:
        engine = create_engine(db_url)
        try:
            df = pd.read_sql_table("transactions", engine)
            # Normalise column names to expected schema
            required_cols = {"date", "category", "amount", "type"}
            if not required_cols.issubset({c.lower() for c in df.columns}):
                raise ValueError("transactions table must contain date, category, amount, type columns")
            # Basic normalisation
            df.columns = [c.lower() for c in df.columns]
            df["date"] = pd.to_datetime(df["date"])
            return df[["date", "category", "amount", "type"]]
        except Exception:
            # Fall through to CSV
            pass

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Sample transactions not found at {path}. Please add data/sample_transactions.csv or configure BANK_DB_URL."
        )
    return pd.read_csv(path, parse_dates=["date"])


def _annual_return_from_risk(risk_score: int) -> float:
    mapping = {
        1: 0.065,
        2: 0.08,
        3: 0.105,
        4: 0.12,
        5: 0.145,
    }
    return mapping.get(int(risk_score), 0.1)


def _sip_required(
    target_amount: float,
    years: float,
    annual_return: float,
) -> Tuple[float, float]:
    months = max(int(years * 12), 1)
    monthly_rate = max(annual_return / 12, 1e-4)
    growth_factor = (1 + monthly_rate) ** months
    # SIP future value formula rearranged to compute contribution
    monthly_investment = target_amount * monthly_rate / (growth_factor - 1)
    projected_value = monthly_investment * (growth_factor - 1) / monthly_rate
    return monthly_investment, projected_value


def build_goal_plans(
    goals: Iterable[Dict[str, Any]],
    risk_score: int,
) -> List[GoalPlan]:
    plans: List[GoalPlan] = []
    risk_rate = _annual_return_from_risk(risk_score)

    for goal in goals:
        try:
            target_amount = float(goal.get("target_amount", 0))
            years = float(goal.get("years", 1))
        except (TypeError, ValueError):
            continue

        priority = goal.get("priority", "medium").lower()
        monthly_investment, projected_value = _sip_required(
            target_amount=target_amount,
            years=years,
            annual_return=risk_rate,
        )
        # Baseline deterministic explanation (always available)
        base_explanation = (
            f"Uses a {risk_rate:.1%} annual return aligned to risk profile "
            f"to fund ₹{target_amount:,.0f} in {years:.1f} years. "
            f"Requires SIP of ₹{monthly_investment:,.0f}/month."
        )

        explanation = base_explanation
        if _use_llm_explanations():
            # Soft-dependency: best-effort call to LLM for a more natural narrative
            profile_snapshot = {"risk_score": risk_score}
            llm_text = explain_plan_with_llm(
                GoalPlan(
                    name=str(goal.get("goal", "Goal")),
                    target_amount=target_amount,
                    years=years,
                    priority=priority,
                    monthly_investment=monthly_investment,
                    projected_value=projected_value,
                    explanation=base_explanation,
                ),
                profile_snapshot,
            )
            if llm_text:
                explanation = f"{base_explanation} AI coach explanation: {llm_text}"
        plans.append(
            GoalPlan(
                name=str(goal.get("goal", "Goal")),
                target_amount=target_amount,
                years=years,
                priority=priority,
                monthly_investment=monthly_investment,
                projected_value=projected_value,
                explanation=explanation,
            )
        )
    return plans


def summarize_cash_flow(
    monthly_income: float,
    monthly_expense: float,
    existing_sips: float,
    emi: float,
    recommended_sip: float,
    cash_reserve: float,
) -> Dict[str, Any]:
    surplus = monthly_income - (monthly_expense + existing_sips + recommended_sip + emi)
    burn = monthly_expense + emi
    runway_months = cash_reserve / burn if burn else math.inf
    savings_rate = max((monthly_income - monthly_expense) / monthly_income, 0) if monthly_income else 0

    return {
        "surplus": surplus,
        "runway_months": runway_months,
        "savings_rate": savings_rate,
        "recommended_sip": recommended_sip,
    }


def behavior_insights(
    spend_df: pd.DataFrame,
    monthly_income: float,
    txn_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    spend_df = spend_df.copy()
    spend_df["share"] = spend_df["amount"] / spend_df["amount"].sum()
    top_category = spend_df.sort_values("share", ascending=False).head(1)
    top_category_name = top_category["category"].iloc[0] if not top_category.empty else "Spending"

    insights = []
    if monthly_income:
        essential = spend_df.loc[spend_df["type"] == "Essential", "amount"].sum()
        essentials_ratio = essential / monthly_income
        if essentials_ratio > 0.6:
            insights.append(
                "Essentials consume above 60% of income. Consider renegotiating EMI or recurring bills."
            )

    if not top_category.empty and top_category["share"].iloc[0] > 0.3:
        insights.append(
            f"{top_category_name} takes {top_category['share'].iloc[0]:.0%} of spends - cap it with an automated limit."
        )

    if txn_df is not None and not txn_df.empty:
        recurring = (
            txn_df[txn_df["category"].str.contains("EMI|SIP", case=False)]
            .groupby("category")["amount"]
            .sum()
        )
        if not recurring.empty:
            label = recurring.idxmax()
            insights.append(f"High recurring debit detected: {label}. Fund this via salary sweep.")

    if not insights:
        insights.append("Spending pattern looks balanced. Keep monthly reviews.")

    return {
        "top_category": top_category_name,
        "insights": insights,
        "spend_df": spend_df,
    }


def predictive_alerts(cash_summary: Dict[str, Any]) -> List[str]:
    alerts: List[str] = []
    surplus = cash_summary["surplus"]
    runway = cash_summary["runway_months"]

    if surplus < 0:
        alerts.append(
            "Projected monthly cash deficit could cause SIP or EMI misses. Increase income or cut variable spends."
        )
    elif surplus < 5000:
        alerts.append("Surplus under ₹5k; a single large bill can derail goals. Move discretionary spends to UPI alerts.")

    if runway < 3:
        alerts.append(
            f"Emergency reserve covers only {runway:.1f} months. Target 6x monthly burn for resilience."
        )
    if cash_summary["savings_rate"] < 0.2:
        alerts.append(
            "Savings rate below 20% of income. Automate transfers on salary day to raise investible surplus."
        )

    if not alerts:
        alerts.append("Cash runway and surplus look healthy for upcoming SIPs.")
    return alerts


def recommend_products(
    profile: Dict[str, Any],
    catalog: Dict[str, List[Dict[str, Any]]],
    top_categories: Iterable[str],
) -> Dict[str, List[Dict[str, Any]]]:
    recommendations: Dict[str, List[Dict[str, Any]]] = {}
    risk = profile.get("risk_score", 3)
    income = profile.get("monthly_income", 0)
    goal_types = {g.get("goal", "").lower() for g in profile.get("goals", [])}
    lifestyle_tags = set(cat.lower() for cat in top_categories)

    def score_mutual_fund(item: Dict[str, Any]) -> float:
        score = 0.0
        score -= abs(item.get("risk_score", 3) - risk) * 0.7
        horizon = profile.get("avg_goal_horizon", 5)
        score -= abs(item.get("ideal_horizon_years", 5) - horizon) * 0.2
        if any(tag in goal_types for tag in item.get("goal_alignment", [])):
            score += 1.0
        score += item.get("expected_return", 0)
        return score

    def score_card(item: Dict[str, Any]) -> float:
        score = 0.0
        if income >= item.get("min_income", 0):
            score += 2.0
        if lifestyle_tags.intersection(set(item.get("best_for", []))):
            score += 1.5
        score -= item.get("annual_fee", 0) / 10000
        return score

    def score_deposit(item: Dict[str, Any]) -> float:
        reserve = profile.get("cash_reserve", 0)
        if reserve >= item.get("min_amount", 0):
            return item.get("interest_rate", 0)
        return item.get("interest_rate", 0) - 2

    funds = sorted(catalog.get("mutual_funds", []), key=score_mutual_fund, reverse=True)[:3]
    cards = sorted(catalog.get("credit_cards", []), key=score_card, reverse=True)[:2]
    deposits = sorted(catalog.get("savings", []), key=score_deposit, reverse=True)[:2]

    def _augment(items: List[Dict[str, Any]], kind: str) -> List[Dict[str, Any]]:
        enriched = []
        for item in items:
            enriched.append(
                {
                    "name": item["name"],
                    "why": item.get("why", ""),
                    "meta": {
                        "kind": kind,
                        **{k: v for k, v in item.items() if k not in {"name", "why"}},
                    },
                }
            )
        return enriched

    recommendations["mutual_funds"] = _augment(funds, "mutual_fund")
    recommendations["credit_cards"] = _augment(cards, "credit_card")
    recommendations["savings"] = _augment(deposits, "savings")
    return recommendations


def format_currency(value: float) -> str:
    return f"₹{value:,.0f}"

