from __future__ import annotations

import io
from typing import Dict, List

import pandas as pd
import streamlit as st

from financial_engine import (
    behavior_insights,
    build_goal_plans,
    format_currency,
    load_product_catalog,
    load_sample_transactions,
    predictive_alerts,
    recommend_products,
    summarize_cash_flow,
)

st.set_page_config(
    page_title="AI-Powered Financial Life Coach",
    page_icon="💹",
    layout="wide",
)

st.title("AI-Powered Hyper-Personalized Financial Coach")
st.caption(
    "Demo of a GenAI-first wealth coach that blends goal planning, "
    "behaviour analytics, product intelligence, and explainable guidance."
)


@st.cache_data
def get_catalog() -> Dict[str, List[Dict]]:
    return load_product_catalog()


@st.cache_data
def get_sample_transactions() -> pd.DataFrame:
    return load_sample_transactions()


catalog = get_catalog()
sample_transactions = get_sample_transactions()

with st.sidebar:
    st.header("Client Snapshot")
    monthly_income = st.number_input("Monthly Income (₹)", min_value=10000, value=120000, step=5000)
    monthly_expense = st.number_input(
        "Average Monthly Expenses (₹)", min_value=5000, value=65000, step=5000
    )
    cash_reserve = st.number_input("Emergency Corpus / Cash (₹)", min_value=0, value=250000, step=10000)
    existing_sips = st.number_input("Existing SIP Commitments (₹)", min_value=0, value=10000, step=1000)
    emi = st.number_input("Monthly EMIs (₹)", min_value=0, value=18000, step=1000)
    risk_score = st.slider("Risk Appetite", 1, 5, value=3, help="1 = Conservative, 5 = Aggressive")

    st.markdown("### Behaviour Data")
    txn_upload = st.file_uploader("Upload last-month transactions (CSV)", type="csv")
    use_sample = st.checkbox("Use bundled sample data", value=True)


default_goals = pd.DataFrame(
    [
        {"Goal": "Buy a ₹10 lakh car", "Target Amount (₹)": 1_000_000, "Years": 5, "Priority": "medium"},
        {"Goal": "Child education corpus", "Target Amount (₹)": 1_500_000, "Years": 8, "Priority": "high"},
        {"Goal": "Emergency fund top-up", "Target Amount (₹)": 400_000, "Years": 2, "Priority": "high"},
    ]
)

st.subheader("Goal Understanding & Planning")
st.markdown(
    "Adjust the goals below or add new goals to see SIP requirements and explainability for each outcome."
)
goal_editor = st.data_editor(
    default_goals,
    num_rows="dynamic",
    use_container_width=True,
    key="goals_editor",
)

default_spend = pd.DataFrame(
    [
        {"category": "Housing & EMI", "amount": 20000, "type": "Essential"},
        {"category": "Groceries", "amount": 14000, "type": "Essential"},
        {"category": "Transport", "amount": 4000, "type": "Essential"},
        {"category": "Lifestyle & Dining", "amount": 9000, "type": "Discretionary"},
        {"category": "Travel", "amount": 10000, "type": "Discretionary"},
        {"category": "Subscriptions", "amount": 2500, "type": "Discretionary"},
    ]
)

st.subheader("Spend Behaviour Signals")
st.markdown("Break down monthly spends for granular nudges and explainable budgeting.")
spend_editor = st.data_editor(
    default_spend,
    num_rows="dynamic",
    use_container_width=True,
    key="spend_editor",
)

if txn_upload is not None:
    try:
        transactions_df = pd.read_csv(txn_upload, parse_dates=["date"])
    except Exception:  # pragma: no cover - streamlit demo safeguard
        st.error("Unable to read the uploaded CSV. Reverting to defaults.")
        transactions_df = sample_transactions.copy()
else:
    transactions_df = sample_transactions.copy() if use_sample else pd.DataFrame()


def _prep_goals(df: pd.DataFrame) -> List[Dict]:
    cleaned = []
    for row in df.to_dict("records"):
        goal_name = str(row.get("Goal", "")).strip()
        if not goal_name:
            continue
        cleaned.append(
            {
                "goal": goal_name,
                "target_amount": float(row.get("Target Amount (₹)", 0) or 0),
                "years": float(row.get("Years", 1) or 1),
                "priority": (row.get("Priority") or "medium").lower(),
            }
        )
    return cleaned


