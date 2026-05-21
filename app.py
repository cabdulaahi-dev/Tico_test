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
        <div style='text-align:center; padding: 4rem 0 2rem 0;'>
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
    elif period == "Last Year":
        return df[df["date"].dt.year == (now.year - 1)]
    elif period.isdigit():
        return df[df["date"].dt.year == int(period)]
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
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("# 📊 TICO Wholesale Pro")
    with c2:
        badge = 'role-admin' if st.session_state.role == "admin" else 'role-viewer'
        label = '👤 ADMIN' if st.session_state.role == "admin" else '👁️ VIEWER'
        st.markdown(f'<br><span class="role-badge {badge}">{label}</span>', unsafe_allow_html=True)
    st.divider()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### ⚡ Navigation")
        if st.session_state.role == "admin":
            menu = st.radio("", [
                "🏠 Dashboard",
                "📝 Sales Entry",
                "💳 Payment Entry",
                "📥 Uruuris (No Invoice)",
                "─── Xog Daawo ───",
                "💵 Daawo: Cash Sales",
                "🧾 Daawo: Invoice Sales",
                "📦 Daawo: Uruuris",
                "💳 Daawo: Payments",
                "🔴 Lacagaha Maqan",
                "─── Analytics ───",
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

        current_year = datetime.now().year
        year_options = ["Last Year"] + [str(y) for y in range(current_year, 2019, -1)]
        quick_options = ["Today", "This Week", "This Month", "This Year"]
        all_options = year_options + ["─────────"] + quick_options

        raw_filter = st.selectbox(
            "Select Period:",
            options=all_options,
            index=0,
            key="period_filter"
        )
        # Ignore separator line
        if raw_filter == "─────────":
            time_filter = "Last Year"
        else:
            time_filter = raw_filter

        # ── Logout at the very bottom of sidebar ──────────────────────────
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.divider()
        role_label = "Admin" if st.session_state.role == "admin" else "Viewer"
        st.markdown(f'<p style="color:#4a7ab8;font-size:0.8rem;margin:0 0 0.5rem 0;">Logged in as: <b style="color:#90caf9">{role_label}</b></p>', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()

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
        st.markdown("## 📝 Geli Iib Cusub")

        # ── session state keys ───────────────────────────────────────────────
        for k, v in {
            "se_items":    [],   # basket items
            "se_type":     "Iib Caadi ah",
        }.items():
            if k not in st.session_state:
                st.session_state[k] = v

        tab_geli, tab_uur_view = st.tabs(["➕ Geli Iib", "📋 Daawo Iibka Uruuris"])

        # ════════════════════════════════════════════════════════════════════
        # TAB 1 — ENTRY FORM
        # ════════════════════════════════════════════════════════════════════
        with tab_geli:

            # ── Sale type selector ───────────────────────────────────────────
            st.markdown("#### 🔀 Nooca Iibka")
            sale_type = st.radio(
                "",
                ["🛒  Iib Caadi ah", "📦  Iib Uruuris ah"],
                horizontal=True,
                key="se_type_radio"
            )
            is_uuruuris = "Uruuris" in sale_type

            st.divider()

            # ── Header fields (differ by type) ──────────────────────────────
            if not is_uuruuris:
                # CAADI
                c1, c2, c3, c4 = st.columns(4)
                with c1: se_date    = st.date_input("📅 Taariikhda", value=datetime.now(), key="se_date_c")
                with c2: se_cust    = st.text_input("👤 Magaca Macaamilka", key="se_cust_c")
                with c3: se_status  = st.selectbox("💳 Lacag Bixinta", ["Cash", "Invoice"], key="se_status_c")
                with c4: se_inv     = st.text_input("📄 Lambarka Boonada", placeholder="INV-0001", key="se_inv_c")

            else:
                # URUURIS
                st.markdown("""
                <div style='background:#071a0e;border:1px solid #1b5e20;border-radius:8px;
                            padding:0.75rem 1.2rem;margin-bottom:1rem;'>
                    <span style='color:#69f0ae;font-size:0.85rem;'>
                        📦 <b>Iib Uruuris ah:</b> Alaabo badan waxaa lagu wada gariiri karaa
                        <b>hal lambar boono</b> iyo <b>hal magac uruuris</b>.
                        Lacag bixintu waxay si toos ah u noqotaa <b style="color:#ffca28;">CASH</b>.
                    </span>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1: se_date    = st.date_input("📅 Taariikhda", value=datetime.now(), key="se_date_u")
                with c2: se_inv     = st.text_input("📄 Lambarka Boonada *", placeholder="UUR-0001", key="se_inv_u")
                with c3: se_cust    = st.text_input("👥 Magaca Uruuriska *", placeholder="Xaafadda Hodan...", key="se_cust_u")
                se_status = "Cash"   # locked

                # Locked badge
                st.markdown("""
                <div style='display:inline-block;background:#0e1e35;border:1px solid #1e3050;
                            border-radius:6px;padding:0.4rem 1rem;margin:0.3rem 0 0.8rem 0;'>
                    <span style='color:#7090b8;font-size:0.8rem;'>💳 Lacag Bixinta:</span>
                    <b style='color:#69f0ae;margin-left:0.5rem;'>CASH</b>
                    <span style='color:#3a5a7a;font-size:0.75rem;margin-left:0.5rem;'>(si toos ah)</span>
                </div>
                """, unsafe_allow_html=True)

            # ── Item input row ───────────────────────────────────────────────
            st.markdown("#### ➕ Ku Dar Alaabta")
            ic1, ic2, ic3, ic4 = st.columns([2, 1, 1, 1])
            with ic1: se_iname  = st.text_input("Magaca Alaabta",  key="se_iname")
            with ic2: se_qty    = st.number_input("Qty", min_value=1, value=1, key="se_qty")
            with ic3: se_price  = st.number_input("Price ($)", min_value=0.0, value=0.0, key="se_price")
            with ic4: se_cost   = st.number_input("Cost ($)",  min_value=0.0, value=0.0, key="se_cost")
            se_disc = st.number_input("⚡ Discount ($)", min_value=0.0, value=0.0, key="se_disc")

            if st.button("➕ Ku Dar Dambiisha", use_container_width=True, key="se_add"):
                if not se_iname.strip():
                    st.error("⚠️ Geli magaca alaabta!")
                elif not se_cust.strip():
                    st.error("⚠️ Geli magaca macaamilka / uruuriska!")
                else:
                    tot = (se_qty * se_price) - se_disc
                    st.session_state.se_items.append({
                        "item_name":  se_iname.strip(),
                        "quantity":   se_qty,
                        "price":      se_price,
                        "cost_price": se_cost,
                        "discount":   se_disc,
                        "total":      tot,
                    })
                    st.success(f"✓  **{se_iname.strip()}** lagu daray dambiisha!")
                    st.rerun()

            # ── Basket preview ───────────────────────────────────────────────
            if st.session_state.se_items:
                st.divider()
                bdf = pd.DataFrame(st.session_state.se_items)
                st.dataframe(bdf, use_container_width=True, hide_index=True)

                grand = bdf["total"].sum()

                # Summary pill (Uruuris)
                if is_uuruuris:
                    inv_lbl  = se_inv.strip()  if "se_inv"  in dir() else "—"
                    cust_lbl = se_cust.strip() if "se_cust" in dir() else "—"
                    st.markdown(f"""
                    <div style='background:#0a1628;border:1px solid #1e3050;border-radius:8px;
                                padding:0.7rem 1.2rem;margin:0.4rem 0;display:flex;gap:2rem;flex-wrap:wrap;'>
                        <span style='color:#7090b8;font-size:0.85rem;'>
                            📄 Boono: <b style='color:#e8f0ff;'>{inv_lbl or "—"}</b>
                        </span>
                        <span style='color:#7090b8;font-size:0.85rem;'>
                            👥 Uruuris: <b style='color:#e8f0ff;'>{cust_lbl or "—"}</b>
                        </span>
                        <span style='color:#7090b8;font-size:0.85rem;'>
                            💰 Wadarta: <b style='color:#69f0ae;'>${grand:,.2f}</b>
                        </span>
                        <span style='color:#7090b8;font-size:0.85rem;'>
                            💳 <b style='color:#69f0ae;'>CASH</b>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"### 🏷️ Grand Total: **${grand:,.2f}**")

                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("🗑️ Nadiifi Dambiisha", use_container_width=True, key="se_clear"):
                        st.session_state.se_items = []
                        st.rerun()
                with bc2:
                    btn_label = "💾 Keydi Uruuris" if is_uuruuris else "💾 Keydi Iibka"
                    if st.button(btn_label, use_container_width=True, key="se_save"):
                        # Validation
                        err = None
                        if not se_cust.strip():
                            err = "⚠️ Geli magaca macaamilka!"
                        elif is_uuruuris and not se_inv.strip():
                            err = "⚠️ Uruuriska wuxuu u baahan yahay Lambarka Boonada!"
                        if err:
                            st.error(err)
                        else:
                            conn = get_db_connection()
                            if conn:
                                with conn.cursor() as cur:
                                    for item in st.session_state.se_items:
                                        cur.execute("""
                                            INSERT INTO sql_tico_sales
                                            (date, customer_name, item_name, quantity,
                                             price, cost_price, discount, total,
                                             status, invoice_number, sale_type)
                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                                        """, (
                                            str(se_date),
                                            se_cust.strip(),
                                            item["item_name"],
                                            item["quantity"],
                                            item["price"],
                                            item["cost_price"],
                                            item["discount"],
                                            item["total"],
                                            se_status,
                                            se_inv.strip() if se_inv.strip() else None,
                                            "Uruuris" if is_uuruuris else "Caadi",
                                        ))
                                conn.commit()
                                conn.close()
                                st.session_state.se_items = []
                                st.success("✅ Si guul leh ayaa loo keydsaday!")
                                st.rerun()

        # ════════════════════════════════════════════════════════════════════
        # TAB 2 — VIEW URUURIS  (Expander rows — qarsan ilaa la gujiyо)
        # ════════════════════════════════════════════════════════════════════
        with tab_uur_view:
            st.markdown("#### 📋 Iibka Uruuris — Loo Uruuriyey Boona & Macaamilka")
            st.caption("Gujiso safka si aad u aragto alaabihii — waa mid qarsan ilaa la garaaco.")

            # ── Pull Uruuris rows from DB ────────────────────────────────────
            uur_df = pd.DataFrame()
            if not sales_df.empty:
                if "sale_type" in sales_df.columns:
                    uur_df = sales_df[sales_df["sale_type"] == "Uruuris"].copy()
                else:
                    st.warning("""
                    ⚠️ Column-ka **sale_type** ma jiro database-ka weli. Ku run gareey SQL-kan:
                    ```sql
                    ALTER TABLE sql_tico_sales
                      ADD COLUMN IF NOT EXISTS sale_type    VARCHAR(50),
                      ADD COLUMN IF NOT EXISTS invoice_number VARCHAR(100);
                    ```
                    """)

            if uur_df.empty:
                st.info("📭 Wax iib Uruuris ah kuma jirto nidaamka.")
            else:
                uur_df["date"] = pd.to_datetime(uur_df["date"], errors="coerce")

                # ── Summary metrics ──────────────────────────────────────────
                u_rev  = uur_df["total"].sum()
                u_grp  = uur_df["customer_name"].nunique()
                u_inv  = uur_df["invoice_number"].nunique() if "invoice_number" in uur_df.columns else 0

                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(safe_metric("💰 Wadarta Dakhliga",  f"${u_rev:,.0f}", "metric-green"), unsafe_allow_html=True)
                with m2: st.markdown(safe_metric("👥 Uruurisyada",       f"{u_grp}",        "metric-gold"),  unsafe_allow_html=True)
                with m3: st.markdown(safe_metric("📄 Boonooyin",         f"{u_inv}"),                         unsafe_allow_html=True)

                st.divider()

                # ── Search bar ───────────────────────────────────────────────
                uu_q = st.text_input(
                    "🔍 Raadi Uruuris / Boono",
                    placeholder="Qor magaca uruuriska ama lambarka boonada...",
                    key="uu_search_v2"
                )
                if uu_q.strip():
                    m = (
                        uur_df["customer_name"].str.contains(uu_q.strip(), case=False, na=False) |
                        uur_df["invoice_number"].astype(str).str.contains(uu_q.strip(), case=False, na=False)
                    )
                    uur_df = uur_df[m]
                    if uur_df.empty:
                        st.info(f"🔍 '{uu_q}' lama helin.")

                # ── Build group index (invoice_number + customer_name) ───────
                grp_key = ["invoice_number", "customer_name"] \
                    if "invoice_number" in uur_df.columns else ["customer_name"]

                groups = (
                    uur_df.groupby(grp_key, dropna=False)
                    .agg(
                        Taariikh   = ("date",      "max"),
                        Alaabo     = ("item_name", "count"),
                        Qty_Guud   = ("quantity",  "sum"),
                        Lacag_Guud = ("total",     "sum"),
                    )
                    .reset_index()
                    .sort_values("Taariikh", ascending=False)
                )

                # ── One expander per group (collapsed by default) ────────────
                for _, row in groups.iterrows():
                    inv_no   = str(row.get("invoice_number") or "—")
                    cust_nm  = row["customer_name"]
                    n_lines  = int(row["Alaabo"])
                    qty_tot  = int(row["Qty_Guud"])
                    lac_tot  = row["Lacag_Guud"]
                    taarikh  = pd.to_datetime(row["Taariikh"]).strftime("%Y-%m-%d") \
                               if pd.notna(row["Taariikh"]) else "—"

                    exp_label = (
                        f"📄 {inv_no}   ·   "
                        f"👥 {cust_nm}   ·   "
                        f"📦 {n_lines} alaab   ·   "
                        f"Qty: {qty_tot}   ·   "
                        f"💰 ${lac_tot:,.2f}   ·   "
                        f"📅 {taarikh}"
                    )

                    with st.expander(exp_label, expanded=False):
                        # Filter exact detail rows
                        if "invoice_number" in uur_df.columns:
                            detail = uur_df[
                                (uur_df["invoice_number"].fillna("—").astype(str) == inv_no) &
                                (uur_df["customer_name"] == cust_nm)
                            ].copy()
                        else:
                            detail = uur_df[uur_df["customer_name"] == cust_nm].copy()

                        detail["date"] = detail["date"].dt.strftime("%Y-%m-%d")

                        show = [c for c in
                            ["id", "date", "item_name", "quantity",
                             "price", "discount", "total"]
                            if c in detail.columns]

                        st.dataframe(
                            detail[show].sort_values("date", ascending=False),
                            use_container_width=True,
                            hide_index=True
                        )

                        # Footer totals
                        st.markdown(f"""
                        <div style='background:#071428;border:1px solid #1e3050;border-radius:6px;
                                    padding:0.5rem 1rem;margin-top:0.4rem;display:flex;gap:2.5rem;'>
                            <span style='color:#7090b8;font-size:0.82rem;'>
                                Wadarta Qty:
                                <b style='color:#e8f0ff;'>{qty_tot}</b>
                            </span>
                            <span style='color:#7090b8;font-size:0.82rem;'>
                                Wadarta Lacag:
                                <b style='color:#69f0ae;'>${lac_tot:,.2f}</b>
                            </span>
                            <span style='color:#7090b8;font-size:0.82rem;'>
                                💳 <b style='color:#69f0ae;'>Cash</b>
                            </span>
                        </div>
                        """, unsafe_allow_html=True)



    # ========================================================================
    # PAGE: PAYMENT ENTRY
    # ========================================================================
    elif menu == "💳 Payment Entry":
        st.markdown("## 💳 Record Customer Payment")
        with st.form("p_form", clear_on_submit=True):
            col_p1, col_p2 = st.columns(2)
            with col_p1: p_date = st.date_input("Payment Date", value=datetime.now())
            with col_p2: p_invoice = st.text_input("📄 Invoice Number", placeholder="e.g. INV-0042")
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
                            INSERT INTO sql_tico_payments
                            (date, customer_name, amount_paid, received_by, invoice_number)
                            VALUES (%s, %s, %s, %s, %s);
                        """, (str(p_date), cust_name.strip(), amt, rcv.strip(),
                              p_invoice.strip() or None))
                    conn.commit()
                    conn.close()
                    st.success("✅ Payment si guul leh ayaa loo keydsaday!")
                    st.rerun()

    # ========================================================================
    # PAGE: URUURIS (NO INVOICE) ⭐ NEW
    # ========================================================================
    elif menu == "📥 Uruuris (No Invoice)":
        st.markdown("## 📥 Uruuris — Alaabta Aan Boona Lahayn")

        # ── Init session state for hold basket ──────────────────────────────
        if "hold_items" not in st.session_state:
            st.session_state.hold_items = []

        tab_geli, tab_daawo = st.tabs(["➕ Xog Geli", "📋 Daawo & Maamul"])

        # ════════════════════════════════════════════════════════════════════
        # TAB 1 — DATA ENTRY
        # ════════════════════════════════════════════════════════════════════
        with tab_geli:
            st.markdown("#### 📝 Geli Macluumaadka Uruuris")

            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                h_date = st.date_input("📅 Taariikhda", value=datetime.now(), key="h_date")
            with col_h2:
                h_invoice = st.text_input("📄 Lambarka Boonada / Reference", placeholder="e.g. REF-0099", key="h_inv")
            with col_h3:
                h_customer = st.text_input("👤 Magaca Macaamilka", placeholder="Customer name...", key="h_cust")

            st.divider()
            st.markdown("#### 📦 Geli Alaabta")

            col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
            with col_i1:
                h_item = st.text_input("Magaca Alaabta", placeholder="Item name...", key="h_item")
            with col_i2:
                h_qty = st.number_input("Tirada (Qty)", min_value=1, value=1, key="h_qty")
            with col_i3:
                h_note = st.text_input("Xusuusin (Optional)", placeholder="Note...", key="h_note")

            if st.button("➕ Ku Dar Dambiisha", use_container_width=True, key="h_add"):
                if not h_item.strip():
                    st.error("⚠️ Geli magaca alaabta!")
                elif not h_customer.strip():
                    st.error("⚠️ Geli magaca macaamilka!")
                else:
                    st.session_state.hold_items.append({
                        "date": str(h_date),
                        "invoice_number": h_invoice.strip() or None,
                        "customer_name": h_customer.strip(),
                        "item_name": h_item.strip(),
                        "quantity": h_qty,
                        "note": h_note.strip() or None,
                    })
                    st.success(f"✓ **{h_item.strip()}** lagu daray dambiisha!")
                    st.rerun()

            # Show current basket
            if st.session_state.hold_items:
                st.divider()
                st.markdown("##### 🧺 Dambiisha Hadda (Pending)")
                basket_df = pd.DataFrame(st.session_state.hold_items)
                st.dataframe(basket_df, use_container_width=True, hide_index=True)
                st.markdown(f"**Wadarta Alaabta:** `{len(st.session_state.hold_items)}` safaf")

                col_sb1, col_sb2 = st.columns(2)
                with col_sb1:
                    if st.button("🗑️ Nadiifi Dambiisha", use_container_width=True, key="h_clear"):
                        st.session_state.hold_items = []
                        st.rerun()
                with col_sb2:
                    if st.button("💾 Keydi Database-ka", use_container_width=True, key="h_save"):
                        conn = get_db_connection()
                        if conn:
                            saved = 0
                            errors = 0
                            with conn.cursor() as cur:
                                # Create table if not exists
                                cur.execute("""
                                    CREATE TABLE IF NOT EXISTS sql_tico_hold_items (
                                        id SERIAL PRIMARY KEY,
                                        date DATE,
                                        invoice_number VARCHAR(100),
                                        customer_name VARCHAR(255) NOT NULL,
                                        item_name VARCHAR(255) NOT NULL,
                                        quantity INTEGER NOT NULL DEFAULT 1,
                                        note TEXT,
                                        created_at TIMESTAMP DEFAULT NOW()
                                    );
                                """)
                                for row in st.session_state.hold_items:
                                    try:
                                        cur.execute("""
                                            INSERT INTO sql_tico_hold_items
                                            (date, invoice_number, customer_name, item_name, quantity, note)
                                            VALUES (%s, %s, %s, %s, %s, %s);
                                        """, (row["date"], row["invoice_number"],
                                              row["customer_name"], row["item_name"],
                                              row["quantity"], row["note"]))
                                        saved += 1
                                    except Exception:
                                        errors += 1
                            conn.commit()
                            conn.close()
                            st.session_state.hold_items = []
                            if errors == 0:
                                st.success(f"✅ {saved} safaf si guul leh ayaa loo keydsaday!")
                            else:
                                st.warning(f"⚠️ {saved} ayaa la keydsaday, {errors} cilad baa jirtay.")
                            st.rerun()

        # ════════════════════════════════════════════════════════════════════
        # TAB 2 — VIEW & MANAGE (QuickBooks drill-down, no single-customer search)
        # ════════════════════════════════════════════════════════════════════
        with tab_daawo:
            st.markdown("#### 📋 Dhamaan Uruurista — Loo Uruuriyey Macaamilka")
            st.caption("👇 Gujiso macaamilka si aad u aragto alaabihiisa maalin maalin ah")

            # Load hold items from DB
            hold_df = pd.DataFrame()
            conn = get_db_connection()
            if conn:
                try:
                    hold_df = pd.read_sql_query(
                        "SELECT * FROM sql_tico_hold_items ORDER BY date DESC, customer_name ASC",
                        conn
                    )
                except Exception:
                    st.info("📭 Jadwalka sql_tico_hold_items wali lama abuuri. Geli xog marka hore.")
                finally:
                    conn.close()

            if hold_df.empty:
                st.info("📭 Wax xog ah kuma jirto uruurista hadda.")
            else:
                hold_df["date"] = pd.to_datetime(hold_df["date"], errors="coerce")

                # ── Summary metrics ──────────────────────────────────────────
                total_rows  = len(hold_df)
                total_custs = hold_df["customer_name"].nunique()
                total_items = hold_df["quantity"].sum()

                sm1, sm2, sm3 = st.columns(3)
                with sm1: st.markdown(safe_metric("📋 Wadarta Safafa", f"{total_rows:,}"),                          unsafe_allow_html=True)
                with sm2: st.markdown(safe_metric("👥 Macaamiisha",    f"{total_custs:,}", "metric-gold"),           unsafe_allow_html=True)
                with sm3: st.markdown(safe_metric("📦 Wadarta Qty",    f"{int(total_items):,}", "metric-green"),     unsafe_allow_html=True)

                st.divider()

                # ── QuickBooks drill-down: grouped by customer → daily ───────
                cust_totals = (
                    hold_df.groupby("customer_name")["quantity"]
                    .sum().reset_index()
                    .sort_values("quantity", ascending=False)
                )

                for _, crow in cust_totals.iterrows():
                    cust      = crow["customer_name"]
                    total_qty = int(crow["quantity"])
                    cust_df   = hold_df[hold_df["customer_name"] == cust].copy()
                    n_rows    = len(cust_df)
                    inv_list  = cust_df["invoice_number"].dropna().unique()
                    inv_label = ", ".join(inv_list) if len(inv_list) > 0 else "—"

                    with st.expander(
                        f"👤  **{cust}**"
                        f"　　　📦 {n_rows} item{'s' if n_rows>1 else ''}"
                        f"　　　Qty: {total_qty}"
                        f"　　　Ref: {inv_label}",
                        expanded=False
                    ):
                        # Daily grouping
                        dates = sorted(cust_df["date"].dt.date.unique(), reverse=True)

                        for d in dates:
                            day_df = cust_df[cust_df["date"].dt.date == d].copy()
                            day_df["date"] = day_df["date"].dt.strftime("%Y-%m-%d")
                            day_qty = int(day_df["quantity"].sum())

                            st.markdown(f"""
                            <div style='background:#071428;border-left:3px solid #1565c0;
                                        border-radius:0 6px 6px 0;padding:0.4rem 1rem;
                                        margin:0.6rem 0 0.3rem 0;display:flex;
                                        justify-content:space-between;align-items:center;'>
                                <span style='color:#90caf9;font-weight:600;font-size:0.9rem;'>
                                    📅 {d.strftime("%A, %d %B %Y")}
                                </span>
                                <span style='color:#ffca28;font-family:monospace;font-size:0.85rem;'>
                                    📦 {day_qty} items
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                            show_cols = [c for c in
                                ["id","date","invoice_number","item_name","quantity","note"]
                                if c in day_df.columns]
                            st.dataframe(
                                day_df[show_cols].reset_index(drop=True),
                                use_container_width=True,
                                hide_index=True,
                            )

                        # Footer + delete (admin only)
                        st.markdown(f"""
                        <div style='background:#0a1e35;border:1px solid #1e3050;border-radius:6px;
                                    padding:0.5rem 1rem;margin-top:0.5rem;display:flex;gap:3rem;'>
                            <span style='color:#7090b8;font-size:0.82rem;'>
                                Items: <b style='color:#e8f0ff;'>{n_rows}</b>
                            </span>
                            <span style='color:#7090b8;font-size:0.82rem;'>
                                Wadarta Qty: <b style='color:#ffca28;'>{total_qty}</b>
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.session_state.role == "admin":
                            st.markdown("---")
                            dc1, dc2 = st.columns([2, 1])
                            with dc1:
                                del_id = st.selectbox(
                                    "🗑️ Dooro ID aad tirtireyso:",
                                    options=cust_df["id"].tolist(),
                                    key=f"hold_del_id_{cust}"
                                )
                            with dc2:
                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("❌ Tirtir", key=f"hold_del_btn_{cust}",
                                             use_container_width=True):
                                    conn2 = get_db_connection()
                                    if conn2:
                                        with conn2.cursor() as cur:
                                            cur.execute(
                                                "DELETE FROM sql_tico_hold_items WHERE id=%s;",
                                                (int(del_id),)
                                            )
                                        conn2.commit()
                                        conn2.close()
                                        st.success(f"🗑️ ID {del_id} waa la tirtiray!")
                                        st.rerun()


    # ========================================================================
    # HELPER — QuickBooks drill-down renderer
    # ========================================================================
    def qb_customer_list(df, label_col, total_col, extra_cols=None,
                         date_col="date", section_key="qb"):
        """
        Renders a two-level QuickBooks-style list:
        Level 1 → customer rows (collapsed, show total)
        Level 2 → daily grouped detail table (expanded on click)
        extra_cols: additional columns to show in the detail table
        """
        if df.empty:
            st.info("📭 Wax xog ah kuma jirto.")
            return

        # Build customer summary
        cust_totals = (
            df.groupby(label_col)[total_col]
            .sum()
            .reset_index()
            .sort_values(total_col, ascending=False)
        )

        for i, crow in cust_totals.iterrows():
            cust      = crow[label_col]
            cust_tot  = crow[total_col]
            cust_df   = df[df[label_col] == cust].copy()
            n_rows    = len(cust_df)

            exp_header = (
                f"👤  **{cust}**"
                f"　　　📦 {n_rows} transaction{'s' if n_rows>1 else ''}"
                f"　　　💰 **${cust_tot:,.2f}**"
            )

            with st.expander(exp_header, expanded=False):
                # ── Daily grouping ───────────────────────────────────────────
                cust_df[date_col] = pd.to_datetime(cust_df[date_col], errors="coerce")
                dates = sorted(cust_df[date_col].dt.date.unique(), reverse=True)

                for d in dates:
                    day_df = cust_df[cust_df[date_col].dt.date == d].copy()
                    day_df[date_col] = day_df[date_col].dt.strftime("%Y-%m-%d")
                    day_total = day_df[total_col].sum() if total_col in day_df.columns else 0

                    # Date header bar
                    st.markdown(f"""
                    <div style='background:#071428;border-left:3px solid #1565c0;
                                border-radius:0 6px 6px 0;padding:0.4rem 1rem;
                                margin:0.6rem 0 0.3rem 0;display:flex;
                                justify-content:space-between;align-items:center;'>
                        <span style='color:#90caf9;font-weight:600;font-size:0.9rem;'>
                            📅 {d.strftime("%A, %d %B %Y")}
                        </span>
                        <span style='color:#69f0ae;font-family:monospace;font-size:0.85rem;'>
                            ${day_total:,.2f}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    base_cols = [c for c in
                        ["id","item_name","quantity","price","cost_price",
                         "discount","total","status","invoice_number","sale_type"]
                        if c in day_df.columns]
                    if extra_cols:
                        base_cols += [c for c in extra_cols
                                      if c in day_df.columns and c not in base_cols]

                    st.dataframe(
                        day_df[base_cols].reset_index(drop=True),
                        use_container_width=True,
                        hide_index=True,
                    )

                # Customer footer
                st.markdown(f"""
                <div style='background:#0a1e35;border:1px solid #1e3050;border-radius:6px;
                            padding:0.5rem 1rem;margin-top:0.5rem;display:flex;gap:3rem;'>
                    <span style='color:#7090b8;font-size:0.82rem;'>
                        Transactions: <b style='color:#e8f0ff;'>{n_rows}</b>
                    </span>
                    <span style='color:#7090b8;font-size:0.82rem;'>
                        Total: <b style='color:#69f0ae;'>${cust_tot:,.2f}</b>
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # ========================================================================
    # PAGE: DAAWO — CASH SALES
    # ========================================================================
    if menu == "💵 Daawo: Cash Sales":
        st.markdown(f"## 💵 Cash Sales — *{time_filter}*")

        if filtered_sales.empty or "status" not in filtered_sales.columns:
            st.info("📭 Wax xog ah kuma jirto.")
        else:
            cash_df = filtered_sales[filtered_sales["status"] == "Cash"].copy()
            if cash_df.empty:
                st.info("📭 Cash iib ah kuma jirto mudadan.")
            else:
                rev   = cash_df["total"].sum()
                prof  = cash_df["item_profit"].sum() if "item_profit" in cash_df.columns else 0
                n_cust = cash_df["customer_name"].nunique()

                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(safe_metric("💰 Cash Revenue", f"${rev:,.2f}", "metric-green"), unsafe_allow_html=True)
                with m2: st.markdown(safe_metric("📈 Net Profit",   f"${prof:,.2f}", "metric-green"), unsafe_allow_html=True)
                with m3: st.markdown(safe_metric("👥 Customers",    f"{n_cust}",     "metric-gold"),  unsafe_allow_html=True)

                st.divider()
                st.caption("👇 Gujiso macaamilka si aad u aragto faahfaahinta maalin maalin ah")
                qb_customer_list(cash_df, "customer_name", "total", section_key="cash")

    # ========================================================================
    # PAGE: DAAWO — INVOICE SALES
    # ========================================================================
    elif menu == "🧾 Daawo: Invoice Sales":
        st.markdown(f"## 🧾 Invoice Sales — *{time_filter}*")

        if filtered_sales.empty or "status" not in filtered_sales.columns:
            st.info("📭 Wax xog ah kuma jirto.")
        else:
            inv_df = filtered_sales[filtered_sales["status"] == "Invoice"].copy()
            if inv_df.empty:
                st.info("📭 Invoice iib ah kuma jirto mudadan.")
            else:
                # Merge payments to show balance
                paid_map = {}
                if not payments_df.empty:
                    paid_map = payments_df.groupby("customer_name")["amount_paid"].sum().to_dict()

                inv_total  = inv_df["total"].sum()
                total_paid = sum(paid_map.get(c, 0) for c in inv_df["customer_name"].unique())
                balance    = max(0, inv_total - total_paid)
                n_cust     = inv_df["customer_name"].nunique()

                m1, m2, m3, m4 = st.columns(4)
                with m1: st.markdown(safe_metric("🧾 Invoice Total", f"${inv_total:,.2f}"),                        unsafe_allow_html=True)
                with m2: st.markdown(safe_metric("✅ Lacag Bixiyey", f"${total_paid:,.2f}", "metric-green"),        unsafe_allow_html=True)
                with m3: st.markdown(safe_metric("🔴 Balance Due",   f"${balance:,.2f}",    "metric-red"),           unsafe_allow_html=True)
                with m4: st.markdown(safe_metric("👥 Customers",     f"{n_cust}",            "metric-gold"),          unsafe_allow_html=True)

                st.divider()
                st.caption("👇 Gujiso macaamilka si aad u aragto faahfaahinta maalin maalin ah")
                qb_customer_list(inv_df, "customer_name", "total", section_key="inv")

    # ========================================================================
    # PAGE: DAAWO — URUURIS
    # ========================================================================
    elif menu == "📦 Daawo: Uruuris":
        st.markdown(f"## 📦 Uruuris Sales — *{time_filter}*")

        uur_view_df = pd.DataFrame()
        if not filtered_sales.empty and "sale_type" in filtered_sales.columns:
            uur_view_df = filtered_sales[filtered_sales["sale_type"] == "Uruuris"].copy()

        if uur_view_df.empty:
            st.info("📭 Wax iib Uruuris ah kuma jirto mudadan.")
        else:
            rev    = uur_view_df["total"].sum()
            n_inv  = uur_view_df["invoice_number"].nunique() if "invoice_number" in uur_view_df.columns else 0
            n_cust = uur_view_df["customer_name"].nunique()

            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(safe_metric("💰 Wadarta Dakhliga", f"${rev:,.2f}", "metric-green"), unsafe_allow_html=True)
            with m2: st.markdown(safe_metric("📄 Boonooyin",        f"{n_inv}",      "metric-gold"),  unsafe_allow_html=True)
            with m3: st.markdown(safe_metric("👥 Uruurisyada",      f"{n_cust}",     "metric-gold"),  unsafe_allow_html=True)

            st.divider()
            st.caption("👇 Gujiso uruuriska si aad u aragto alaabihii maalin maalin ah")

            # Group by invoice_number + customer_name as the "customer" unit
            if "invoice_number" in uur_view_df.columns:
                uur_view_df["uur_label"] = (
                    uur_view_df["invoice_number"].fillna("—").astype(str)
                    + "  ·  "
                    + uur_view_df["customer_name"]
                )
                qb_customer_list(uur_view_df, "uur_label", "total", section_key="uur")
            else:
                qb_customer_list(uur_view_df, "customer_name", "total", section_key="uur")

    # ========================================================================
    # PAGE: DAAWO — PAYMENTS
    # ========================================================================
    elif menu == "💳 Daawo: Payments":
        st.markdown(f"## 💳 Payments — *{time_filter}*")

        pay_view = filter_by_period(payments_df, time_filter) if not payments_df.empty else pd.DataFrame()

        if pay_view.empty:
            st.info("📭 Wax lacag bixin ah kuma jirto mudadan.")
        else:
            tot_paid  = pay_view["amount_paid"].sum()
            n_cust    = pay_view["customer_name"].nunique()
            n_txn     = len(pay_view)

            m1, m2, m3 = st.columns(3)
            with m1: st.markdown(safe_metric("✅ Lacag La Helay",  f"${tot_paid:,.2f}", "metric-green"), unsafe_allow_html=True)
            with m2: st.markdown(safe_metric("👥 Macaamiisha",     f"{n_cust}",          "metric-gold"),  unsafe_allow_html=True)
            with m3: st.markdown(safe_metric("🧾 Transactions",    f"{n_txn}",            "metric-gold"),  unsafe_allow_html=True)

            st.divider()
            st.caption("👇 Gujiso macaamilka si aad u aragto lacag bixintii maalin maalin ah")

            # Payments drill-down (reuse helper with amount_paid as total col)
            pay_view2 = pay_view.copy()
            if "date" in pay_view2.columns:
                pay_view2["date"] = pd.to_datetime(pay_view2["date"], errors="coerce")

            # Custom expander (payments have different columns)
            cust_totals = (
                pay_view2.groupby("customer_name")["amount_paid"]
                .sum().reset_index()
                .sort_values("amount_paid", ascending=False)
            )

            for _, crow in cust_totals.iterrows():
                cust     = crow["customer_name"]
                cust_tot = crow["amount_paid"]
                cdf      = pay_view2[pay_view2["customer_name"] == cust].copy()
                n_rows   = len(cdf)

                with st.expander(
                    f"👤  **{cust}**　　　🧾 {n_rows} payment{'s' if n_rows>1 else ''}"
                    f"　　　✅ **${cust_tot:,.2f}**",
                    expanded=False
                ):
                    dates = sorted(cdf["date"].dt.date.unique(), reverse=True)
                    for d in dates:
                        day_df = cdf[cdf["date"].dt.date == d].copy()
                        day_df["date"] = day_df["date"].dt.strftime("%Y-%m-%d")
                        day_tot = day_df["amount_paid"].sum()

                        st.markdown(f"""
                        <div style='background:#071428;border-left:3px solid #43a047;
                                    border-radius:0 6px 6px 0;padding:0.4rem 1rem;
                                    margin:0.6rem 0 0.3rem 0;display:flex;
                                    justify-content:space-between;align-items:center;'>
                            <span style='color:#90caf9;font-weight:600;font-size:0.9rem;'>
                                📅 {d.strftime("%A, %d %B %Y")}
                            </span>
                            <span style='color:#69f0ae;font-family:monospace;font-size:0.85rem;'>
                                ✅ ${day_tot:,.2f}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                        show = [c for c in
                            ["id","date","amount_paid","received_by","invoice_number"]
                            if c in day_df.columns]
                        st.dataframe(day_df[show].reset_index(drop=True),
                                     use_container_width=True, hide_index=True)

                    st.markdown(f"""
                    <div style='background:#0a1e35;border:1px solid #1e3050;border-radius:6px;
                                padding:0.5rem 1rem;margin-top:0.5rem;'>
                        <span style='color:#7090b8;font-size:0.82rem;'>
                            Wadarta Lacagta La Helay:
                            <b style='color:#69f0ae;'>${cust_tot:,.2f}</b>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    # ========================================================================
    # PAGE: LACAGAHA MAQAN (ACCOUNTS RECEIVABLE)
    # ========================================================================
    elif menu == "🔴 Lacagaha Maqan":
        st.markdown(f"## 🔴 Lacagaha Maqan — Accounts Receivable")
        st.caption("Macaamiisha leh deyn furan oo aan lacagta wali bixin")

        if sales_df.empty:
            st.info("📭 Wax xog ah kuma jirto.")
        else:
            # All invoice sales (not filtered by period — show all outstanding)
            inv_all = sales_df[sales_df["status"] == "Invoice"].copy() if "status" in sales_df.columns else pd.DataFrame()

            if inv_all.empty:
                st.success("✅ Wax deyn furan ah kuma jirto nidaamka!")
            else:
                # Build per-customer balance
                inv_summary = inv_all.groupby("customer_name")["total"].sum().reset_index()
                inv_summary.columns = ["customer_name", "Invoice_Total"]

                if not payments_df.empty:
                    pay_sum = payments_df.groupby("customer_name")["amount_paid"].sum().reset_index()
                    pay_sum.columns = ["customer_name", "Total_Paid"]
                    inv_summary = inv_summary.merge(pay_sum, on="customer_name", how="left")
                    inv_summary["Total_Paid"] = inv_summary["Total_Paid"].fillna(0)
                else:
                    inv_summary["Total_Paid"] = 0

                inv_summary["Balance_Due"] = (
                    inv_summary["Invoice_Total"] - inv_summary["Total_Paid"]
                ).clip(lower=0)

                # Only customers with outstanding balance
                ar_df = inv_summary[inv_summary["Balance_Due"] > 0].sort_values(
                    "Balance_Due", ascending=False
                )

                if ar_df.empty:
                    st.success("✅ Dhamaan macaamiisha ayaa lacagtooda bixiyey!")
                else:
                    total_ar   = ar_df["Balance_Due"].sum()
                    total_inv  = ar_df["Invoice_Total"].sum()
                    total_paid = ar_df["Total_Paid"].sum()
                    n_cust     = len(ar_df)

                    m1, m2, m3, m4 = st.columns(4)
                    with m1: st.markdown(safe_metric("🔴 Wadarta Deynta",  f"${total_ar:,.2f}",   "metric-red"),   unsafe_allow_html=True)
                    with m2: st.markdown(safe_metric("🧾 Invoice Guud",    f"${total_inv:,.2f}"),                   unsafe_allow_html=True)
                    with m3: st.markdown(safe_metric("✅ La Bixiyey",      f"${total_paid:,.2f}", "metric-green"),  unsafe_allow_html=True)
                    with m4: st.markdown(safe_metric("👥 Macaamiisha",     f"{n_cust}",            "metric-gold"),   unsafe_allow_html=True)

                    st.divider()
                    st.caption("👇 Gujiso macaamilka si aad u aragto alaabihii deynta ku ah — loo uruuriyey maalin maalin ah")

                    for _, arow in ar_df.iterrows():
                        cust      = arow["customer_name"]
                        bal       = arow["Balance_Due"]
                        inv_tot   = arow["Invoice_Total"]
                        paid_tot  = arow["Total_Paid"]

                        # Severity color
                        if bal > 1000:
                            sev_color = "#ff5252"
                            sev_icon  = "🔴"
                        elif bal > 300:
                            sev_color = "#ffca28"
                            sev_icon  = "🟡"
                        else:
                            sev_color = "#ff8a65"
                            sev_icon  = "🟠"

                        with st.expander(
                            f"{sev_icon}  **{cust}**"
                            f"　　　Invoice: ${inv_tot:,.2f}"
                            f"　　　La Bixiyey: ${paid_tot:,.2f}"
                            f"　　　**Balance Due: ${bal:,.2f}**",
                            expanded=False
                        ):
                            cust_inv_df = inv_all[inv_all["customer_name"] == cust].copy()
                            cust_inv_df["date"] = pd.to_datetime(
                                cust_inv_df["date"], errors="coerce"
                            )
                            dates = sorted(
                                cust_inv_df["date"].dt.date.unique(), reverse=True
                            )

                            for d in dates:
                                day_df = cust_inv_df[
                                    cust_inv_df["date"].dt.date == d
                                ].copy()
                                day_df["date"] = day_df["date"].dt.strftime("%Y-%m-%d")
                                day_tot = day_df["total"].sum()

                                st.markdown(f"""
                                <div style='background:#1a0808;border-left:3px solid {sev_color};
                                            border-radius:0 6px 6px 0;padding:0.4rem 1rem;
                                            margin:0.6rem 0 0.3rem 0;display:flex;
                                            justify-content:space-between;align-items:center;'>
                                    <span style='color:#90caf9;font-weight:600;font-size:0.9rem;'>
                                        📅 {d.strftime("%A, %d %B %Y")}
                                    </span>
                                    <span style='color:{sev_color};font-family:monospace;font-size:0.85rem;'>
                                        🔴 ${day_tot:,.2f}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)

                                show = [c for c in
                                    ["id","date","item_name","quantity",
                                     "price","discount","total","invoice_number"]
                                    if c in day_df.columns]
                                st.dataframe(
                                    day_df[show].reset_index(drop=True),
                                    use_container_width=True,
                                    hide_index=True,
                                )

                            # Payment history for this customer
                            if not payments_df.empty:
                                cust_pays = payments_df[
                                    payments_df["customer_name"] == cust
                                ].copy()
                                if not cust_pays.empty:
                                    cust_pays["date"] = pd.to_datetime(
                                        cust_pays["date"], errors="coerce"
                                    ).dt.strftime("%Y-%m-%d")
                                    st.markdown("##### ✅ Lacag Bixintii")
                                    pay_show = [c for c in
                                        ["id","date","amount_paid",
                                         "received_by","invoice_number"]
                                        if c in cust_pays.columns]
                                    st.dataframe(
                                        cust_pays[pay_show].reset_index(drop=True),
                                        use_container_width=True,
                                        hide_index=True,
                                    )

                            # Balance footer
                            st.markdown(f"""
                            <div style='background:#1a0808;border:1px solid {sev_color};
                                        border-radius:6px;padding:0.6rem 1.2rem;
                                        margin-top:0.6rem;display:flex;gap:3rem;'>
                                <span style='color:#7090b8;font-size:0.82rem;'>
                                    Invoice Total: <b style='color:#e8f0ff;'>${inv_tot:,.2f}</b>
                                </span>
                                <span style='color:#7090b8;font-size:0.82rem;'>
                                    La Bixiyey: <b style='color:#69f0ae;'>${paid_tot:,.2f}</b>
                                </span>
                                <span style='color:#7090b8;font-size:0.82rem;'>
                                    Balance Due: <b style='color:{sev_color};'>${bal:,.2f}</b>
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

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
