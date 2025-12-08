# Quick Start Guide

Get the AI Financial Assistant up and running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL installed and running
- [ ] OpenAI API key

## Step 1: Backend Setup (2 minutes)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL and OpenAI API key
uvicorn main:app --reload
```

✅ Backend running at http://localhost:8000

## Step 2: Frontend Setup (2 minutes)

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with API_BASE_URL=http://localhost:8000
npm run dev
```

✅ Frontend running at http://localhost:3000

## Step 3: Test the Demo (1 minute)

```bash
cd demo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
streamlit run app.py
```

✅ Demo running at http://localhost:8501

## First Steps

1. **Register a user** at http://localhost:3000
2. **Create a financial goal** (e.g., "Save $50,000 for a house in 3 years")
3. **Chat with the assistant** about your finances
4. **View recommendations** based on your profile
5. **Check alerts** for financial insights

## Example API Calls

### Register
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "password123",
    "age": 30,
    "income": 50000,
    "risk_tolerance": "moderate"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Create Goal (with token from login)
```bash
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "House Down Payment",
    "description": "Save for house down payment",
    "goal_type": "house",
    "target_amount": 50000,
    "target_date": "2026-12-31T00:00:00",
    "monthly_contribution": 1500
  }'
```

## Troubleshooting

**Backend won't start?**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in .env
- Check port 8000 is not in use

**Frontend won't connect?**
- Ensure backend is running
- Check API_BASE_URL in .env.local
- Clear browser cache

**Demo not working?**
- Verify OpenAI API key is valid
- Check internet connection
- Review API rate limits

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Explore API docs at http://localhost:8000/docs

Happy coding! 🚀

