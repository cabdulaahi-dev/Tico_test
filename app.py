import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import io
import base64

# ============================================================================
# PAGE CONFIG & SETUP
# ============================================================================
st.set_page_config(
    page_title="TICO Wholesale Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

for key, default in {
    "authenticated": False,
    "role": None,
    "current_items": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# DATABASE CONNECTION
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

def load_data():
    sales_df = pd.DataFrame()
    payments_df = pd.DataFrame()
    conn = get_db_connection()
    if conn:
        try:
            sales_df = pd.read_sql_query("SELECT * FROM sql_tico_sales ORDER BY id DESC", conn)
            payments_df = pd.read_sql_query("SELECT * FROM sql_tico_payments ORDER BY id DESC", conn)
        except Exception as e:
            st.warning(f"Xogta lama soo kicin karin: {e}")
        finally:
            conn.close()
    if not sales_df.empty:
        sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")
        sales_df["item_profit"] = sales_df["total"] - (sales_df["quantity"] * sales_df["cost_price"])
    if not payments_df.empty:
        payments_df["date"] = pd.to_datetime(payments_df["date"], errors="coerce")
    return sales_df, payments_df

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }
code, .mono { font-family: 'JetBrains Mono', monospace; }

.stApp { background: #060d1a; }

section[data-testid="stSidebar"] {
    background: #0a1628 !important;
    border-right: 1px solid #1a2840;
}
section[data-testid="stSidebar"] * { color: #c8d8f0 !important; }

h1, h2, h3, h4, h5 { color: #e8f0ff !important; letter-spacing: -0.02em; }

.stTextInput input, .stSelectbox select, .stNumberInput input,
div[data-baseweb="select"] > div {
    background: #0e1e35 !important;
    color: #c8d8f0 !important;
    border: 1px solid #1e3050 !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1976d2, #1565c0) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(21,101,192,0.4) !important;
}

.metric-card {
    background: linear-gradient(135deg, #0e1e35, #0a1628);
    border: 1px solid #1e3050;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.5rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1565c0, #42a5f5);
}
.metric-label { font-size: 0.75rem; color: #7090b8; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: #e8f0ff; font-family: 'JetBrains Mono', monospace; }
.metric-sub { font-size: 0.8rem; color: #4a7ab8; margin-top: 0.2rem; }

.metric-green::before { background: linear-gradient(90deg, #1b5e20, #43a047); }
.metric-green .metric-value { color: #69f0ae; }
.metric-red::before { background: linear-gradient(90deg, #b71c1c, #ef5350); }
.metric-red .metric-value { color: #ff5252; }
.metric-gold::before { background: linear-gradient(90deg, #e65100, #ffa726); }
.metric-gold .metric-value { color: #ffca28; }

.section-header {
    background: linear-gradient(135deg, #0e1e35, #091525);
    border: 1px solid #1e3050;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    border-left: 4px solid #1565c0;
}
.section-header h3 { margin: 0 !important; color: #90caf9 !important; font-size: 1rem; }

.customer-rank-card {
    background: #0e1e35;
    border: 1px solid #1e3050;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.rank-badge {
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: white;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    flex-shrink: 0;
}
.rank-1 { background: linear-gradient(135deg, #f9a825, #e65100) !important; }
.rank-2 { background: linear-gradient(135deg, #78909c, #546e7a) !important; }
.rank-3 { background: linear-gradient(135deg, #8d6e63, #5d4037) !important; }

.pl-profit {
    background: linear-gradient(135deg, #0a2310, #0d2d14);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    border: 1px solid #1b5e20;
    border-left: 5px solid #43a047;
}
.pl-loss {
    background: linear-gradient(135deg, #1c0a0a, #2d1010);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    border: 1px solid #b71c1c;
    border-left: 5px solid #ef5350;
}

.report-box {
    background: #0e1e35;
    border: 1px solid #1e3050;
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
}

.role-badge {
    display: inline-block; padding: 0.3rem 1rem;
    border-radius: 20px; font-size: 0.8rem; font-weight: 600;
    letter-spacing: 0.05em;
}
.role-admin { background: linear-gradient(135deg, #b71c1c, #c62828); color: white; }
.role-viewer { background: linear-gradient(135deg, #e65100, #f57c00); color: white; }

div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

.stDataFrame { background: #0e1e35 !important; }

.stTabs [data-baseweb="tab-list"] { background: #0a1628; border-radius: 8px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #7090b8; border-radius: 6px; }
.stTabs [aria-selected="true"] { background: #1565c0 !important; color: white !important; }

.alert-warning {
    background: linear-gradient(135deg, #1a1500, #2d2200);
    border: 1px solid #f9a825;
    border-radius: 8px;
    padding: 1rem;
    color: #ffca28;
    margin: 0.5rem 0;
}
.alert-danger {
    background: linear-gradient(135deg, #1a0000, #2d0000);
    border: 1px solid #ef5350;
    border-radius: 8px;
    padding: 1rem;
    color: #ff5252;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOGIN
# ============================================================================
def check_password():
    if not st.session_state.authenticated:
        st.markdown("""
        <div style='text-align: center; padding: 4rem 0 2rem 0;'>
            <div style='font-size:3rem;'>📊</div>
            <h1 style='color:#e8f0ff; font-size:2.5rem; font-weight:700; margin:0.5rem 0;'>TICO Wholesale Pro</h1>
            <p style='color:#4a7ab8; font-size:1rem;'>Advanced Analytics & Business Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown('<div style="background:#0e1e35;border:1px solid #1e3050;border-radius:12px;padding:2rem;">', unsafe_allow_html=True)
            st.markdown("#### 🔐 Secure Login")
            password = st.text_input("Enter Password", type="password", key="pwd_input", placeholder="Enter your password...")
            if st.button("🚀 Unlock Access", use_container_width=True):
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
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def filter_by_period(df, period):
    if df.empty:
        return df
    now = datetime.now().date()
    if period == "Today":
        return df[df["date"].dt.date == now]
    elif period == "This Week":
        start = now - timedelta(days=now.weekday())
        return df[df["date"].dt.date >= start]
    elif period == "This Month":
        return df[(df["date"].dt.year == now.year) & (df["date"].dt.month == now.month)]
    elif period == "This Year":
        return df[df["date"].dt.year == now.year]
    return df

def safe_metric(label, value, css_class=""):
    return f"""
    <div class="metric-card {css_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

def plotly_theme():
    return dict(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(14,30,53,0.8)',
        font=dict(color='#c8d8f0', family='Space Grotesk'),
        xaxis=dict(gridcolor='#1e3050', linecolor='#1e3050'),
        yaxis=dict(gridcolor='#1e3050', linecolor='#1e3050'),
    )

# ============================================================================
# MAIN APP
# ============================================================================
if check_password():
    sales_df, payments_df = load_data()

    # --- Header ---
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        st.markdown("# 📊 TICO Wholesale Pro")
    with c2:
        badge = 'role-admin' if st.session_state.role == "admin" else 'role-viewer'
        label = '👤 ADMIN' if st.session_state.role == "admin" else '👁️ VIEWER'
        st.markdown(f'<br><span class="role-badge {badge}">{label}</span>', unsafe_allow_html=True)
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()
    st.divider()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### ⚡ Navigation")
        if st.session_state.role == "admin":
            menu = st.radio("", [
                "🏠 Dashboard",
                "📝 Sales Entry",
                "💳 Payment Entry",
                "👥 Customer Analytics",
                "📦 Product Analytics",
                "📈 Time Analytics",
                "🧾 Profit & Loss",
                "📋 Reports & Export",
                "⚙️ Data Management",
            ])
        else:
            menu = st.radio("", [
                "🏠 Dashboard",
                "👥 Customer Analytics",
                "📦 Product Analytics",
                "📈 Time Analytics",
                "🧾 Profit & Loss",
                "📋 Reports & Export",
            ])

        st.divider()
        st.markdown("### 🕒 Period Filter")
        time_filter = st.radio("", ["All Time", "Today", "This Week", "This Month", "This Year"])

    filtered_sales = filter_by_period(sales_df, time_filter)

    # ========================================================================
    # PAGE: DASHBOARD
    # ========================================================================
    if menu == "🏠 Dashboard":
        st.markdown(f"## 🏠 Business Overview — *{time_filter}*")

        rev = filtered_sales["total"].sum() if not filtered_sales.empty else 0
        cost = (filtered_sales["quantity"] * filtered_sales["cost_price"]).sum() if not filtered_sales.empty else 0
        profit = rev - cost
        txn_count = len(filtered_sales) if not filtered_sales.empty else 0
        unique_customers = filtered_sales["customer_name"].nunique() if not filtered_sales.empty else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: st.markdown(safe_metric("💰 Revenue", f"${rev:,.0f}"), unsafe_allow_html=True)
        with c2: st.markdown(safe_metric("📈 Net Profit", f"${profit:,.0f}", "metric-green" if profit >= 0 else "metric-red"), unsafe_allow_html=True)
        with c3: st.markdown(safe_metric("💸 Total Cost", f"${cost:,.0f}"), unsafe_allow_html=True)
        with c4: st.markdown(safe_metric("🧾 Transactions", f"{txn_count:,}", "metric-gold"), unsafe_allow_html=True)
        with c5: st.markdown(safe_metric("👥 Customers", f"{unique_customers:,}", "metric-gold"), unsafe_allow_html=True)

        if not filtered_sales.empty:
            st.divider()
            col_ch1, col_ch2 = st.columns(2)

            # Revenue trend by date
            with col_ch1:
                daily = filtered_sales.groupby(filtered_sales["date"].dt.date).agg(
                    Revenue=("total", "sum"),
                    Profit=("item_profit", "sum")
                ).reset_index()
                daily.columns = ["Date", "Revenue", "Profit"]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Revenue"], name="Revenue",
                    fill='tozeroy', line=dict(color='#42a5f5', width=2),
                    fillcolor='rgba(66,165,245,0.15)'))
                fig.add_trace(go.Scatter(x=daily["Date"], y=daily["Profit"], name="Profit",
                    line=dict(color='#69f0ae', width=2, dash='dot')))
                fig.update_layout(**plotly_theme(), title="📈 Revenue & Profit Trend",
                    title_font_color='#90caf9', height=300, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig, use_container_width=True)

            # Top items pie
            with col_ch2:
                item_rev = filtered_sales.groupby("item_name")["total"].sum().nlargest(8).reset_index()
                fig2 = px.pie(item_rev, names="item_name", values="total",
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                    title="📦 Revenue by Item")
                fig2.update_layout(**plotly_theme(), height=300, margin=dict(l=0,r=0,t=40,b=0))
                fig2.update_traces(textfont_color='white')
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 📋 Recent Transactions")
            disp = filtered_sales.head(20).copy()
            disp["date"] = disp["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(
                disp[["id","date","customer_name","item_name","quantity","price","discount","total","status"]],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("📭 Wax xog ah kuma jirto waqtigan la doortay.")

    # ========================================================================
    # PAGE: SALES ENTRY
    # ========================================================================
    elif menu == "📝 Sales Entry":
        st.markdown("## 📝 Record New Sale")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: s_date = st.date_input("Date", value=datetime.now())
        with col_m2: c_name = st.text_input("Customer Name")
        with col_m3: status = st.selectbox("Payment Status", ["Cash", "Invoice"])

        st.divider()
        st.markdown("#### ➕ Add Items to Basket")
        col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1, 1, 1])
        with col_i1: i_name = st.text_input("Item Name", key="i_txt")
        with col_i2: qty = st.number_input("Quantity", min_value=1, value=1, key="i_qty")
        with col_i3: price = st.number_input("Price ($)", min_value=0.00, value=0.00, key="i_prc")
        with col_i4: c_price = st.number_input("Cost Price ($)", min_value=0.00, value=0.00, key="i_cst")
        discount = st.number_input("⚡ Discount ($)", min_value=0.00, value=0.00)

        if st.button("➕ Add Item to Basket", use_container_width=True):
            if not i_name.strip():
                st.error("Geli magaca badeecada!")
            else:
                tot = (qty * price) - discount
                st.session_state.current_items.append({
                    "item_name": i_name.strip(), "quantity": qty, "price": price,
                    "cost_price": c_price, "discount": discount, "total": tot
                })
                st.success(f"✓ {i_name} lagu daray dambiisha!")
                st.rerun()

        if st.session_state.current_items:
            st.divider()
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
                if st.button("💾 Save Transaction to SQL"):
                    if not c_name.strip():
                        st.error("Qor magaca macaamilka!")
                    else:
                        conn = get_db_connection()
                        if conn:
                            with conn.cursor() as cur:
                                for item in st.session_state.current_items:
                                    cur.execute("""
                                        INSERT INTO sql_tico_sales 
                                        (date, customer_name, item_name, quantity, price, cost_price, discount, total, status)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                                    """, (str(s_date), c_name.strip(), item["item_name"],
                                          item["quantity"], item["price"], item["cost_price"],
                                          item["discount"], item["total"], status))
                            conn.commit()
                            conn.close()
                            st.session_state.current_items = []
                            st.success("✅ Si guul leh loogu xareeyey SQL Database!")
                            st.rerun()

    # ========================================================================
    # PAGE: PAYMENT ENTRY
    # ========================================================================
    elif menu == "💳 Payment Entry":
        st.markdown("## 💳 Record Customer Payment")
        with st.form("p_form", clear_on_submit=True):
            p_date = st.date_input("Payment Date", value=datetime.now())
            cust_name = st.text_input("Customer Name")
            amt = st.number_input("Amount Paid ($)", min_value=0.01, step=0.01)
            rcv = st.text_input("Received By")
            sub_p = st.form_submit_button("💾 Save Payment to SQL")
        if sub_p:
            if not cust_name.strip() or not rcv.strip():
                st.error("Buuxi meelaha banaan!")
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
                    st.success("✅ Payment si guul leh ayaa loo keydsaday!")
                    st.rerun()

    # ========================================================================
    # PAGE: CUSTOMER ANALYTICS ⭐ NEW
    # ========================================================================
    elif menu == "👥 Customer Analytics":
        st.markdown(f"## 👥 Customer Analytics — *{time_filter}*")

        if filtered_sales.empty:
            st.info("📭 Wax xog ah kuma jirto waqtigan.")
        else:
            # Build customer summary
            cust_summary = filtered_sales.groupby("customer_name").agg(
                Total_Revenue=("total", "sum"),
                Total_Profit=("item_profit", "sum"),
                Transactions=("id", "count"),
                Total_Qty=("quantity", "sum"),
            ).reset_index()

            # Merge payments
            if not payments_df.empty:
                pay_summary = payments_df.groupby("customer_name")["amount_paid"].sum().reset_index()
                pay_summary.columns = ["customer_name", "Total_Paid"]
                cust_summary = cust_summary.merge(pay_summary, on="customer_name", how="left")
                cust_summary["Total_Paid"] = cust_summary["Total_Paid"].fillna(0)
            else:
                cust_summary["Total_Paid"] = 0

            invoice_totals = filtered_sales[filtered_sales["status"] == "Invoice"].groupby("customer_name")["total"].sum().reset_index()
            invoice_totals.columns = ["customer_name", "Invoice_Total"]
            cust_summary = cust_summary.merge(invoice_totals, on="customer_name", how="left")
            cust_summary["Invoice_Total"] = cust_summary["Invoice_Total"].fillna(0)
            cust_summary["Remaining_Debt"] = (cust_summary["Invoice_Total"] - cust_summary["Total_Paid"]).clip(lower=0)
            cust_summary = cust_summary.sort_values("Total_Revenue", ascending=False)

            tab1, tab2, tab3 = st.tabs(["🏆 Top Customers", "📉 Low Customers", "🔍 Customer Detail"])

            with tab1:
                st.markdown('<div class="section-header"><h3>🏆 Top Performing Customers (by Revenue)</h3></div>', unsafe_allow_html=True)
                top_n = min(10, len(cust_summary))
                top_customers = cust_summary.head(top_n)

                for i, row in enumerate(top_customers.itertuples(), 1):
                    rank_class = f"rank-{i}" if i <= 3 else ""
                    medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"#{i}"
                    debt_warn = f' <span style="color:#ff5252;">⚠️ Debt: ${row.Remaining_Debt:,.0f}</span>' if row.Remaining_Debt > 0 else ""
                    st.markdown(f"""
                    <div class="customer-rank-card">
                        <div class="rank-badge {rank_class}">{medal}</div>
                        <div style="flex:1">
                            <div style="color:#e8f0ff;font-weight:600;font-size:1rem;">{row.customer_name}</div>
                            <div style="color:#7090b8;font-size:0.8rem;">{row.Transactions} transactions · {row.Total_Qty:.0f} items{debt_warn}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="color:#42a5f5;font-weight:700;font-family:monospace;">${row.Total_Revenue:,.0f}</div>
                            <div style="color:#69f0ae;font-size:0.8rem;">Profit: ${row.Total_Profit:,.0f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()
                fig = px.bar(
                    top_customers, x="customer_name", y="Total_Revenue",
                    color="Total_Profit",
                    color_continuous_scale=["#1565c0","#42a5f5","#69f0ae"],
                    title="Top Customers — Revenue vs Profit",
                    labels={"customer_name":"Customer","Total_Revenue":"Revenue ($)","Total_Profit":"Profit ($)"}
                )
                fig.update_layout(**plotly_theme(), height=350, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.markdown('<div class="section-header"><h3>📉 Low Activity / Inactive Customers</h3></div>', unsafe_allow_html=True)
                bottom_customers = cust_summary.tail(min(10, len(cust_summary))).sort_values("Total_Revenue")

                for i, row in enumerate(bottom_customers.itertuples(), 1):
                    alert_class = "alert-danger" if row.Total_Revenue < 100 else "alert-warning"
                    st.markdown(f"""
                    <div class="{alert_class}" style="display:flex;justify-content:space-between;align-items:center;margin:0.3rem 0;">
                        <div>
                            <span style="font-weight:600">{row.customer_name}</span>
                            <span style="font-size:0.8rem;margin-left:1rem;">{row.Transactions} transactions</span>
                        </div>
                        <div style="font-family:monospace;font-weight:700">${row.Total_Revenue:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 📊 All Customers by Revenue")
                fig2 = px.bar(
                    cust_summary.sort_values("Total_Revenue"),
                    x="Total_Revenue", y="customer_name",
                    orientation='h',
                    color="Total_Revenue",
                    color_continuous_scale=["#b71c1c","#ef5350","#42a5f5","#69f0ae"],
                    title="Customer Revenue Ranking",
                )
                fig2.update_layout(**plotly_theme(), height=max(300, len(cust_summary)*35),
                                   margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                st.markdown("#### 🔍 Individual Customer Deep Dive")
                sel_cust = st.selectbox("👤 Select Customer:", sorted(sales_df["customer_name"].unique()))
                if sel_cust:
                    cust_sales = sales_df[sales_df["customer_name"] == sel_cust].copy()

                    r = cust_sales["total"].sum()
                    c_cost = (cust_sales["quantity"] * cust_sales["cost_price"]).sum()
                    p = r - c_cost
                    inv_total = cust_sales[cust_sales["status"] == "Invoice"]["total"].sum()
                    paid = payments_df[payments_df["customer_name"] == sel_cust]["amount_paid"].sum() if not payments_df.empty else 0
                    debt = max(0, inv_total - paid)

                    cols = st.columns(4)
                    with cols[0]: st.markdown(safe_metric("Total Revenue", f"${r:,.0f}"), unsafe_allow_html=True)
                    with cols[1]: st.markdown(safe_metric("Net Profit", f"${p:,.0f}", "metric-green"), unsafe_allow_html=True)
                    with cols[2]: st.markdown(safe_metric("Invoice Total", f"${inv_total:,.0f}"), unsafe_allow_html=True)
                    with cols[3]: st.markdown(safe_metric("Remaining Debt", f"${debt:,.0f}", "metric-red" if debt > 0 else ""), unsafe_allow_html=True)

                    st.divider()
                    cust_sales_disp = cust_sales.copy()
                    cust_sales_disp["date"] = cust_sales_disp["date"].dt.strftime("%Y-%m-%d")
                    st.dataframe(
                        cust_sales_disp[["date","item_name","quantity","price","discount","total","status"]].sort_values("date", ascending=False),
                        use_container_width=True, hide_index=True
                    )

    # ========================================================================
    # PAGE: PRODUCT ANALYTICS ⭐ NEW
    # ========================================================================
    elif menu == "📦 Product Analytics":
        st.markdown(f"## 📦 Product Analytics — *{time_filter}*")

        if filtered_sales.empty:
            st.info("📭 Wax xog ah kuma jirto waqtigan.")
        else:
            prod_summary = filtered_sales.groupby("item_name").agg(
                Qty_Sold=("quantity", "sum"),
                Revenue=("total", "sum"),
                Profit=("item_profit", "sum"),
                Transactions=("id", "count"),
                Avg_Price=("price", "mean"),
            ).reset_index()
            prod_summary["Profit_Margin"] = ((prod_summary["Profit"] / prod_summary["Revenue"]) * 100).round(1)
            prod_summary = prod_summary.sort_values("Qty_Sold", ascending=False)

            tab1, tab2, tab3 = st.tabs(["🔥 Best Sellers", "🥶 Slow Movers", "📊 Full Analysis"])

            with tab1:
                st.markdown('<div class="section-header"><h3>🔥 Best Selling Products</h3></div>', unsafe_allow_html=True)
                top_prod = prod_summary.head(10)
                for i, row in enumerate(top_prod.itertuples(), 1):
                    rank_class = f"rank-{i}" if i <= 3 else ""
                    medal = ["🥇","🥈","🥉"][i-1] if i <= 3 else f"#{i}"
                    st.markdown(f"""
                    <div class="customer-rank-card">
                        <div class="rank-badge {rank_class}">{medal}</div>
                        <div style="flex:1">
                            <div style="color:#e8f0ff;font-weight:600">{row.item_name}</div>
                            <div style="color:#7090b8;font-size:0.8rem;">{row.Transactions} orders · Avg price ${row.Avg_Price:.2f}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="color:#ffca28;font-weight:700;font-family:monospace;">{row.Qty_Sold:.0f} units</div>
                            <div style="color:#69f0ae;font-size:0.8rem;">Margin: {row.Profit_Margin:.1f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    fig = px.bar(top_prod, x="item_name", y="Qty_Sold",
                        color="Revenue", color_continuous_scale=["#1565c0","#42a5f5"],
                        title="Top Products — Units Sold")
                    fig.update_layout(**plotly_theme(), height=320, margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fig, use_container_width=True)
                with col_p2:
                    fig2 = px.bar(top_prod, x="item_name", y="Profit_Margin",
                        color="Profit_Margin", color_continuous_scale=["#b71c1c","#ffca28","#69f0ae"],
                        title="Profit Margin % by Product")
                    fig2.update_layout(**plotly_theme(), height=320, margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fig2, use_container_width=True)

            with tab2:
                st.markdown('<div class="section-header"><h3>🥶 Slow Moving Products — Need Attention</h3></div>', unsafe_allow_html=True)
                slow = prod_summary.tail(10).sort_values("Qty_Sold")
                for row in slow.itertuples():
                    alert = "alert-danger" if row.Qty_Sold <= 5 else "alert-warning"
                    st.markdown(f"""
                    <div class="{alert}" style="display:flex;justify-content:space-between;align-items:center;margin:0.3rem 0;">
                        <div>
                            <span style="font-weight:600">{row.item_name}</span>
                            <span style="font-size:0.8rem;margin-left:1rem;">Margin: {row.Profit_Margin:.1f}%</span>
                        </div>
                        <div style="font-family:monospace;font-weight:700">{row.Qty_Sold:.0f} units sold</div>
                    </div>
                    """, unsafe_allow_html=True)

                fig3 = px.scatter(prod_summary, x="Qty_Sold", y="Profit_Margin",
                    size="Revenue", color="Revenue", hover_name="item_name",
                    color_continuous_scale=["#b71c1c","#1565c0","#69f0ae"],
                    title="Products: Volume vs Profit Margin (bubble = revenue)")
                fig3.update_layout(**plotly_theme(), height=380, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig3, use_container_width=True)

            with tab3:
                st.markdown("#### 📊 Complete Product Summary Table")
                display_prod = prod_summary.copy()
                display_prod.columns = ["Item Name","Qty Sold","Revenue ($)","Profit ($)","Orders","Avg Price ($)","Margin %"]
                st.dataframe(display_prod, use_container_width=True, hide_index=True)

    # ========================================================================
    # PAGE: TIME ANALYTICS ⭐ NEW
    # ========================================================================
    elif menu == "📈 Time Analytics":
        st.markdown("## 📈 Time-Based Sales Analytics")

        if sales_df.empty:
            st.info("📭 Xog kuma jirto nidaamka.")
        else:
            tab_day, tab_week, tab_month, tab_year = st.tabs(["📅 Per Day", "📆 Per Week", "🗓️ Per Month", "📊 Per Year"])

            def build_time_chart(group_df, title, x_label):
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                    subplot_titles=["Revenue & Profit", "Transaction Count"])
                fig.add_trace(go.Bar(x=group_df[x_label], y=group_df["Revenue"],
                    name="Revenue", marker_color='#1565c0'), row=1, col=1)
                fig.add_trace(go.Scatter(x=group_df[x_label], y=group_df["Profit"],
                    name="Profit", line=dict(color='#69f0ae', width=2)), row=1, col=1)
                fig.add_trace(go.Bar(x=group_df[x_label], y=group_df["Transactions"],
                    name="Transactions", marker_color='#42a5f5'), row=2, col=1)
                fig.update_layout(**plotly_theme(), title=title, height=500,
                    margin=dict(l=0,r=0,t=60,b=0))
                return fig

            with tab_day:
                df_day = sales_df.copy()
                df_day["Day"] = df_day["date"].dt.date
                grp = df_day.groupby("Day").agg(
                    Revenue=("total","sum"), Profit=("item_profit","sum"),
                    Transactions=("id","count")).reset_index()
                grp["Day"] = grp["Day"].astype(str)
                fig = build_time_chart(grp, "Daily Sales Performance", "Day")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(grp, use_container_width=True, hide_index=True)

            with tab_week:
                df_week = sales_df.copy()
                df_week["Week"] = df_week["date"].dt.to_period("W").astype(str)
                grp = df_week.groupby("Week").agg(
                    Revenue=("total","sum"), Profit=("item_profit","sum"),
                    Transactions=("id","count")).reset_index()
                fig = build_time_chart(grp, "Weekly Sales Performance", "Week")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(grp, use_container_width=True, hide_index=True)

            with tab_month:
                df_month = sales_df.copy()
                df_month["Month"] = df_month["date"].dt.to_period("M").astype(str)
                grp = df_month.groupby("Month").agg(
                    Revenue=("total","sum"), Profit=("item_profit","sum"),
                    Transactions=("id","count")).reset_index()
                fig = build_time_chart(grp, "Monthly Sales Performance", "Month")
                st.plotly_chart(fig, use_container_width=True)

                # Month-over-month growth
                if len(grp) >= 2:
                    grp["Revenue_Growth"] = grp["Revenue"].pct_change() * 100
                    st.markdown("#### 📊 Month-over-Month Growth")
                    fig2 = px.bar(grp.dropna(), x="Month", y="Revenue_Growth",
                        color="Revenue_Growth",
                        color_continuous_scale=["#b71c1c","#ffca28","#69f0ae"],
                        title="Revenue Growth % (MoM)")
                    fig2.update_layout(**plotly_theme(), height=280, margin=dict(l=0,r=0,t=40,b=0))
                    st.plotly_chart(fig2, use_container_width=True)

                st.dataframe(grp, use_container_width=True, hide_index=True)

            with tab_year:
                df_year = sales_df.copy()
                df_year["Year"] = df_year["date"].dt.year.astype(str)
                grp = df_year.groupby("Year").agg(
                    Revenue=("total","sum"), Profit=("item_profit","sum"),
                    Transactions=("id","count"), Customers=("customer_name","nunique")).reset_index()
                fig = build_time_chart(grp, "Yearly Sales Performance", "Year")
                st.plotly_chart(fig, use_container_width=True)

                c1, c2, c3 = st.columns(3)
                for i, row in enumerate(grp.itertuples()):
                    col = [c1, c2, c3][i % 3]
                    with col:
                        st.markdown(safe_metric(f"📅 {row.Year}", f"${row.Revenue:,.0f}", "metric-gold"), unsafe_allow_html=True)

    # ========================================================================
    # PAGE: PROFIT & LOSS
    # ========================================================================
    elif menu == "🧾 Profit & Loss":
        st.markdown(f"## 🧾 Profit & Loss Statement — *{time_filter}*")

        if filtered_sales.empty:
            st.info("📭 Wax xog ah kuma jirto mudadan.")
        else:
            total_revenue = filtered_sales["total"].sum()
            total_discount = filtered_sales["discount"].sum()
            gross_revenue = total_revenue + total_discount
            total_cogs = (filtered_sales["quantity"] * filtered_sales["cost_price"]).sum()
            gross_profit = total_revenue - total_cogs
            gp_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

            if gross_profit >= 0:
                st.markdown(f"""
                <div class="pl-profit">
                    <h3 style="margin:0;color:#fff;">🎉 GANACSIGU WUXUU KU JIRAA FAA'IIDO</h3>
                    <p style="margin:8px 0 0;font-size:1.3rem;color:#c8e6c9;">Net Profit: <b style="font-family:monospace;">${gross_profit:,.2f}</b> &nbsp;·&nbsp; Margin: <b>{gp_margin:.1f}%</b></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="pl-loss">
                    <h3 style="margin:0;color:#fff;">⚠️ GANACSIGU WUXUU KU JIRAA KHASAARO</h3>
                    <p style="margin:8px 0 0;font-size:1.3rem;color:#ffcdd2;">Net Loss: <b style="font-family:monospace;">${abs(gross_profit):,.2f}</b></p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_pl1, col_pl2 = st.columns(2)
            with col_pl1:
                st.markdown("#### 📊 P&L Summary Table")
                pl_data = {
                    "Account": [
                        "Gross Sales (Before Discount)",
                        "Total Discounts Given",
                        "Net Revenue",
                        "Cost of Goods Sold (COGS)",
                        "─────────────────────",
                        "GROSS PROFIT / LOSS",
                        "Profit Margin %",
                    ],
                    "Amount ($)": [
                        f"${gross_revenue:,.2f}",
                        f"- ${total_discount:,.2f}",
                        f"${total_revenue:,.2f}",
                        f"- ${total_cogs:,.2f}",
                        "──────────",
                        f"${gross_profit:,.2f}",
                        f"{gp_margin:.1f}%",
                    ]
                }
                st.table(pd.DataFrame(pl_data))

            with col_pl2:
                st.markdown("#### 📦 Profit by Product")
                item_pl = filtered_sales.groupby("item_name").agg(
                    Revenue=("total","sum"),
                    COGS=("quantity","sum"),
                    Profit=("item_profit","sum")
                ).reset_index().sort_values("Profit", ascending=False)
                fig = px.bar(item_pl, x="item_name", y="Profit",
                    color="Profit",
                    color_continuous_scale=["#b71c1c","#1565c0","#69f0ae"],
                    title="Profit per Product")
                fig.update_layout(**plotly_theme(), height=320, margin=dict(l=0,r=0,t=40,b=0))
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown("#### 🧾 P&L by Customer")
            cust_pl = filtered_sales.groupby("customer_name").agg(
                Revenue=("total","sum"),
                Profit=("item_profit","sum"),
                Transactions=("id","count")
            ).reset_index()
            cust_pl["Margin%"] = (cust_pl["Profit"]/cust_pl["Revenue"]*100).round(1)
            cust_pl = cust_pl.sort_values("Profit", ascending=False)
            st.dataframe(cust_pl, use_container_width=True, hide_index=True)

    # ========================================================================
    # PAGE: REPORTS & EXPORT ⭐ NEW
    # ========================================================================
    elif menu == "📋 Reports & Export":
        st.markdown("## 📋 Reports & Export")

        if filtered_sales.empty:
            st.info("📭 Wax xog ah kuma jirto mudadan.")
        else:
            report_type = st.selectbox("📄 Select Report Type:", [
                "Sales Summary Report",
                "Customer Report",
                "Product Performance Report",
                "Profit & Loss Report",
                "Debt & Payments Report",
            ])

            st.divider()

            if report_type == "Sales Summary Report":
                df_report = filtered_sales.copy()
                df_report["date"] = df_report["date"].dt.strftime("%Y-%m-%d")
                summary = {
                    "Total Revenue": f"${df_report['total'].sum():,.2f}",
                    "Total Transactions": str(len(df_report)),
                    "Total Items Sold": str(int(df_report['quantity'].sum())),
                    "Total Discounts": f"${df_report['discount'].sum():,.2f}",
                    "Unique Customers": str(df_report['customer_name'].nunique()),
                }
                st.markdown('<div class="report-box">', unsafe_allow_html=True)
                st.markdown(f"### 📊 Sales Summary Report — {time_filter}")
                cols = st.columns(len(summary))
                for col, (k, v) in zip(cols, summary.items()):
                    with col:
                        st.markdown(safe_metric(k, v), unsafe_allow_html=True)
                st.markdown("#### Transaction Details")
                st.dataframe(df_report[["id","date","customer_name","item_name","quantity","price","discount","total","status"]], use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
                excel_data = to_excel_bytes(df_report)
                st.download_button("📥 Export to Excel", data=excel_data,
                    file_name=f"TICO_Sales_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            elif report_type == "Customer Report":
                cust_rep = filtered_sales.groupby("customer_name").agg(
                    Total_Revenue=("total","sum"),
                    Total_Profit=("item_profit","sum"),
                    Transactions=("id","count"),
                    Total_Qty=("quantity","sum"),
                ).reset_index()
                if not payments_df.empty:
                    pay = payments_df.groupby("customer_name")["amount_paid"].sum().reset_index()
                    pay.columns = ["customer_name","Total_Paid"]
                    cust_rep = cust_rep.merge(pay, on="customer_name", how="left")
                    cust_rep["Total_Paid"] = cust_rep["Total_Paid"].fillna(0)
                else:
                    cust_rep["Total_Paid"] = 0
                inv = filtered_sales[filtered_sales["status"]=="Invoice"].groupby("customer_name")["total"].sum().reset_index()
                inv.columns = ["customer_name","Invoice_Total"]
                cust_rep = cust_rep.merge(inv, on="customer_name", how="left")
                cust_rep["Invoice_Total"] = cust_rep["Invoice_Total"].fillna(0)
                cust_rep["Remaining_Debt"] = (cust_rep["Invoice_Total"] - cust_rep["Total_Paid"]).clip(lower=0)
                cust_rep = cust_rep.sort_values("Total_Revenue", ascending=False)
                st.markdown(f"### 👥 Customer Report — {time_filter}")
                st.dataframe(cust_rep, use_container_width=True, hide_index=True)
                excel_data = to_excel_bytes(cust_rep)
                st.download_button("📥 Export Customers to Excel", data=excel_data,
                    file_name=f"TICO_Customer_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            elif report_type == "Product Performance Report":
                prod_rep = filtered_sales.groupby("item_name").agg(
                    Qty_Sold=("quantity","sum"),
                    Revenue=("total","sum"),
                    COGS=("cost_price","sum"),
                    Profit=("item_profit","sum"),
                    Orders=("id","count"),
                ).reset_index()
                prod_rep["Margin%"] = (prod_rep["Profit"]/prod_rep["Revenue"]*100).round(1)
                prod_rep = prod_rep.sort_values("Qty_Sold", ascending=False)
                st.markdown(f"### 📦 Product Performance Report — {time_filter}")
                st.dataframe(prod_rep, use_container_width=True, hide_index=True)
                excel_data = to_excel_bytes(prod_rep)
                st.download_button("📥 Export Products to Excel", data=excel_data,
                    file_name=f"TICO_Product_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            elif report_type == "Profit & Loss Report":
                total_rev = filtered_sales["total"].sum()
                total_disc = filtered_sales["discount"].sum()
                gross_rev = total_rev + total_disc
                total_cogs = (filtered_sales["quantity"] * filtered_sales["cost_price"]).sum()
                net_profit = total_rev - total_cogs
                margin = (net_profit / total_rev * 100) if total_rev > 0 else 0

                pl_rep = pd.DataFrame({
                    "Account": ["Gross Sales","Total Discounts","Net Revenue","COGS","Net Profit/Loss","Profit Margin %"],
                    "Amount": [gross_rev, -total_disc, total_rev, -total_cogs, net_profit, margin],
                    "Formatted": [f"${gross_rev:,.2f}", f"-${total_disc:,.2f}", f"${total_rev:,.2f}",
                                  f"-${total_cogs:,.2f}", f"${net_profit:,.2f}", f"{margin:.1f}%"]
                })
                st.markdown(f"### 🧾 Profit & Loss Report — {time_filter}")
                st.table(pl_rep[["Account","Formatted"]])
                excel_data = to_excel_bytes(pl_rep[["Account","Formatted"]])
                st.download_button("📥 Export P&L to Excel", data=excel_data,
                    file_name=f"TICO_PL_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            elif report_type == "Debt & Payments Report":
                if payments_df.empty:
                    st.info("Wax lacag bixin ah kuma jirto nidaamka.")
                else:
                    inv_sales = sales_df[sales_df["status"] == "Invoice"].groupby("customer_name")["total"].sum().reset_index()
                    inv_sales.columns = ["customer_name", "Invoice_Total"]
                    pay_sum = payments_df.groupby("customer_name")["amount_paid"].sum().reset_index()
                    pay_sum.columns = ["customer_name", "Total_Paid"]
                    debt_rep = inv_sales.merge(pay_sum, on="customer_name", how="left")
                    debt_rep["Total_Paid"] = debt_rep["Total_Paid"].fillna(0)
                    debt_rep["Remaining_Debt"] = (debt_rep["Invoice_Total"] - debt_rep["Total_Paid"]).clip(lower=0)
                    debt_rep = debt_rep.sort_values("Remaining_Debt", ascending=False)
                    total_debt = debt_rep["Remaining_Debt"].sum()
                    st.markdown(f"### 💳 Debt & Payments Report")
                    st.markdown(safe_metric("🔴 Total Outstanding Debt", f"${total_debt:,.2f}", "metric-red"), unsafe_allow_html=True)
                    st.dataframe(debt_rep, use_container_width=True, hide_index=True)
                    excel_data = to_excel_bytes(debt_rep)
                    st.download_button("📥 Export Debt Report to Excel", data=excel_data,
                        file_name=f"TICO_Debt_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.divider()
            st.markdown("### 🖨️ Print Report")
            st.markdown("""
            <div style="background:#0e1e35;border:1px solid #1e3050;border-radius:10px;padding:1rem 1.5rem;">
                <p style="color:#7090b8;margin:0;">Adigoo rabtid inaad daabicho warbixinta:</p>
                <ol style="color:#c8d8f0;margin:0.5rem 0 0 0;">
                    <li>Browser-ka riix <b>Ctrl+P</b> (Windows) ama <b>Cmd+P</b> (Mac)</li>
                    <li>Dooro <b>"Save as PDF"</b> haddaad PDF u baahan tahay</li>
                    <li>Ama riix badhanka <b>Export to Excel</b> kor ku yaala</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

    # ========================================================================
    # PAGE: DATA MANAGEMENT
    # ========================================================================
    elif menu == "⚙️ Data Management":
        st.markdown("## ⚙️ Data Management")

        if sales_df.empty:
            st.info("Database-ka hadda wax xog ah kuma jiraan.")
        else:
            manage_df = sales_df.copy()
            manage_df["date"] = manage_df["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(manage_df.sort_values("id", ascending=False), use_container_width=True, hide_index=True)
            st.divider()

            options_id = sorted(sales_df["id"].tolist(), reverse=True)
            selected_id = st.selectbox("🎯 Dooro ID-ga:", options_id)
            row_data = sales_df[sales_df["id"] == selected_id].iloc[0]
            st.markdown(f"**Customer:** {row_data['customer_name']} &nbsp;|&nbsp; **Item:** {row_data['item_name']}")

            col_e1, col_e2, col_e3 = st.columns(3)
            with col_e1: edit_qty = st.number_input("Quantity", min_value=1, value=int(row_data["quantity"]))
            with col_e2: edit_price = st.number_input("Price ($)", min_value=0.00, value=float(row_data["price"]))
            with col_e3: edit_disc = st.number_input("Discount ($)", min_value=0.00, value=float(row_data["discount"]))

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔄 Update SQL Record", use_container_width=True):
                    new_total = (edit_qty * edit_price) - edit_disc
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE sql_tico_sales
                                SET quantity=%s, price=%s, discount=%s, total=%s
                                WHERE id=%s;
                            """, (edit_qty, edit_price, edit_disc, new_total, int(selected_id)))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ ID {selected_id} si guul leh ayaa loo cusboonaysiiyey!")
                        st.rerun()
            with col_btn2:
                if st.button("❌ Delete from SQL", use_container_width=True):
                    conn = get_db_connection()
                    if conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM sql_tico_sales WHERE id=%s;", (int(selected_id),))
                        conn.commit()
                        conn.close()
                        st.error(f"🗑️ ID {selected_id} waa la tirtiray!")
                        st.rerun()
