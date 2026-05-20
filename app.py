import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# ============================================================================
# PAGE CONFIG & SETUP
# ============================================================================
st.set_page_config(
    page_title="TICO Wholesale Core (SQL)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None

if "current_items" not in st.session_state:
    st.session_state.current_items = []

# ============================================================================
# SQL DATABASE CONNECTION
# ============================================================================
DB_URL = st.secrets.get("DATABASE_URL", "")

def get_db_connection():
    if not DB_URL:
        st.error("❌ DATABASE_URL lagama helin Streamlit Secrets!")
        return None
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"❌ Xiriirka Database-ka ayaa go'an: {e}")
        return None

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
        h1, h2, h3, h4 { font-family: 'Segoe UI', sans-serif; color: #ffffff; }
        .stTextInput input, .stSelectbox select, .stNumberInput input {
            background-color: #151b27 !important; color: #ffffff !important; border: 1px solid #2d3748 !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #1f77b4 0%, #1557a0
