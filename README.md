# AI-Powered Hyper-Personalized Financial Life Coach

This repository contains a working Streamlit prototype that brings the presentation’s idea to life. The demo emulates a GenAI-powered financial coach that understands goals, analyses behaviour, recommends banking products, and surfaces explainable insights in real time.

## Features
- Multi-goal SIP planner with explainable reasoning by risk profile.
- Behaviour signals from editable spend buckets or uploaded transaction CSVs.
- Cash-flow stress test producing predictive alerts (EMI/SIP miss risk, runway).
- Product intelligence layer with curated mutual funds, credit cards, and safety nets.
- Downloadable plan snapshot to share with stakeholders.

## Getting Started
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

When Streamlit opens in the browser:
1. Tune the client snapshot (income, cash, EMIs, risk appetite) from the sidebar.
2. Edit or add financial goals to auto-generate SIP requirements and explanations.
3. Adjust the spend table or upload a CSV (columns: `date,category,amount,type`) for deeper nudges.
4. Review predictive alerts, explainable recommendations, and download the plan if needed.

## Data Inputs
- `data/products.json` – curated mutual funds, cards, and savings products with metadata used by the recommendation engine.
- `data/sample_transactions.csv` – sample behaviour data for quick demos (toggle in sidebar).

## Notes
- The prototype is deterministic – no external API keys required – making it safe to demo offline.
- Extend the logic in `financial_engine.py` to plug in live bank data, GenAI prompt chains, or RAG layers as needed.

