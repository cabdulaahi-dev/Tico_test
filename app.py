import streamlit as st
import pandas as pd
import numpy as np
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

# Initialize session state for authentication and role tracking
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None  # "admin" or "viewer"

# Custom CSS for Professional Styling
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #ffffff; }
        .role-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; font-weight: 600; margin-left: 1rem; }
        .role-admin { background-color: #d62728; color: white; }
        .role-viewer { background-color: #ff7f0e; color: white; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

def check_password():
    if not st.session_state.authenticated:
        st.markdown("<div style='text-align: center; padding: 2rem 0;'><h1>TICO Wholesale Core</h1></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 Authentication Required")
            password = st.text_input("Enter Password", type="password", placeholder="Enter password")
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
                    st.error("❌ Invalid password.")
        return False
    return True

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

SALES_FILE = "tico_sales_only_db.csv"
PAYMENTS_FILE = "tico_payments_db.csv"

def ensure_databases():
    if not os.path.exists(SALES_FILE) or os.stat(SALES_FILE).st_size == 0:
        pd.DataFrame(columns=["Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"]).to_csv(SALES_FILE, index=False)
    if not os.path.exists(PAYMENTS_FILE) or os.stat(PAYMENTS_FILE).st_size == 0:
        pd.DataFrame(columns=["Date", "Customer_Name", "Amount_Paid", "Received_By"]).to_csv(PAYMENTS_FILE, index=False)

ensure_databases()

# Load Data cleanly
try:
    sales_df = pd.read_csv(SALES_FILE)
    sales_df["Date"] = pd.to_datetime(sales_df["Date"])
except:
    sales_df = pd.DataFrame(columns=["Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"])

try:
    payments_df = pd.read_csv(PAYMENTS_FILE)
    payments_df["Date"] = pd.to_datetime(payments_df["Date"])
except:
    payments_df = pd.DataFrame(columns=["Date", "Customer_Name", "Amount_Paid", "Received_By"])

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if check_password():
    # Header
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        st.markdown("# 📊 TICO Wholesale Core")
    with col2:
        if st.session_state.role == "admin":
            st.markdown('<span class="role-badge role-admin">👤 ADMIN - Full Access</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="role-badge role-viewer">👁️ VIEWER - Read-Only</span>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()
            
    st.divider()

    # Sidebar Navigation & Filters
    with st.sidebar:
        st.markdown("### ⏰ Time Period")
        time_filter = st.radio("Select Analysis Period:", options=["Today", "This Month"])
        st.divider()
        st.markdown("### 📑 Navigation")
        if st.session_state.role == "admin":
            nav_choice = st.radio("Select Section:", options=["Dashboard", "Sales Entry", "Payment Entry", "Analytics"])
        else:
            nav_choice = st.radio("Select Section:", options=["Dashboard", "Analytics"])

        # ====================================================================
        # MAINTENANCE & BACKUP SYSTEM (ADMIN ONLY)
        # ====================================================================
        if st.session_state.role == "admin":
            st.divider()
            st.markdown("### 🛠️ Admin Maintenance")
            
            # Download Sales DB
            sales_csv = sales_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Sales Backup",
                data=sales_csv,
                file_name=f"Backup_Sales_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Download Payments DB
            payments_csv = payments_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Payments Backup",
                data=payments_csv,
                file_name=f"Backup_Payments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Time Filter Logic
    today = datetime.now().date()
    if not sales_df.empty:
        if time_filter == "Today":
            filtered_sales = sales_df[sales_df["Date"].dt.date == today]
        else:
            filtered_sales = sales_df[sales_df["Date"].dt.to_period("M") == pd.to_datetime(today).to_period("M")]
    else:
        filtered_sales = sales_df

    # ========================================================================
    # DASHBOARD TAB
    # ========================================================================
    if nav_choice == "Dashboard":
        st.markdown(f"## Dashboard - {time_filter}")
        
        # Calculate Metrics
        total_rev = filtered_sales["Total"].sum() if not filtered_sales.empty else 0.0
        total_cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum() if not filtered_sales.empty else 0.0
        total_profit = total_rev - total_cost
        margin = (total_profit / total_rev * 100) if total_rev > 0 else 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total Revenue", f"${total_rev:,.2f}")
        col2.metric("📊 Total Profit", f"${total_profit:,.2f}", delta=f"{margin:.1f}% Margin")
        col3.metric("📦 Items Sold", f"{int(filtered_sales['Quantity'].sum()) if not filtered_sales.empty else 0:,}")
        col4.metric("🛍️ Orders", f"{len(filtered_sales):,}")

        st.divider()
        
        # Top & Bottom Items Performance
        st.markdown("### 🏆 Product Performance Analytics")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 📈 Top Selling Items")
            if not filtered_sales.empty:
                top = filtered_sales.groupby("Item_Name")["Quantity"].sum().sort_values(ascending=False).head(5).reset_index()
                st.dataframe(top, use_container_width=True, hide_index=True)
            else:
                st.info("No data available for this period")
                
        with col_b:
            st.markdown("#### 📉 Bottom Selling Items")
            if not filtered_sales.empty:
                bottom = filtered_sales.groupby("Item_Name")["Quantity"].sum().sort_values(ascending=True).head(5).reset_index()
                st.dataframe(bottom, use_container_width=True, hide_index=True)
            else:
                st.info("No data available for this period")

    # ========================================================================
    # SALES ENTRY
    # ========================================================================
    elif nav_choice == "Sales Entry":
        st.markdown("## 📝 Sales Entry Form")
        with st.form("sales_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sale_date = st.date_input("Sale Date", value=datetime.now())
                customer_name = st.text_input("Customer Name")
                item_name = st.text_input("Item Name")
            with col2:
                quantity = st.number_input("Quantity", min_value=1, step=1)
                price = st.number_input("Wholesale Selling Price ($)", min_value=0.01, step=0.01)
                cost_price = st.number_input("Cost Price / Soo-gadashada ($)", min_value=0.01, step=0.01)
            status = st.selectbox("Status", options=["Cash", "Credit"])
            
            if st.form_submit_button("✅ Record Sale", use_container_width=True):
                if customer_name and item_name:
                    total_amount = quantity * price
                    new_sale = pd.DataFrame([{
                        "Date": pd.to_datetime(sale_date), "Customer_Name": customer_name, "Item_Name": item_name,
                        "Quantity": quantity, "Price": price, "Cost_Price": cost_price, "Total": total_amount, "Status": status
                    }])
                    sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False)
                    st.success("✓ Sale successfully recorded!")
                    st.rerun()
                else:
                    st.error("Please fill all empty fields!")

    # ========================================================================
    # PAYMENT ENTRY
    # ========================================================================
    elif nav_choice == "Payment Entry":
        st.markdown("## 💳 Payment Entry Form")
        with st.form("payment_form", clear_on_submit=True):
            payment_date = st.date_input("Payment Date", value=datetime.now())
            customer_name = st.text_input("Customer Name")
            amount_paid = st.number_input("Amount Paid ($)", min_value=0.01, step=0.01)
            received_by = st.text_input("Received By")
            
            if st.form_submit_button("✅ Record Payment", use_container_width=True):
                if customer_name and amount_paid > 0 and received_by:
                    new_pay = pd.DataFrame([{
                        "Date": pd.to_datetime(payment_date), "Customer_Name": customer_name, 
                        "Amount_Paid": amount_paid, "Received_By": received_by
                    }])
                    payments_df = pd.concat([payments_df, new_pay], ignore_index=True)
                    payments_df.to_csv(PAYMENTS_FILE, index=False)
                    st.success("✓ Payment recorded successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all empty fields!")

    # ========================================================================
    # ANALYTICS TAB
    # ========================================================================
    elif nav_choice == "Analytics":
        st.markdown("## 📊 Advanced Analytics & Profits")
        if not filtered_sales.empty:
            profit_df = filtered_sales.copy()
            profit_df["Net_Profit"] = profit_df["Total"] - (profit_df["Quantity"] * profit_df["Cost_Price"])
            summary = profit_df.groupby("Item_Name").agg({
                "Quantity": "sum", "Total": "sum", "Net_Profit": "sum"
            }).reset_index()
            summary.columns = ["Item Name", "Total Qty Sold", "Total Revenue ($)", "Net Profit ($)"]
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No data available for analysis in this period.")
