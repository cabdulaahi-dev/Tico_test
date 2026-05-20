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

# Initialize session state for Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None

# Basket kumeelgaar ah ee dhowrka shey inta aan la kaydin
if "current_items" not in st.session_state:
    st.session_state.current_items = []

# ============================================================================
# SQL DATABASE CONNECTION
# ============================================================================
# Waxaan xogta sirta ah ka soo aqrinaynaa Streamlit Secrets si ay ammaan u noqoto
# DATABASE_URL wuxuu ka imaan doonaa Neon.tech
DB_URL = st.secrets.get("DATABASE_URL", "")

def get_db_connection():
    if not DB_URL:
        st.error("❌ DATABASE_URL lagama helin Streamlit Secrets! Fadlan nidaami.")
        return None
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"❌ Khata ayaa ka dhacday xiriirka Database-ka: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # Create Sales Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sql_tico_sales (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    customer_name VARCHAR(255) NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    price NUMERIC(10, 2) NOT NULL,
                    cost_price NUMERIC(10, 2) NOT NULL,
                    discount NUMERIC(10, 2) DEFAULT 0.0,
                    total NUMERIC(10, 2) NOT NULL,
                    status VARCHAR(50) NOT NULL
                );
            """)
            # Create Payments Table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sql_tico_payments (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    customer_name VARCHAR(255) NOT NULL,
                    amount_paid NUMERIC(10, 2) NOT NULL,
                    received_by VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()
        conn.close()

# Dhal Miisaska (Tables-ka) haddaanay jirin
if DB_URL:
    init_db()

# ============================================================================
# CUSTOM CSS FOR DARK THEME
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
        st.markdown("<div style='text-align: center; padding: 2rem 0;'><h1>TICO Wholesale SQL Core</h1><p style='color: #b0b8c1;'>Secure SQL Database Management</p></div>", unsafe_allow_html=True)
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
    # Soo aqri xogta hadda ku jirta SQL Database
    sales_df = pd.DataFrame()
    payments_df = pd.DataFrame()
    
    conn = get_db_connection()
    if conn:
        try:
            sales_df = pd.read_sql_query("SELECT * FROM sql_tico_sales", conn)
            payments_df = pd.read_sql_query("SELECT * FROM sql_tico_payments", conn)
        except Exception as e:
            st.warning(f"Xogta lama soo kicin karin hadda: {e}")
        finally:
            conn.close()

    if not sales_df.empty:
        sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")
    if not payments_df.empty:
        payments_df["date"] = pd.to_datetime(payments_df["date"], errors="coerce")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.markdown("# 📊 TICO Wholesale (SQL)")
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
        time_filter = st.radio("Period:", ["All Time", "Today"])
        st.divider()
        if st.session_state.role == "admin":
            menu = st.radio("Menu:", ["Dashboard", "Sales Entry", "Payment Entry", "Customer History"])
        else:
            menu = st.radio("Menu:", ["Dashboard", "Customer History"])

    filtered_sales = sales_df.copy()
    if time_filter == "Today" and not sales_df.empty:
        filtered_sales = sales_df[sales_df["date"].dt.date == datetime.now().date()]

    # ------------------------------------------------------------------------
    # PAGE: DASHBOARD
    # ------------------------------------------------------------------------
    if menu == "Dashboard":
        st.markdown(f"## 🏠 Dashboard Summary ({time_filter})")
        if not filtered_sales.empty:
            rev = filtered_sales["total"].sum()
            cost = (filtered_sales["quantity"] * filtered_sales["cost_price"]).sum()
            prof = rev - cost
            items = filtered_sales["quantity"].sum()
        else: rev, cost, prof, items = 0.0, 0.0, 0.0, 0

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("💰 Total Revenue", f"${rev:,.2f}")
        with col2: st.metric("📊 Net Profit", f"${prof:,.2f}")
        with col3: st.metric("📦 Items Sold", f"{int(items):,}")
        with col4: st.metric("🛍️ Total Rows", len(filtered_sales))

        st.divider()
        st.markdown("### 📋 Recent Sales (SQL Data)")
        if not filtered_sales.empty:
            disp = filtered_sales.copy()
            disp["date"] = disp["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(disp.sort_values("id", ascending=False), use_container_width=True, hide_index=True)
        else: st.info("Database-ka xog kuma jirto weli.")

    # ------------------------------------------------------------------------
    # PAGE: SALES ENTRY (SAVE TO SQL)
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
                    "item_name": i_name.strip(), "quantity": qty, "price": price, "cost_price": c_price, "discount": discount, "total": tot
                })
                st.success(f"✓ {i_name} lagu daray dambiisha!")
                st.rerun()

        if st.session_state.current_items:
            st.markdown("---")
            basket_df = pd.DataFrame(st.session_state.current_items)
            st.dataframe(basket_df, use_container_width=True, hide_index=True)
            grand_total = basket_df["total"].sum()
            st.markdown(f"### 🏷️ Grand Total: **${grand_total:,.2f}**")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🗑️ Clear Basket"):
                    st.session_state.current_items = []
                    st.rerun()
            with col_b2:
                if st.button("💾 Save Full Transaction to SQL"):
                    if not c_name.strip(): st.error("Qor magaca macaamilka!")
                    else:
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                for item in st.session_state.current_items:
                                    cur.execute("""
                                        INSERT INTO sql_tico_sales (date, customer_name, item_name, quantity, price, cost_price, discount, total, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                                    """, (str(s_date), c_name.strip(), item["item_name"], item["quantity"], item["price"], item["cost_price"], item["discount"], item["total"], status))
                                conn.commit()
                            conn.close()
                            st.session_state.current_items = []
                            st.success("✅ Dhammaan xogtii si rasmi ah loogu xareeyey SQL Database!")
                            st.rerun()

    # ------------------------------------------------------------------------
    # PAGE: PAYMENT ENTRY
    # ------------------------------------------------------------------------
    elif menu == "Payment Entry":
        st.markdown("## 💳 Record Customer Payment (SQL)")
        with st.form("p_form", clear_on_submit=True):
            p_date = st.date_input("Payment Date", value=datetime.now())
            cust_name = st.text_input("Customer Name")
            amt = st.number_input("Amount Paid ($)", min_value=0.01, step=0.01)
            rcv = st.text_input("Received By")
            sub_p = st.form_submit_button("💾 Save Payment to SQL")

        if sub_p:
            if not cust_name.strip() or not rcv.strip(): st.error("Buuxi meelaha banaan!")
            else:
                conn = get_db_connection()
                if conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO sql_tico_payments (date, customer_name, amount_paid, received_by)
                            VALUES (%s, %s, %s, %s);
                        """, (str(p_date), cust_name.strip(), amt, rcv.strip()))
                    conn.commit()
                    conn.close()
                    st.success("✅ Payment-gii waa lagu guuleystay!")
                    st.rerun()

    # ------------------------------------------------------------------------
    # PAGE: CUSTOMER HISTORY (SQL QUERY)
    # ------------------------------------------------------------------------
    elif menu == "Customer History":
        st.markdown("## 🔍 Customer Purchase History (SQL Filtered)")
        if sales_df.empty: st.info("Xog kuma jirto database-ka.")
        else:
            all_customers = sorted(sales_df["customer_name"].unique())
            selected_cust = st.selectbox("👤 Dooro Macaamilka:", all_customers)
            
            if selected_cust:
                st.divider()
                cust_sales = sales_df[sales_df["customer_name"] == selected_cust].copy()
                cust_sales["date"] = cust_sales["date"].dt.strftime("%Y-%m-%d")
                
                st.dataframe(cust_sales[["date", "item_name", "quantity", "price", "discount", "total", "status"]].sort_values("date", ascending=False), use_container_width=True, hide_index=True)
                
                total_bought = cust_sales["total"].sum()
                total_invoice = cust_sales[cust_sales["status"] == "Invoice"]["total"].sum()
                total_cash = cust_sales[cust_sales["status"] == "Cash"]["total"].sum()
                
                total_paid = 0.0
                if not payments_df.empty:
                    cust_payments = payments_df[payments_df["customer_name"] == selected_cust].copy()
                    if not cust_payments.empty:
                        total_paid = cust_payments["amount_paid"].sum()
                        
                remaining_debt = total_invoice - total_paid
                
                c_box1, c_box2, c_box3, c_box4 = st.columns(4)
                with c_box1: st.metric("🛍️ Total Purchases", f"${total_bought:,.2f}")
                with c_box2: st.metric("💵 Cash Purchases", f"${total_cash:,.2f}")
                with c_box3: st.metric("🧾 Invoice Total", f"${total_invoice:,.2f}")
                with c_box4: st.metric("🔴 Remaining Debt", f"${remaining_debt:,.2f}")
