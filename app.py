import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ============================================================================
# PAGE CONFIG & SETUP
# ============================================================================
st.set_page_config(
    page_title="TICO Wholesale Core",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        h1, h2, h3 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
        }
        .metric-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #252d3d 100%);
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .metric-label {
            color: #b0b8c1;
            font-size: 0.875rem;
            text-transform: uppercase;
        }
        .metric-value {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 700;
        }
        .stTextInput input,
        .stSelectbox select,
        .stNumberInput input {
            background-color: #151b27 !important;
            color: #ffffff !important;
            border: 1px solid #2d3748 !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #1f77b4 0%, #1557a0 100%);
            color: white;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            width: 100%;
        }
        .role-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .role-admin { background-color: #d62728; color: white; }
        .role-viewer { background-color: #ff7f0e; color: white; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOGIN SYSTEM
# ============================================================================
def check_password():
    if not st.session_state.authenticated:
        st.markdown(
            "<div style='text-align: center; padding: 2rem 0;'>"
            "<h1>TICO Wholesale Core</h1>"
            "<p style='color: #b0b8c1;'>Sales & Profit Analytics Platform</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Login Required")
            password = st.text_input("Enter Password", type="password", key="pwd_input")

            if st.button("Unlock Access", use_container_width=True):
                if password == "Tico000123":
                    st.session_state.authenticated = True
                    st.session_state.role = "admin"
                    st.session_state.username = "Administrator"
                    st.rerun()
                elif password == "Tico000":
                    st.session_state.authenticated = True
                    st.session_state.role = "viewer"
                    st.session_state.username = "Manager"
                    st.rerun()
                else:
                    st.error("❌ Password khaldan!")
        return False
    return True


# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================
SALES_DB = "tico_sales_only_db.csv"
PAYMENTS_DB = "tico_payments_db.csv"

SALES_COLS = ["Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"]
PAYMENTS_COLS = ["Date", "Customer_Name", "Amount_Paid", "Received_By"]


def ensure_db():
    if not os.path.exists(SALES_DB):
        pd.DataFrame(columns=SALES_COLS).to_csv(SALES_DB, index=False)
    if not os.path.exists(PAYMENTS_DB):
        pd.DataFrame(columns=PAYMENTS_COLS).to_csv(PAYMENTS_DB, index=False)


ensure_db()


def load_sales():
    try:
        df = pd.read_csv(SALES_DB)
        if not df.empty and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame(columns=SALES_COLS)


def load_payments():
    try:
        df = pd.read_csv(PAYMENTS_DB)
        if not df.empty and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame(columns=PAYMENTS_COLS)


def save_sale(new_row: dict, existing_df: pd.DataFrame):
    new_df = pd.DataFrame([new_row])
    pd.concat([existing_df, new_df], ignore_index=True).to_csv(SALES_DB, index=False)


def save_payment(new_row: dict, existing_df: pd.DataFrame):
    new_df = pd.DataFrame([new_row])
    pd.concat([existing_df, new_df], ignore_index=True).to_csv(PAYMENTS_DB, index=False)


# ============================================================================
# MAIN APPLICATION
# ============================================================================
if check_password():
    sales_df = load_sales()
    payments_df = load_payments()

    # ── Header ──────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown("# 📊 TICO Wholesale")
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

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⏰ Time Filter")
        time_filter = st.radio("Period:", ["Today", "All Time"], label_visibility="collapsed")

        st.divider()
        st.markdown("### 📑 Navigation")

        if st.session_state.role == "admin":
            menu = st.radio(
                "Menu:",
                ["Dashboard", "Sales Entry", "Payment Entry", "Analytics"],
                label_visibility="collapsed",
            )
        else:
            menu = st.radio("Menu:", ["Dashboard", "Analytics"], label_visibility="collapsed")
            st.info("📖 Read-Only Mode")

        # ── Database Backup (Admin only) ────────────────────────────────────
        if st.session_state.role == "admin":
            st.divider()
            st.markdown("### 🛠️ Database Backup")

            # Sales CSV download
            if not sales_df.empty:
                sales_csv = sales_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Sales (CSV)",
                    data=sales_csv,
                    file_name="Tico_Sales_Backup.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_sales",
                )
            else:
                st.caption("Sales file is empty — nothing to download.")

            # Payments CSV download
            if not payments_df.empty:
                payments_csv = payments_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Payments (CSV)",
                    data=payments_csv,
                    file_name="Tico_Payments_Backup.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_payments",
                )
            else:
                st.caption("Payments file is empty — nothing to download.")

    # ── Time Filtering ────────────────────────────────────────────────────────
    filtered_sales = sales_df.copy()
    if time_filter == "Today" and not sales_df.empty:
        today = datetime.now().date()
        filtered_sales = sales_df[sales_df["Date"].dt.date == today]

    # =========================================================================
    # PAGE: Dashboard
    # =========================================================================
    if menu == "Dashboard":
        st.markdown(f"## 🏠 Dashboard Summary ({time_filter})")

        if not filtered_sales.empty:
            rev = filtered_sales["Total"].sum()
            cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum()
            prof = rev - cost
            items = filtered_sales["Quantity"].sum()
        else:
            rev, cost, prof, items = 0.0, 0.0, 0.0, 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Revenue", f"${rev:,.2f}")
        with col2:
            st.metric("📊 Net Profit", f"${prof:,.2f}")
        with col3:
            st.metric("📦 Items Sold", f"{int(items):,}")
        with col4:
            st.metric("🛍️ Total Orders", len(filtered_sales))

        st.divider()
        st.markdown("### 📋 Recent Recorded Sales")

        if not filtered_sales.empty:
            df_disp = filtered_sales.copy()
            df_disp["Date"] = df_disp["Date"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(
                df_disp.sort_values("Date", ascending=False),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("Wax xog ah ma jirto mudadan loo doortay.")

    # =========================================================================
    # PAGE: Sales Entry
    # =========================================================================
    elif menu == "Sales Entry":
        st.markdown("## 📝 Record New Sale")

        with st.form("sales_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                s_date = st.date_input("Date", value=datetime.now())
                c_name = st.text_input("Customer Name")
                i_name = st.text_input("Item Name")
            with col2:
                qty = st.number_input("Quantity", min_value=1, step=1, value=1)
                price = st.number_input("Wholesale Price ($)", min_value=0.01, step=0.01, value=0.01)
                c_price = st.number_input("Cost Price ($)", min_value=0.01, step=0.01, value=0.01)

            status = st.selectbox("Status", ["Completed", "Pending"])
            submitted = st.form_submit_button("💾 Save Sale Record", use_container_width=True)

        # Handle submission OUTSIDE the form block to avoid nesting issues
        if submitted:
            if not c_name.strip() or not i_name.strip():
                st.error("Fadlan buuxi dhammaan meelaha banaan!")
            else:
                tot = qty * price
                new_sale = {
                    "Date": pd.to_datetime(s_date),
                    "Customer_Name": c_name.strip(),
                    "Item_Name": i_name.strip(),
                    "Quantity": qty,
                    "Price": price,
                    "Cost_Price": c_price,
                    "Total": tot,
                    "Status": status,
                }
                save_sale(new_sale, sales_df)
                st.success("✅ Gabaad! Xogtii waa la kaydiyey.")
                st.rerun()

    # =========================================================================
    # PAGE: Payment Entry
    # =========================================================================
    elif menu == "Payment Entry":
        st.markdown("## 💳 Record Customer Payment")

        with st.form("payment_form", clear_on_submit=True):
            p_date = st.date_input("Payment Date", value=datetime.now())
            c_name = st.text_input("Customer Name")
            amt = st.number_input("Amount Paid ($)", min_value=0.01, step=0.01, value=0.01)
            rcv = st.text_input("Received By")
            submitted_p = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

        # Handle submission OUTSIDE the form block
        if submitted_p:
            if not c_name.strip() or not rcv.strip():
                st.error("Fadlan geli magaca macaamilka iyo qofka gudaasay!")
            else:
                new_payment = {
                    "Date": pd.to_datetime(p_date),
                    "Customer_Name": c_name.strip(),
                    "Amount_Paid": amt,
                    "Received_By": rcv.strip(),
                }
                save_payment(new_payment, payments_df)
                st.success("✅ Payment-gii si sax ah ayaa loo qoray!")
                st.rerun()

    # =========================================================================
    # PAGE: Analytics
    # =========================================================================
    elif menu == "Analytics":
        st.markdown("## 📊 Advanced Profit & Customer Analytics")

        if not filtered_sales.empty:
            # ── Summary KPIs ─────────────────────────────────────────────────
            rev = filtered_sales["Total"].sum()
            cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum()
            prof = rev - cost
            margin = (prof / rev * 100) if rev > 0 else 0.0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Revenue", f"${rev:,.2f}")
            with col2:
                st.metric("📊 Net Profit", f"${prof:,.2f}")
            with col3:
                st.metric("📈 Profit Margin", f"{margin:.1f}%")

            st.divider()

            # ── Customer & Product Tables ─────────────────────────────────────
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🏆 Top Customers by Spend")
                cust = (
                    filtered_sales.groupby("Customer_Name")["Total"]
                    .sum()
                    .reset_index()
                    .sort_values("Total", ascending=False)
                    .rename(columns={"Customer_Name": "Customer", "Total": "Total Spent ($)"})
                )
                cust["Total Spent ($)"] = cust["Total Spent ($)"].map("${:,.2f}".format)
                st.dataframe(cust, use_container_width=True, hide_index=True)

            with col2:
                st.markdown("### 📦 Top Products by Revenue")
                items_g = (
                    filtered_sales.groupby("Item_Name")["Total"]
                    .sum()
                    .reset_index()
                    .sort_values("Total", ascending=False)
                    .rename(columns={"Item_Name": "Product", "Total": "Revenue ($)"})
                )
                items_g["Revenue ($)"] = items_g["Revenue ($)"].map("${:,.2f}".format)
                st.dataframe(items_g, use_container_width=True, hide_index=True)

            st.divider()

            # ── Profit per Product ────────────────────────────────────────────
            st.markdown("### 💹 Profit Breakdown by Product")
            filtered_sales_copy = filtered_sales.copy()
            filtered_sales_copy["Profit"] = (
                (filtered_sales_copy["Price"] - filtered_sales_copy["Cost_Price"])
                * filtered_sales_copy["Quantity"]
            )
            profit_tbl = (
                filtered_sales_copy.groupby("Item_Name")
                .agg(
                    Units_Sold=("Quantity", "sum"),
                    Revenue=("Total", "sum"),
                    Profit=("Profit", "sum"),
                )
                .reset_index()
                .sort_values("Profit", ascending=False)
                .rename(columns={"Item_Name": "Product"})
            )
            profit_tbl["Revenue"] = profit_tbl["Revenue"].map("${:,.2f}".format)
            profit_tbl["Profit"] = profit_tbl["Profit"].map("${:,.2f}".format)
            st.dataframe(profit_tbl, use_container_width=True, hide_index=True)

        else:
            st.info("Xog xisaabeed diyaar ah ma jirto hadda.")
