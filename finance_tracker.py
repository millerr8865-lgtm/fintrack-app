import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os
import sqlite3
import bcrypt
from openai import OpenAI  # Compatible with xAI

# File paths
DATA_DIR = "data"
INCOME_FILE = os.path.join(DATA_DIR, "income.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
DEBTS_FILE = os.path.join(DATA_DIR, "debts.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
DB_FILE = os.path.join(DATA_DIR, "users.db")

os.makedirs(DATA_DIR, exist_ok=True)

# ... (Keep all your existing auth, load/save functions exactly as they are - lines 21-92 from current file)

# Grok / xAI Setup
def get_grok_client():
    api_key = st.session_state.get("grok_api_key")
    if not api_key:
        return None
    return OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1"
    )

# Custom CSS (kept + enhanced)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3 { color: #58a6ff; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; }
    .metric-card { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="FinTrack AI", layout="wide")

# Authentication (your existing code - kept unchanged)

# ... [paste your full auth block here if editing manually]

# Main App after login
st.title(f"💰 FinTrack AI - Welcome, {st.session_state.user_name}")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Income", "Expenses/Bills", "Debts", "AI Budget Advisor", "Settings"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Load data
income_df = load_data(INCOME_FILE, pd.DataFrame(columns=['Date', 'Source', 'Amount', 'Notes']))
expenses_df = load_data(EXPENSES_FILE, pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Notes']))
debts_df = load_data(DEBTS_FILE, pd.DataFrame(columns=['Debt Name', 'Total Balance', 'Interest Rate', 'Min Payment', 'Extra Payment']))

if page == "Dashboard":
    # Your existing Dashboard code (unchanged)
    st.header("Overview")
    total_income = income_df['Amount'].sum() if not income_df.empty else 0
    total_expenses = expenses_df['Amount'].sum() if not expenses_df.empty else 0
    net = total_income - total_expenses
    total_debt = debts_df['Total Balance'].sum() if not debts_df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Income", f"${total_income:,.2f}")
    with col2: st.metric("Total Expenses", f"${total_expenses:,.2f}")
    with col3: st.metric("Net", f"${net:,.2f}")
    with col4: st.metric("Total Debt", f"${total_debt:,.2f}")
    
    # Charts (existing)

elif page == "AI Budget Advisor":
    st.header("🤖 Grok AI Financial Advisor")
    
    if "grok_api_key" not in st.session_state:
        st.warning("Enter your Grok API key in Settings first.")
    else:
        if st.button("🔍 Get AI Weekly Budget & Recommendations", type="primary"):
            with st.spinner("Grok is analyzing your finances..."):
                client = get_grok_client()
                
                # Prepare context
                context = f"""
                Current data:
                Monthly Income: ${income_df['Amount'].sum() if not income_df.empty else 0}
                Total Expenses: ${expenses_df['Amount'].sum() if not expenses_df.empty else 0}
                Total Debt: ${debts_df['Total Balance'].sum() if not debts_df.empty else 0}
                Recent categories: {expenses_df['Category'].value_counts().to_dict() if not expenses_df.empty else 'None'}
                """
                
                response = client.chat.completions.create(
                    model="grok-4.1-fast",  # Cheapest good model
                    messages=[
                        {"role": "system", "content": "You are an expert personal finance advisor. Give practical, numbers-based weekly allocations for bills, savings, groceries, leisure, debt payoff."},
                        {"role": "user", "content": f"Analyze this user's finances and suggest a smart weekly budget breakdown. {context}"}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                
                advice = response.choices[0].message.content
                st.success("✅ AI Analysis Complete")
                st.markdown(advice)
                
                # Optional: Show charts based on AI suggestions
                st.subheader("Visual Breakdown")
                # You can parse AI output for charts later

elif page == "Settings":
    st.header("Settings")
    grok_key = st.text_input("Grok (xAI) API Key", type="password", value=st.session_state.get("grok_api_key", ""))
    if st.button("Save API Key"):
        st.session_state.grok_api_key = grok_key
        st.success("API Key saved (in session only)!")
    
    # Your existing reset data option

# Keep all other pages (Income, Expenses, Debts) as they are
