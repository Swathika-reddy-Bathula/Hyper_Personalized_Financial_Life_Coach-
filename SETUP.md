# Setup Instructions

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- OpenAI API Key
- (Optional) Pinecone API Key for vector search

## Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Set up PostgreSQL database:
```bash
createdb financial_assistant
# Update DATABASE_URL in .env
```

6. Run the backend:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Demo Setup (Streamlit)

1. Navigate to the demo directory:
```bash
cd demo
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

5. Run the Streamlit app:
```bash
streamlit run app.py
```

The demo will be available at `http://localhost:8501`

## Database Initialization

The database tables will be created automatically when you first run the backend. However, you may want to seed some initial data:

```python
# You can create a script to seed products, etc.
```

## Testing

### Backend API Testing
Use the interactive API docs at `http://localhost:8000/docs` or use curl/Postman.

Example:
```bash
# Register a user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

## Troubleshooting

### Backend Issues
- Ensure PostgreSQL is running
- Check that all environment variables are set correctly
- Verify database connection string format

### Frontend Issues
- Clear browser cache
- Check that backend is running on the correct port
- Verify API_BASE_URL in environment variables

### Demo Issues
- Ensure OpenAI API key is valid
- Check API rate limits
- Verify internet connection for API calls

## Production Deployment

### Backend
- Use a production ASGI server like Gunicorn with Uvicorn workers
- Set up proper database connection pooling
- Use environment variables for all secrets
- Enable HTTPS

### Frontend
- Build for production: `npm run build`
- Deploy to Vercel, Netlify, or similar
- Set up proper environment variables

### Database
- Use managed PostgreSQL service (AWS RDS, Heroku Postgres, etc.)
- Set up regular backups
- Configure connection pooling

## AWS Deployment (Optional)

1. **EC2**: Deploy backend to EC2 instance
2. **Lambda**: Use Lambda for serverless functions
3. **S3**: Store static assets and data
4. **RDS**: Use RDS for managed PostgreSQL

## Security Considerations

- Never commit `.env` files
- Use strong JWT secrets
- Implement rate limiting
- Use HTTPS in production
- Validate all user inputs
- Implement proper CORS policies

