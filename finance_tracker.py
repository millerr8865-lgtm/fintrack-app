import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os
import sqlite3
import bcrypt

# File paths
DATA_DIR = "data"
INCOME_FILE = os.path.join(DATA_DIR, "income.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
DEBTS_FILE = os.path.join(DATA_DIR, "debts.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
DB_FILE = os.path.join(DATA_DIR, "users.db")

os.makedirs(DATA_DIR, exist_ok=True)

# Database setup for users
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password_hash TEXT, name TEXT)''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(email, password, name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)", (email, hashed, name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password_hash, name FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    if result and verify_password(password, result[0]):
        return result[1]
    return None

# Data loading functions
def load_data(file_path, default_df):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        default_df.to_csv(file_path, index=False)
        return default_df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Default DFs
income_df = pd.DataFrame(columns=['Date', 'Source', 'Amount', 'Notes'])
expenses_df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Notes'])
debts_df = pd.DataFrame(columns=['Debt Name', 'Total Balance', 'Interest Rate', 'Min Payment', 'Extra Payment'])

income_df = load_data(INCOME_FILE, income_df)
expenses_df = load_data(EXPENSES_FILE, expenses_df)
debts_df = load_data(DEBTS_FILE, debts_df)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"monthly_income": 0.0, "savings_goal": 0.20}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

settings = load_settings()

# Custom CSS for modern/sleek UI
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .css-1d391kg { background-color: #161b22; }
    h1, h2, h3 { color: #58a6ff; }
    .stButton>button { background-color: #238636; color: white; border-radius: 6px; }
    .metric-card { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="FinTrack", layout="wide", initial_sidebar_state="expanded")

# Authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

if not st.session_state.logged_in:
    st.title("🔐 Welcome to FinTrack")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            name = login_user(email, password)
            if name:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.success(f"Welcome back, {name}!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Register")
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(email, password, name):
                st.success("Registration successful! Please login.")
            else:
                st.error("Email already exists")
    st.stop()

# Main App
st.title(f"💰 FinTrack - Welcome, {st.session_state.user_name}")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Income", "Expenses/Bills", "Debts", "Savings", "Settings"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Load data
income_df = load_data(INCOME_FILE, income_df)
expenses_df = load_data(EXPENSES_FILE, expenses_df)
debts_df = load_data(DEBTS_FILE, debts_df)

if page == "Dashboard":
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
    
    if not income_df.empty:
        st.subheader("Income Trends")
        income_plot = income_df.copy()
        income_plot['Date'] = pd.to_datetime(income_plot['Date'])
        fig = px.bar(income_plot, x='Date', y='Amount', color='Source', title="Income History")
        st.plotly_chart(fig, use_container_width=True)
    
    if not expenses_df.empty:
        st.subheader("Expenses Breakdown")
        fig_exp = px.pie(expenses_df, names='Category', values='Amount')
        st.plotly_chart(fig_exp, use_container_width=True)
    
    st.subheader("Debts")
    if not debts_df.empty:
        fig_debt = px.bar(debts_df, x='Debt Name', y='Total Balance')
        st.plotly_chart(fig_debt, use_container_width=True)

elif page == "Income":
    st.header("Income Tracking")
    with st.form("add_income"):
        col1, col2 = st.columns(2)
        with col1:
            date_inc = st.date_input("Date", value=date.today())
            source = st.text_input("Source (Salary, OT, etc.)")
        with col2:
            amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        notes = st.text_area("Notes")
        if st.form_submit_button("Add Income"):
            new_row = pd.DataFrame([{'Date': date_inc, 'Source': source, 'Amount': amount, 'Notes': notes}])
            income_df = pd.concat([income_df, new_row], ignore_index=True)
            save_data(income_df, INCOME_FILE)
            st.success("Added!")
            st.rerun()
    
    st.dataframe(income_df, use_container_width=True)

elif page == "Expenses/Bills":
    st.header("Expenses & Upcoming Bills")
    with st.form("add_expense"):
        col1, col2 = st.columns(2)
        with col1:
            date_exp = st.date_input("Date")
            category = st.selectbox("Category", ["Rent", "Utilities", "Groceries", "Transport", "Insurance", "Debt", "Other"])
        with col2:
            amount = st.number_input("Amount ($)", min_value=0.0)
        notes = st.text_area("Notes / Due Date")
        if st.form_submit_button("Add Expense"):
            new_row = pd.DataFrame([{'Date': date_exp, 'Category': category, 'Amount': amount, 'Notes': notes}])
            expenses_df = pd.concat([expenses_df, new_row], ignore_index=True)
            save_data(expenses_df, EXPENSES_FILE)
            st.success("Added!")
            st.rerun()
    
    st.dataframe(expenses_df, use_container_width=True)

elif page == "Debts":
    st.header("Debt Tracker")
    with st.form("add_debt"):
        debt_name = st.text_input("Debt Name")
        balance = st.number_input("Balance", min_value=0.0)
        rate = st.number_input("Interest Rate (%)", min_value=0.0)
        min_pay = st.number_input("Min Payment", min_value=0.0)
        extra = st.number_input("Extra Payment (this month)", min_value=0.0)
        if st.form_submit_button("Save Debt"):
            new_row = pd.DataFrame([{'Debt Name': debt_name, 'Total Balance': balance, 
                                   'Interest Rate': rate, 'Min Payment': min_pay, 'Extra Payment': extra}])
            if not debts_df.empty and debt_name in debts_df['Debt Name'].values:
                debts_df.loc[debts_df['Debt Name'] == debt_name] = new_row.iloc[0]
            else:
                debts_df = pd.concat([debts_df, new_row], ignore_index=True)
            save_data(debts_df, DEBTS_FILE)
            st.success("Saved!")
            st.rerun()
    
    st.dataframe(debts_df, use_container_width=True)
    if not debts_df.empty:
        st.write(f"**Total Debt:** ${debts_df['Total Balance'].sum():,.2f}")

elif page == "Savings":
    st.header("Savings & Projections")
    monthly_income = st.number_input("Monthly Income (incl. OT)", value=settings.get("monthly_income", 0.0))
    savings_rate = st.slider("Target Savings Rate (%)", 0, 100, int(settings.get("savings_goal", 0.2)*100))
    
    if st.button("Save Settings"):
        settings["monthly_income"] = monthly_income
        settings["savings_goal"] = savings_rate / 100.0
        save_settings(settings)
        st.success("Saved!")
    
    total_exp = expenses_df['Amount'].sum() if not expenses_df.empty else 0
    disposable = monthly_income - total_exp
    savings = disposable * (savings_rate / 100)
    debt_extra = disposable - savings
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Disposable Income", f"${disposable:,.2f}")
    col2.metric("Recommended Savings", f"${savings:,.2f}")
    col3.metric("For Extra Debt", f"${debt_extra:,.2f}")

elif page == "Settings":
    st.header("App Settings")
    st.info("Data stored locally in CSV files.")
    if st.button("Reset All Data"):
        if st.checkbox("I understand this will delete everything"):
            for f in [INCOME_FILE, EXPENSES_FILE, DEBTS_FILE]:
                if os.path.exists(f): os.remove(f)
            st.success("Data reset. Refresh page.")
            st.rerun()

st.sidebar.success("Modern sleek UI • Email auth • Persistent data")
