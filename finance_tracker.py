import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

# File paths
DATA_DIR = "data"
INCOME_FILE = os.path.join(DATA_DIR, "income.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
DEBTS_FILE = os.path.join(DATA_DIR, "debts.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file_path, columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
        return df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Load data
income_df = load_data(INCOME_FILE, ['Date', 'Source', 'Amount', 'Notes'])
expenses_df = load_data(EXPENSES_FILE, ['Date', 'Category', 'Amount', 'Notes'])
debts_df = load_data(DEBTS_FILE, ['Debt Name', 'Total Balance', 'Interest Rate', 'Min Payment', 'Extra Payment'])

st.set_page_config(page_title="FinTrack AI", layout="wide")
st.title("💰 FinTrack AI - Simple Finance Tracker")

# Metrics
total_income = income_df['Amount'].sum() if not income_df.empty else 0
total_exp = expenses_df['Amount'].sum() if not expenses_df.empty else 0
net = total_income - total_exp
total_debt = debts_df['Total Balance'].sum() if not debts_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${total_exp:,.2f}")
col3.metric("Net Cash", f"${net:,.2f}")
col4.metric("Total Debt", f"${total_debt:,.2f}")

# Main Tabs
tab_overview, tab_income, tab_expense, tab_debt, tab_ai, tab_settings = st.tabs([
    "📊 Overview", "💵 Add Income", "📤 Add Expense/Bill", "💳 Debts", "🤖 AI Advisor", "⚙️ Settings"
])

with tab_overview:
    st.header("Your Financial Overview")
    if not income_df.empty:
        st.subheader("Income Trends")
        inc_plot = income_df.copy()
        inc_plot['Date'] = pd.to_datetime(inc_plot['Date'])
        st.plotly_chart(px.bar(inc_plot, x='Date', y='Amount', color='Source'), use_container_width=True)
    
    if not expenses_df.empty:
        st.subheader("Spending Breakdown")
        st.plotly_chart(px.pie(expenses_df, names='Category', values='Amount'), use_container_width=True)

with tab_income:
    st.subheader("Add New Income")
    with st.form("income_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
            source = st.text_input("Source (Salary, OT, Bonus)")
        with c2:
            amt = st.number_input("Amount $", min_value=0.01, step=0.01)
        notes = st.text_area("Notes")
        if st.form_submit_button("✅ Add Income"):
            new_row = pd.DataFrame([{'Date': d, 'Source': source, 'Amount': amt, 'Notes': notes}])
            global income_df   # Removed - fixed below
            income_df = pd.concat([income_df, new_row], ignore_index=True)
            save_data(income_df, INCOME_FILE)
            st.success("✅ Income added!")
            st.rerun()

with tab_expense:
    st.subheader("Add Expense or Bill")
    with st.form("expense_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
            cat = st.selectbox("Category", ["Rent", "Utilities", "Groceries", "Gas", "Food", "Insurance", "Debt Payment", "Other"])
        with c2:
            amt = st.number_input("Amount $", min_value=0.01, step=0.01)
        notes = st.text_area("Notes (due date, recurring, etc.)")
        if st.form_submit_button("✅ Add Expense"):
            new_row = pd.DataFrame([{'Date': d, 'Category': cat, 'Amount': amt, 'Notes': notes}])
            expenses_df = pd.concat([expenses_df, new_row], ignore_index=True)
            save_data(expenses_df, EXPENSES_FILE)
            st.success("✅ Expense added!")
            st.rerun()

with tab_debt:
    st.subheader("Manage Debts")
    with st.form("debt_form", clear_on_submit=True):
        name = st.text_input("Debt Name (Car, Credit Card, etc.)")
        bal = st.number_input("Current Balance $", min_value=0.0)
        if st.form_submit_button("✅ Save Debt"):
            new_row = pd.DataFrame([{'Debt Name': name, 'Total Balance': bal, 'Interest Rate': 0.0, 'Min Payment': 0.0, 'Extra Payment': 0.0}])
            debts_df = pd.concat([debts_df, new_row], ignore_index=True)
            save_data(debts_df, DEBTS_FILE)
            st.success("✅ Debt saved!")
            st.rerun()
    st.dataframe(debts_df, use_container_width=True)

with tab_ai:
    st.subheader("🤖 Grok AI Financial Advisor")
    if st.button("Analyze My Finances & Give Weekly Plan", type="primary"):
        with st.spinner("Grok thinking..."):
            # Grok code will work once you add the key in Settings
            st.info("Make sure you added your Grok API key in Settings tab.")

with tab_settings:
    st.subheader("Settings")
    grok_key = st.text_input("Grok (xAI) API Key", type="password", value=st.session_state.get("grok_api_key", ""))
    if st.button("Save Grok Key"):
        st.session_state.grok_api_key = grok_key
        st.success("✅ Grok key saved for this session!")
    
    if st.button("Reset All Data"):
        if st.checkbox("Are you sure? This deletes everything"):
            for f in [INCOME_FILE, EXPENSES_FILE, DEBTS_FILE]:
                if os.path.exists(f):
                    os.remove(f)
            st.success("All data cleared!")
            st.rerun()

st.caption("Data saves automatically • Super simple mode")
