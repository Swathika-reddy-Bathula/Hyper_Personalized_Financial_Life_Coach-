# AI-Driven Financial Assistant

An AI-driven financial assistant that acts as a personalized financial coach, leveraging Generative AI (GenAI) and Large Language Models (LLMs) to provide:

- Goal-based investment planning
- Real-time budgeting insights
- Personalized product recommendations
- Predictive financial alerts
- Explainable AI (XAI) reasoning for every suggestion

## Project Structure

```
.
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── demo/            # Streamlit demo interface
├── database/        # Database migrations and schemas
└── docs/           # Documentation
```

## Features

### 1. Goal Understanding & Planning
Extracts and plans for financial goals from natural language input.

### 2. Behavior Analysis
Analyzes spending patterns to suggest savings opportunities.

### 3. Personalized Product Matching
Recommends suitable financial products based on user profile.

### 4. Predictive Alerts
Warns of risks like missed SIPs or low balances.

### 5. Explainability Layer
Justifies recommendations to build trust.

## Technical Stack

- **AI Models**: GPT-4, Llama-3, LangChain, LlamaIndex
- **Frontend**: React/Next.js, Tailwind CSS
- **Backend**: Python, FastAPI
- **Cloud**: AWS (EC2, Lambda, S3)
- **Database**: PostgreSQL
- **Vector DB**: Pinecone/FAISS

## Setup Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Demo Setup
```bash
cd demo
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables

Create `.env` files in each directory with appropriate API keys:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `DATABASE_URL`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

