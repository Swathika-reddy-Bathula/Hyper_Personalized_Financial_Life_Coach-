"""
Streamlit Demo Interface for AI Financial Assistant
"""
import streamlit as st
import openai
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="💰",
    layout="wide"
)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_context" not in st.session_state:
    st.session_state.user_context = {
        "age": 30,
        "income": 50000,
        "risk_tolerance": "moderate"
    }

def chat_with_ai(message, context=None):
    """Chat with OpenAI directly for demo"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful financial assistant. 
                    Provide clear, actionable financial advice. Always explain your reasoning.
                    Be empathetic and supportive. Help users with:
                    - Goal-based investment planning
                    - Budgeting and spending analysis
                    - Financial product recommendations
                    - Risk assessment"""
                },
                {
                    "role": "user",
                    "content": f"User Context: {json.dumps(context or {})}\n\nUser Message: {message}"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_goal(user_input, context):
    """Analyze and extract financial goals"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial planning assistant. 
                    Extract financial goals from user input and create a structured plan.
                    Return a JSON object with: title, description, goal_type, target_amount, target_date, monthly_contribution, reasoning."""
                },
                {
                    "role": "user",
                    "content": f"User Input: {user_input}\nUser Context: {json.dumps(context)}\n\nExtract the financial goal and create a detailed plan."
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_recommendations(context):
    """Get product recommendations with reasoning"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial advisor. Recommend suitable financial products.
                    Consider user's age, income, and risk tolerance. Provide clear reasoning for each recommendation."""
                },
                {
                    "role": "user",
                    "content": f"User Profile: {json.dumps(context)}\n\nRecommend 3-5 suitable financial products with detailed explanations."
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar for user profile
with st.sidebar:
    st.header("👤 User Profile")
    age = st.slider("Age", 18, 80, st.session_state.user_context.get("age", 30))
    income = st.number_input("Annual Income ($)", min_value=0, value=int(st.session_state.user_context.get("income", 50000)), step=1000)
    risk_tolerance = st.selectbox(
        "Risk Tolerance",
        ["conservative", "moderate", "aggressive"],
        index=["conservative", "moderate", "aggressive"].index(st.session_state.user_context.get("risk_tolerance", "moderate"))
    )
    
    st.session_state.user_context = {
        "age": age,
        "income": income,
        "risk_tolerance": risk_tolerance
    }
    
    st.divider()
    
    if st.button("Get Recommendations"):
        with st.spinner("Analyzing your profile..."):
            recommendations = get_recommendations(st.session_state.user_context)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"**Product Recommendations:**\n\n{recommendations}"
            })

# Main interface
st.title("💰 AI Financial Assistant")
st.markdown("Your personalized financial coach powered by AI")

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🎯 Goals", "📊 Insights"])

with tab1:
    st.header("Chat with Your Financial Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your finances..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_ai(prompt, st.session_state.user_context)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with tab2:
    st.header("Financial Goals")
    
    goal_input = st.text_area(
        "Describe your financial goal:",
        placeholder="e.g., I want to save $50,000 for a down payment on a house in 3 years"
    )
    
    if st.button("Analyze Goal"):
        if goal_input:
            with st.spinner("Analyzing your goal..."):
                plan = analyze_goal(goal_input, st.session_state.user_context)
                st.markdown("### Goal Analysis & Plan")
                st.markdown(plan)
        else:
            st.warning("Please enter a goal description")

with tab3:
    st.header("Financial Insights")
    
    st.subheader("Your Profile Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Age", st.session_state.user_context["age"])
    with col2:
        st.metric("Annual Income", f"${st.session_state.user_context['income']:,}")
    with col3:
        st.metric("Risk Tolerance", st.session_state.user_context["risk_tolerance"].title())
    
    st.divider()
    
    st.subheader("Quick Insights")
    st.info("""
    **Based on your profile:**
    - Recommended emergency fund: ${:,.0f} (6 months expenses)
    - Suggested monthly savings: ${:,.0f} (20% of income)
    - Investment horizon: {} years until retirement
    """.format(
        st.session_state.user_context["income"] * 0.5,
        st.session_state.user_context["income"] * 0.2 / 12,
        65 - st.session_state.user_context["age"]
    ))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI Financial Assistant Demo | Powered by GPT-4</p>
</div>
""", unsafe_allow_html=True)

