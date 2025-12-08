# Architecture Overview

## System Architecture

```
┌─────────────────┐
│   Frontend      │  Next.js + React + Tailwind CSS
│   (Port 3000)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend API   │  FastAPI + Python
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼───┐ ┌────▼────┐ ┌───▼───┐
│PostgreSQL│ │OpenAI│ │Pinecone│ │  AWS  │
│Database  │ │ API  │ │VectorDB│ │Services│
└─────────┘ └──────┘ └────────┘ └────────┘
```

## Component Overview

### Backend (FastAPI)

#### Models
- **User**: User accounts and profiles
- **Goal**: Financial goals with AI-generated plans
- **Transaction**: Income and expense tracking
- **Product**: Financial products catalog
- **Alert**: Predictive financial alerts

#### Services
- **AIService**: LangChain + OpenAI integration for:
  - Goal understanding and planning
  - Spending behavior analysis
  - Product recommendation reasoning (XAI)
  - Conversational chat

- **GoalService**: Goal management with AI planning
- **BudgetService**: Budget analysis with AI insights
- **RecommendationService**: Product matching with XAI
- **AlertService**: Predictive alert generation

#### API Endpoints
- `/api/v1/auth/*` - Authentication
- `/api/v1/goals/*` - Goal management
- `/api/v1/budgeting/*` - Budget and transactions
- `/api/v1/recommendations/*` - Product recommendations
- `/api/v1/alerts/*` - Financial alerts
- `/api/v1/chat` - Conversational interface

### Frontend (Next.js)

#### Pages
- Main dashboard with tabbed interface
- Login/Registration

#### Components
- **ChatInterface**: Conversational AI chat
- **GoalsDashboard**: Goal creation and tracking
- **BudgetInsights**: Spending analysis and charts
- **Recommendations**: Product recommendations with XAI
- **Alerts**: Financial alerts and notifications

### Demo (Streamlit)

Standalone demo interface for quick testing:
- Chat interface
- Goal analysis
- Financial insights
- Direct OpenAI integration

## Data Flow

### Goal Creation Flow
1. User creates goal via frontend
2. Backend receives goal data
3. AIService analyzes goal and generates plan
4. Goal saved with AI plan
5. Response returned to frontend

### Recommendation Flow
1. User requests recommendations
2. Backend fetches user profile
3. RecommendationService matches products
4. AIService generates XAI reasoning
5. Recommendations returned with explanations

### Alert Generation Flow
1. AlertService checks various conditions:
   - Low balance
   - Goal deadlines
   - Budget exceeded
2. Alerts created and stored
3. Frontend polls for new alerts
4. User notified

## AI Integration

### LangChain
- Used for structured AI interactions
- Prompt templates for consistent responses
- Chain composition for complex workflows

### OpenAI GPT-4
- Goal understanding and planning
- Spending pattern analysis
- Product recommendation reasoning
- Conversational responses

### Explainable AI (XAI)
- Every recommendation includes reasoning
- Clear explanations of why products match
- Transparency in decision-making
- Builds user trust

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation
- SQL injection prevention (SQLAlchemy ORM)

## Scalability Considerations

- Database connection pooling
- Async/await for I/O operations
- Caching strategies (can be added)
- Rate limiting (can be added)
- Load balancing ready

## Future Enhancements

- Vector database integration (Pinecone/FAISS)
- Advanced analytics with LlamaIndex
- Real-time notifications (WebSockets)
- Mobile app (React Native)
- Integration with banking APIs
- Multi-currency support
- Advanced ML models for predictions

