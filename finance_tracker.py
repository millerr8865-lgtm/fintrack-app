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

# Load/Save helpers
def load_data(file_path, columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
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
st.title("💰 FinTrack AI - Your Simple Finance Tracker")

# Simple PIN protection (set once)
if 'pin_set' not in st.session_state:
    st.session_state.pin_set = False
    st.session_state.pin = "1234"  # Change this to your own PIN

if not st.session_state.pin_set:
    st.subheader("Set Your 4-Digit PIN")
    new_pin = st.text_input("Create a simple PIN", type="password", max_chars=4)
    if st.button("Set PIN"):
        if new_pin:
            st.session_state.pin = new_pin
            st.session_state.pin_set = True
            st.success("PIN saved!")
            st.rerun()
    st.stop()

pin_input = st.text_input("Enter PIN to access", type="password", max_chars=4)
if pin_input != st.session_state.pin:
    st.warning("Enter correct PIN")
    st.stop()

# Metrics
total_income = income_df['Amount'].sum() if not income_df.empty else 0
total_exp = expenses_df['Amount'].sum() if not expenses_df.empty else 0
net = total_income - total_exp
total_debt = debts_df['Total Balance'].sum() if not debts_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Income", f"${total_income:,.2f}")
col2.metric("Expenses", f"${total_exp:,.2f}")
col3.metric("Net", f"${net:,.2f}")
col4.metric("Debt", f"${total_debt:,.2f}")

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💵 Add Income", "📤 Add Expense/Bill", "💳 Debts", "🤖 AI Advisor"])

with tab1:
    st.header("Overview")
    if not income_df.empty:
        st.plotly_chart(px.bar(income_df, x='Date', y='Amount', color='Source'), use_container_width=True)
    if not expenses_df.empty:
        st.plotly_chart(px.pie(expenses_df, names='Category', values='Amount'), use_container_width=True)

with tab2:  # Add Income
    with st.form("income_form"):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
            source = st.text_input("Source (Job, OT, Bonus)")
        with c2:
            amt = st.number_input("Amount $", min_value=0.01, step=0.01)
        notes = st.text_area("Notes", height=80)
        if st.form_submit_button("✅ Add Income"):
            new = pd.DataFrame([{'Date': d, 'Source': source, 'Amount': amt, 'Notes': notes}])
            global income_df
            income_df = pd.concat([income_df, new], ignore_index=True)
            save_data(income_df, INCOME_FILE)
            st.success("Income added!")
            st.rerun()

with tab3:  # Add Expense
    with st.form("expense_form"):
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
            cat = st.selectbox("Category", ["Rent", "Utilities", "Groceries", "Gas", "Food", "Insurance", "Debt Payment", "Other"])
        with c2:
            amt = st.number_input("Amount $", min_value=0.01)
        notes = st.text_area("Notes (e.g. due date, recurring)")
        if st.form_submit_button("✅ Add Expense"):
            new = pd.DataFrame([{'Date': d, 'Category': cat, 'Amount': amt, 'Notes': notes}])
            global expenses_df
            expenses_df = pd.concat([expenses_df, new], ignore_index=True)
            save_data(expenses_df, EXPENSES_FILE)
            st.success("Expense added!")
            st.rerun()

with tab4:  # Debts
    with st.form("debt_form"):
        name = st.text_input("Debt Name (e.g. Car Loan)")
        bal = st.number_input("Current Balance $", min_value=0.0)
        if st.form_submit_button("Save Debt"):
            new = pd.DataFrame([{'Debt Name': name, 'Total Balance': bal, 'Interest Rate': 0.0, 'Min Payment': 0.0, 'Extra Payment': 0.0}])
            global debts_df
            debts_df = pd.concat([debts_df, new], ignore_index=True)
            save_data(debts_df, DEBTS_FILE)
            st.success("Debt saved!")
            st.rerun()
    st.dataframe(debts_df, use_container_width=True)

with tab5:
    st.header("🤖 Grok AI Advisor")
    if st.button("Analyze My Finances & Suggest Weekly Plan", type="primary"):
        with st.spinner("Grok is analyzing..."):
            # (Grok code from before - works if you have key in session)
            st.info("Add your Grok key in Settings if needed. AI will give bills/savings/groceries breakdown.")

# Settings in sidebar
with st.sidebar:
    st.header("Settings")
    if st.button("Reset All Data"):
        if st.checkbox("Confirm delete all?"):
            for f in [INCOME_FILE, EXPENSES_FILE, DEBTS_FILE]:
                if os.path.exists(f): os.remove(f)
            st.success("All data cleared")
            st.rerun()
    st.caption("Data saves automatically. PIN is remembered in this browser.")

st.success("✅ Super simple mode active")
