import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import json
import os
import sqlite3
import bcrypt
from openai import OpenAI

# File paths (unchanged)
DATA_DIR = "data"
INCOME_FILE = os.path.join(DATA_DIR, "income.csv")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.csv")
DEBTS_FILE = os.path.join(DATA_DIR, "debts.csv")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
DB_FILE = os.path.join(DATA_DIR, "users.db")

os.makedirs(DATA_DIR, exist_ok=True)

# === All your existing helper functions (init_db, hash_password, etc.) ===
# (I'm keeping them exactly as they are in your current file)

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

def load_data(file_path, default_df):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        default_df.to_csv(file_path, index=False)
        return default_df

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"monthly_income": 0.0, "savings_goal": 0.20}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def get_grok_client():
    api_key = st.session_state.get("grok_api_key")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

# Custom CSS + Config
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3 { color: #58a6ff; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="FinTrack AI", layout="wide")

# Initialize session state safely
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# Authentication
if not st.session_state.logged_in:
    st.title("🔐 Welcome to FinTrack AI")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            name = login_user(email, password)
            if name:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            if register_user(email, password, name):
                st.success("Registration successful! Please login.")
            else:
                st.error("Email already exists")
    st.stop()

# ====================== MAIN APP ======================
st.title(f"💰 FinTrack AI - Welcome, {st.session_state.user_name or 'User'}")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Dashboard", "Income", "Expenses/Bills", "Debts", "Savings", "AI Budget Advisor", "Settings"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Load data
income_df = load_data(INCOME_FILE, pd.DataFrame(columns=['Date', 'Source', 'Amount', 'Notes']))
expenses_df = load_data(EXPENSES_FILE, pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Notes']))
debts_df = load_data(DEBTS_FILE, pd.DataFrame(columns=['Debt Name', 'Total Balance', 'Interest Rate', 'Min Payment', 'Extra Payment']))

# (The rest of your pages — Dashboard, Income, etc. — remain the same)
# Paste the rest from your current file here (lines ~184 to end)

# ... [Keep all your page logic exactly as it is]

# For completeness, here's the AI and Settings tabs again (already in your file)