goals = _prep_goals(goal_editor)
plans = build_goal_plans(goals, risk_score=risk_score)

plan_df = pd.DataFrame(
    [
        {
            "Goal": plan.name,
            "Target (₹)": format_currency(plan.target_amount),
            "Years": f"{plan.years:.1f}",
            "Monthly SIP (₹)": format_currency(plan.monthly_investment),
            "Projected Corpus (₹)": format_currency(plan.projected_value),
            "Explainability": plan.explanation,
        }
        for plan in plans
    ]
)

recommended_sip = sum(plan.monthly_investment for plan in plans)
cash_summary = summarize_cash_flow(
    monthly_income=monthly_income,
    monthly_expense=monthly_expense,
    existing_sips=existing_sips,
    emi=emi,
    recommended_sip=recommended_sip,
    cash_reserve=cash_reserve,
)

behaviour = behavior_insights(spend_editor, monthly_income=monthly_income, txn_df=transactions_df)
alerts = predictive_alerts(cash_summary)

avg_goal_horizon = (
    sum(plan.years for plan in plans) / len(plans) if plans else 5
)

top_spend_tags = spend_editor.sort_values("amount", ascending=False)["category"].head(3).tolist()
profile = {
    "risk_score": risk_score,
    "monthly_income": monthly_income,
    "cash_reserve": cash_reserve,
    "goals": goals,
    "avg_goal_horizon": avg_goal_horizon,
}
product_recs = recommend_products(profile, catalog, top_spend_tags)

st.divider()
st.subheader("Explainable Goal Plans")
if plan_df.empty:
    st.info("Add at least one goal to generate a tailored investment plan.")
else:
    st.dataframe(plan_df, use_container_width=True, hide_index=True)
    st.caption(f"Total suggested monthly SIP outlay: {format_currency(recommended_sip)}")

st.subheader("Cashflow & Predictive Health")
col1, col2, col3 = st.columns(3)
col1.metric("Net Monthly Surplus", format_currency(cash_summary["surplus"]))
col2.metric(
    "Emergency Runway",
    f"{cash_summary['runway_months']:.1f} months" if cash_summary["runway_months"] != float("inf") else "∞",
)
col3.metric("Savings Rate", f"{cash_summary['savings_rate']*100:.0f}%")

st.bar_chart(spend_editor.set_index("category")["amount"])

with st.expander("Behaviour Insights", expanded=True):
    for bullet in behaviour["insights"]:
        st.write(f"• {bullet}")

st.subheader("Predictive Alerts")
for alert in alerts:
    st.warning(alert)

st.subheader("Personalized Product Matches with Reasons")
product_cols = st.columns(3)
sections = ["mutual_funds", "credit_cards", "savings"]
labels = {
    "mutual_funds": "Investments",
    "credit_cards": "Credit Cards",
    "savings": "Cash & Safety Nets",
}
for idx, section in enumerate(sections):
    with product_cols[idx]:
        st.markdown(f"**{labels[section]}**")
        for item in product_recs.get(section, []):
            st.write(f"**{item['name']}**")
            st.write(item["why"])
            meta_lines = []
            for key, value in item["meta"].items():
                if key in {"kind", "why"}:
                    continue
                meta_lines.append(f"{key.replace('_', ' ').title()}: {value}")
            if meta_lines:
                st.caption(" | ".join(meta_lines))

st.subheader("Downloadable Plan Snapshot")
if not plan_df.empty:
    csv_buffer = io.StringIO()
    plan_df.to_csv(csv_buffer, index=False)
    st.download_button(
        "Download Goal Plan (CSV)",
        data=csv_buffer.getvalue(),
        file_name="financial_coach_goal_plan.csv",
        mime="text/csv",
    )

with st.expander("How this Demo Maps to the Assignment"):
    st.markdown(
        """
        - ✅ **Goal Understanding & Planning** – Dynamic SIP planner across multiple goals.
        - ✅ **Behaviour Analysis** – Spend editor + uploaded transactions drive nudges.
        - ✅ **Product Matching Engine** – Recommends funds, cards, and savings products with explainability.
        - ✅ **Predictive Alerts** – Cashflow stress testing for SIP/EMI misses.
        - ✅ **Explainability Layer** – Every table row and card surfaces the reasoning trail.
        """
    )

st.success("Prototype ready – launch with `streamlit run streamlit_app.py` to demo the AI coach live.")

