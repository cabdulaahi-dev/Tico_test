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
            background: linear-gradient(135deg, #1f77b4 0%, #1557a0 100%); color: white; border-radius: 8px; font-weight: 600; width: 100%;
        }
        .role-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; font-weight: 600; }
        .role-admin { background-color: #d62728; color: white; }
        .role-viewer { background-color: #ff7f0e; color: white; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOGIN SYSTEM
# ============================================================================
def check_password():
    if not st.session_state.authenticated:
        st.markdown("<div style='text-align: center; padding: 2rem 0;'><h1>TICO Wholesale SQL Core</h1><p style='color: #b0b8c1;'>Secure SQL Database & Deep Analytics</p></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Login Required")
            password = st.text_input("Enter Password", type="password", key="pwd_input")
            if st.button("Unlock Access", use_container_width=True):
                if password == "Tico000123":
                    st.session_state.authenticated = True
                    st.session_state.role = "admin"
                    st.rerun()
                elif password == "Tico000":
                    st.session_state.authenticated = True
                    st.session_state.role = "viewer"
                    st.rerun()
                else:
                    st.error("❌ Password khaldan!")
        return False
    return True

# ============================================================================
# MAIN APPLICATION
# ============================================================================
if check_password():
    sales_df = pd.DataFrame()
    payments_df = pd.DataFrame()
    
    conn = get_db_connection()
    if conn:
        try:
            sales_df = pd.read_sql_query("SELECT * FROM sql_tico_sales", conn)
            payments_df = pd.read_sql_query("SELECT * FROM sql_tico_payments", conn)
        except Exception as e:
            st.warning(f"Xogta lama soo kicin karin: {e}")
        finally:
            conn.close()

    if not sales_df.empty:
        sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")
    if not payments_df.empty:
        payments_df["date"] = pd.to_datetime(payments_df["date"], errors="coerce")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.markdown("# 📊 TICO Wholesale (SQL Core)")
    with c2:
        if st.session_state.role == "admin":
            st.markdown('<span class="role-badge role-admin">👤 ADMIN ACCESS</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="role-badge role-viewer">👁️ VIEWER ACCESS</span>', unsafe_allow_html=True)
    with c3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()

    st.divider()

    # Sidebar
    with st.sidebar:
        time_filter = st.radio("Period:", ["All Time", "Today", "This Month"])
        st.divider()
        if st.session_state.role == "admin":
            menu = st.radio("Menu:", ["Dashboard", "Sales Entry", "Payment Entry", "Customer History", "Data Management"])
        else:
            menu = st.radio("Menu:", ["Dashboard", "Customer History"])

    # Sifeynta waqtiga ee xogta (Time Filtering)
    filtered_sales = sales_df.copy()
    if not sales_df.empty:
        current_date = datetime.now().date()
        if time_filter == "Today":
            filtered_sales = sales_df[sales_df["date"].dt.date == current_date]
        elif time_filter == "This Month":
            filtered_sales = sales_df[
                (sales_df["date"].dt.year == current_date.year) & 
                (sales_df["date"].dt.month == current_date.month)
            ]

    # ------------------------------------------------------------------------
    # PAGE: DASHBOARD (ANALYTICS ENGINE)
    # ------------------------------------------------------------------------
    if menu == "Dashboard":
        st.markdown(f"## 🏠 Analytics Dashboard ({time_filter})")
        
        if not filtered_sales.empty:
            # Xisaabinta guud ee Maaliyadda
            rev = filtered_sales["total"].sum()
            cost = (filtered_sales["quantity"] * filtered_sales["cost_price"]).sum()
            prof = rev - cost
            items_sold = filtered_sales["quantity"].sum()

            # --- DEEP ANALYTICS ENGINE (Badeecadaha ugu iibka badan/hooseeya) ---
            # Group gareey xogta badeecad kasta si loo helo xaddiga (Quantity) iyo Faa'iidada (Profit)
            filtered_sales["item_profit"] = filtered_sales["total"] - (filtered_sales["quantity"] * filtered_sales["cost_price"])
            item_summary = filtered_sales.groupby("item_name").agg(
                Total_Qty=("quantity", "sum"),
                Total_Profit=("item_profit", "sum")
            ).reset_index()

            top_item_row = item_summary.loc[item_summary["Total_Qty"].idxmax()]
            lowest_item_row = item_summary.loc[item_summary["Total_Qty"].idxmin()]
            
            top_item = f"{top_item_row['item_name']} ({int(top_item_row['Total_Qty'])} xabo)"
            lowest_item = f"{lowest_item_row['item_name']} ({int(lowest_item_row['Total_Qty'])} xabo)"
        else:
            rev, cost, prof, items_sold = 0.0, 0.0, 0.0, 0
            top_item, lowest_item = "Ma jirto", "Ma jirto"

        # Muujinta Metrics-ka sare
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("💰 Total Revenue", f"${rev:,.2f}")
        with col2: st.metric("📊 Net Profit (Faa'iido)", f"${prof:,.2f}")
        with col3: st.metric("📦 Top Selling Item (Ugu iibka badan)", top_item)
        with col4: st.metric("📉 Lowest Selling Item", lowest_item)

        st.divider()
        st.markdown("### 📋 Liiska Iibka ee Shaxda (Item Profit Breakdowns)")
        if not filtered_sales.empty:
            disp_df = filtered_sales.copy()
            disp_df["date"] = disp_df["date"].dt.strftime("%Y-%m-%d")
            disp_df["profit_per_item"] = disp_df["total"] - (disp_df["quantity"] * disp_df["cost_price"])
            
            # Dib u habayn tiirarka si ay u qurux weynaadaan
            show_cols = ["id", "date", "customer_name", "item_name", "quantity", "price", "discount", "total", "profit_per_item", "status"]
            st.dataframe(disp_df[show_cols].sort_values("id", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Wax xog ah kama dhex dhalan mudadan loo doortay.")

    # ------------------------------------------------------------------------
    # PAGE: SALES ENTRY
    # ------------------------------------------------------------------------
    elif menu == "Sales Entry":
        st.markdown("## 📝 Record New Sale (Multi-Item SQL)")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: s_date = st.date_input("Date", value=datetime.now())
        with col_m2: c_name = st.text_input("Customer Name")
        with col_m3: status = st.selectbox("Payment Status", ["Cash", "Invoice"])
            
        st.divider()
        st.markdown("#### 📦 Add Items")
        col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1, 1, 1])
        with col_i1: i_name = st.text_input("Item Name", key="i_txt")
        with col_i2: qty = st.number_input("Quantity", min_value=1, value=1, key="i_qty")
        with col_i3: price = st.number_input("Price ($)", min_value=0.00, value=0.00, key="i_prc")
        with col_i4: c_price = st.number_input("Cost Price ($)", min_value=0.00, value=0.00, key="i_cst")
            
        discount = st.number_input("⚡ Discount ($)", min_value=0.00, value=0.00)
        
        if st.button("➕ Add Item to List", use_container_width=True):
            if not i_name.strip(): st.error("Geli magaca badeecada!")
            else:
                tot = (qty * price) - discount
                st.session_state.current_items.append({
                    "item_name": i_name.
