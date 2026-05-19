ort streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path
import hashlib
import json

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
if "username" not in st.session_state:
    st.session_state.username = None

# Custom CSS for Professional Styling
st.markdown("""
    <style>
        /* Root Variables */
        :root {
            --primary-color: #1f77b4;
            --success-color: #2ca02c;
            --warning-color: #ff7f0e;
            --danger-color: #d62728;
            --dark-bg: #0f1419;
            --card-bg: #1a1f2e;
            --text-primary: #ffffff;
            --text-secondary: #b0b8c1;
            --border-color: #2d3748;
        }
        
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        
        /* Typography */
        h1, h2, h3 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            font-size: 1.8rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        h3 {
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        /* Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, #1a1f2e 0%, #252d3d 100%);
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #4a5568;
            box-shadow: 0 8px 12px rgba(31, 119, 180, 0.2);
            transform: translateY(-2px);
        }
        
        .metric-label {
            color: #b0b8c1;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        
        .metric-delta {
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .metric-positive {
            color: #2ca02c;
        }
        
        .metric-negative {
            color: #d62728;
        }
        
        /* Form Styling */
        .stForm {
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 1.5rem;
            background: rgba(26, 31, 46, 0.7);
            backdrop-filter: blur(10px);
        }
        
        .stTextInput input, .stSelectbox select, .stNumberInput input {
            background-color: #151b27 !important;
            color: #ffffff !important;
            border: 1px solid #2d3748 !important;
            border-radius: 8px !important;
        }
        
        .stTextInput input::placeholder, .stNumberInput input::placeholder {
            color: #7a8291 !important;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #1f77b4 0%, #1557a0 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2e8bc0 0%, #2366b2 100%);
            box-shadow: 0 6px 12px rgba(31, 119, 180, 0.3);
            transform: translateY(-2px);
        }
        
        /* Sidebar */
        .stSidebar {
            background: linear-gradient(180deg, #0f1419 0%, #151b27 100%);
            border-right: 1px solid #2d3748;
        }
        
        /* Table Styling */
        .stDataFrame {
            font-size: 0.95rem;
        }
        
        .stDataFrame thead th {
            background-color: #1a1f2e !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #2d3748 !important;
        }
        
        .stDataFrame tbody td {
            background-color: rgba(26, 31, 46, 0.5) !important;
            color: #ffffff !important;
            border-bottom: 1px solid #2d3748 !important;
        }
        
        /* Success/Alert Messages */
        .stSuccess {
            background-color: rgba(44, 160, 44, 0.15) !important;
            border: 1px solid #2ca02c !important;
            border-radius: 8px !important;
        }
        
        .stError {
            background-color: rgba(214, 39, 40, 0.15) !important;
            border: 1px solid #d62728 !important;
            border-radius: 8px !important;
        }
        
        .stWarning {
            background-color: rgba(255, 127, 14, 0.15) !important;
            border: 1px solid #ff7f0e !important;
            border-radius: 8px !important;
        }
        
        .stInfo {
            background-color: rgba(31, 119, 180, 0.15) !important;
            border: 1px solid #1f77b4 !important;
            border-radius: 8px !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 2px solid #2d3748;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #b0b8c1;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            color: #1f77b4 !important;
            border-bottom-color: #1f77b4 !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1a1f2e !important;
            color: #ffffff !important;
            border: 1px solid #2d3748 !important;
            border-radius: 8px !important;
        }
        
        /* Role Badge */
        .role-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-left: 1rem;
        }
        
        .role-admin {
            background-color: #d62728;
            color: white;
        }
        
        .role-viewer {
            background-color: #ff7f0e;
            color: white;
        }
        
        /* Loading Animation */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION SYSTEM - TWO-TIER ACCESS CONTROL
# ============================================================================

def check_password():
    """Check if user is authenticated and assign role based on password"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
            <div style='text-align: center; padding: 4rem 0;'>
                <h1 style='margin-bottom: 2rem; color: #1f77b4;'>TICO Wholesale Core</h1>
                <p style='color: #b0b8c1; font-size: 1.1rem; margin-bottom: 2rem;'>
                    Advanced Sales & Profit Analytics Platform
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🔐 Authentication Required")
            st.markdown("""
            **Available Accounts:**
            - **Admin**: Full access to all features
            - **Manager/Viewer**: Read-only access (Dashboard & Analytics only)
            """)
            
            password = st.text_input(
                "Enter Password",
                type="password",
                key="password_input",
                placeholder="Enter your password"
            )
            
            if st.button("Unlock Access", use_container_width=True):
                # Admin password - Full access
                if password == "Tico000123":
                    st.session_state.authenticated = True
                    st.session_state.role = "admin"
                    st.session_state.username = "Administrator"
                    st.success("✓ Admin access granted! Redirecting...")
                    st.rerun()
                
                # Manager/Viewer password - Read-only access
                elif password == "Tico000":
                    st.session_state.authenticated = True
                    st.session_state.role = "viewer"
                    st.session_state.username = "Manager"
                    st.success("✓ Manager access granted! (Read-only mode)")
                    st.rerun()
                
                else:
                    st.error("❌ Invalid password. Please try again.")
                    st.info("💡 Tip: Make sure you have the correct password for your account level.")
        
        return False
    
    return True

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

class DataManager:
    """Manage CSV database operations"""
    
    SALES_DB = "tico_sales_only_db.csv"
    PAYMENTS_DB = "tico_payments_db.csv"
    
    SALES_COLUMNS = ["Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"]
    PAYMENTS_COLUMNS = ["Date", "Customer_Name", "Amount_Paid", "Received_By"]
    
    @staticmethod
    def ensure_databases():
        """Create databases if they don't exist"""
        if not os.path.exists(DataManager.SALES_DB):
            pd.DataFrame(columns=DataManager.SALES_COLUMNS).to_csv(DataManager.SALES_DB, index=False)
        
        if not os.path.exists(DataManager.PAYMENTS_DB):
            pd.DataFrame(columns=DataManager.PAYMENTS_COLUMNS).to_csv(DataManager.PAYMENTS_DB, index=False)
    
    @staticmethod
    def load_sales_data():
        """Load sales database"""
        if os.path.exists(DataManager.SALES_DB):
            df = pd.read_csv(DataManager.SALES_DB)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
            return df
        return pd.DataFrame(columns=DataManager.SALES_COLUMNS)
    
    @staticmethod
    def load_payments_data():
        """Load payments database"""
        if os.path.exists(DataManager.PAYMENTS_DB):
            df = pd.read_csv(DataManager.PAYMENTS_DB)
            if not df.empty:
                df["Date"] = pd.to_datetime(df["Date"])
            return df
        return pd.DataFrame(columns=DataManager.PAYMENTS_COLUMNS)
    
    @staticmethod
    def add_sale(date, customer_name, item_name, quantity, price, cost_price, total, status):
        """Add a new sale record"""
        df = DataManager.load_sales_data()
        
        new_sale = pd.DataFrame({
            "Date": [pd.to_datetime(date)],
            "Customer_Name": [customer_name],
            "Item_Name": [item_name],
            "Quantity": [quantity],
            "Price": [price],
            "Cost_Price": [cost_price],
            "Total": [total],
            "Status": [status]
        })
        
        df = pd.concat([df, new_sale], ignore_index=True)
        df.to_csv(DataManager.SALES_DB, index=False)
        return True
    
    @staticmethod
    def add_payment(date, customer_name, amount_paid, received_by):
        """Add a new payment record"""
        df = DataManager.load_payments_data()
        
        new_payment = pd.DataFrame({
            "Date": [pd.to_datetime(date)],
            "Customer_Name": [customer_name],
            "Amount_Paid": [amount_paid],
            "Received_By": [received_by]
        })
        
        df = pd.concat([df, new_payment], ignore_index=True)
        df.to_csv(DataManager.PAYMENTS_DB, index=False)
        return True

# ============================================================================
# ANALYTICS ENGINE
# ============================================================================

class AnalyticsEngine:
    """Advanced analytics and calculations"""
    
    @staticmethod
    def get_filtered_sales(sales_df, time_filter):
        """Filter sales by time period"""
        if sales_df.empty:
            return sales_df
        
        today = datetime.now().date()
        
        if time_filter == "Today":
            return sales_df[sales_df["Date"].dt.date == today]
        elif time_filter == "This Month":
            current_month = today.replace(day=1)
            return sales_df[sales_df["Date"].dt.to_period("M") == current_month.to_period("M")]
        
        return sales_df
    
    @staticmethod
    def calculate_metrics(sales_df):
        """Calculate key metrics"""
        if sales_df.empty:
            return {
                "total_revenue": 0,
                "total_cost": 0,
                "total_profit": 0,
                "total_items_sold": 0,
                "total_orders": 0,
                "profit_margin": 0
            }
        
        total_revenue = sales_df["Total"].sum()
        total_cost = (sales_df["Quantity"] * sales_df["Cost_Price"]).sum()
        total_profit = total_revenue - total_cost
        total_items_sold = sales_df["Quantity"].sum()
        total_orders = len(sales_df)
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "total_items_sold": int(total_items_sold),
            "total_orders": total_orders,
            "profit_margin": profit_margin
        }
    
    @staticmethod
    def get_top_items(sales_df, metric="revenue", limit=5):
        """Get top selling items by revenue or quantity"""
        if sales_df.empty:
            return pd.DataFrame()
        
        if metric == "revenue":
            top = sales_df.groupby("Item_Name").agg({
                "Total": "sum",
                "Quantity": "sum"
            }).sort_values("Total", ascending=False).head(limit)
            top.columns = ["Revenue", "Quantity Sold"]
        else:  # quantity
            top = sales_df.groupby("Item_Name").agg({
                "Quantity": "sum",
                "Total": "sum"
            }).sort_values("Quantity", ascending=False).head(limit)
            top.columns = ["Quantity Sold", "Revenue"]
        
        return top.reset_index()
    
    @staticmethod
    def get_bottom_items(sales_df, metric="revenue", limit=5):
        """Get bottom selling items"""
        if sales_df.empty:
            return pd.DataFrame()
        
        if metric == "revenue":
            bottom = sales_df.groupby("Item_Name").agg({
                "Total": "sum",
                "Quantity": "sum"
            }).sort_values("Total", ascending=True).head(limit)
            bottom.columns = ["Revenue", "Quantity Sold"]
        else:  # quantity
            bottom = sales_df.groupby("Item_Name").agg({
                "Quantity": "sum",
                "Total": "sum"
            }).sort_values("Quantity", ascending=True).head(limit)
            bottom.columns = ["Quantity Sold", "Revenue"]
        
        return bottom.reset_index()
    
    @staticmethod
    def get_daily_performance(sales_df):
        """Get daily performance data"""
        if sales_df.empty:
            return pd.DataFrame()
        
        daily = sales_df.groupby(sales_df["Date"].dt.date).agg({
            "Total": "sum",
            "Quantity": "sum"
        }).reset_index()
        daily.columns = ["Date", "Revenue", "Items Sold"]
        return daily
    
    @staticmethod
    def get_customer_analysis(sales_df):
        """Analyze customer performance"""
        if sales_df.empty:
            return pd.DataFrame()
        
        customers = sales_df.groupby("Customer_Name").agg({
            "Total": "sum",
            "Quantity": "sum"
        }).sort_values("Total", ascending=False).reset_index()
        customers.columns = ["Customer_Name", "Total Spent", "Items Purchased"]
        return customers

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_metric_card(label, value, delta=None, delta_color="neutral"):
    """Render a metric card"""
    delta_text = ""
    if delta is not None:
        delta_symbol = "↑" if delta >= 0 else "↓"
        delta_color_class = "metric-positive" if delta >= 0 else "metric-negative"
        delta_text = f'<div class="metric-delta {delta_color_class}">{delta_symbol} {abs(delta):.1f}%</div>'
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_text}
        </div>
    """, unsafe_allow_html=True)

def render_header():
    """Render page header with role indicator"""
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    
    with col1:
        st.markdown("# 📊 TICO Wholesale Core")
        st.markdown("Advanced Sales & Profit Analytics Platform")
    
    with col2:
        # Display current role
        if st.session_state.role == "admin":
            st.markdown('<span class="role-badge role-admin">👤 ADMIN - Full Access</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="role-badge role-viewer">👁️ VIEWER - Read-Only</span>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.username = None
            st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Initialize databases
    DataManager.ensure_databases()
    
    # Load data
    sales_df = DataManager.load_sales_data()
    payments_df = DataManager.load_payments_data()
    
    # Render header
    render_header()
    st.divider()
    
    # ========================================================================
    # SIDEBAR - TIME FILTER & NAVIGATION
    # ========================================================================
    
    with st.sidebar:
        st.markdown("### ⏰ Time Period")
        time_filter = st.radio(
            "Select Analysis Period:",
            options=["Today", "This Month"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### 📑 Navigation")
        
        # Build navigation menu based on user role
        if st.session_state.role == "admin":
            nav_options = ["Dashboard", "Sales Entry", "Payment Entry", "Analytics"]
            nav_choice = st.radio(
                "Select Section:",
                options=nav_options,
                label_visibility="collapsed"
            )
        else:  # viewer role
            st.info("📖 **Read-Only Mode**\n\nYou have access to:\n- Dashboard\n- Analytics only")
            nav_options = ["Dashboard", "Analytics"]
            nav_choice = st.radio(
                "Select Section:",
                options=nav_options,
                label_visibility="collapsed"
            )
    
    # Filter sales data
    filtered_sales = AnalyticsEngine.get_filtered_sales(sales_df, time_filter)
    
    # ========================================================================
    # DASHBOARD TAB
    # ========================================================================
    
    if nav_choice == "Dashboard":
        st.markdown(f"## Dashboard - {time_filter}")
        
        # Calculate metrics
        metrics = AnalyticsEngine.calculate_metrics(filtered_sales)
        
        # Key Metrics Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Total Revenue",
                f"${metrics['total_revenue']:,.2f}",
                delta=None,
                help="Total sales revenue"
            )
        
        with col2:
            st.metric(
                "📊 Total Profit",
                f"${metrics['total_profit']:,.2f}",
                delta=f"{metrics['profit_margin']:.1f}%",
                help="Net profit (Revenue - Cost)"
            )
        
        with col3:
            st.metric(
                "📦 Items Sold",
                f"{metrics['total_items_sold']:,}",
                help="Total quantity sold"
            )
        
        with col4:
            st.metric(
                "🛍️ Orders",
                f"{metrics['total_orders']:,}",
                help="Total number of orders"
            )
        
        st.divider()
        
        # Key Metrics Row 2
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💵 Total Cost",
                f"${metrics['total_cost']:,.2f}",
                help="Total cost of goods sold"
            )
        
        with col2:
            avg_order_value = (metrics['total_revenue'] / metrics['total_orders']) if metrics['total_orders'] > 0 else 0
            st.metric(
                "🎯 Avg Order Value",
                f"${avg_order_value:,.2f}",
                help="Average revenue per order"
            )
        
        with col3:
            avg_profit = (metrics['total_profit'] / metrics['total_orders']) if metrics['total_orders'] > 0 else 0
            st.metric(
                "📈 Avg Profit/Order",
                f"${avg_profit:,.2f}",
                help="Average profit per order"
            )
        
        st.divider()
        
        # Performance Analysis
        st.markdown("### 📈 Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Selling Items")
            metric_choice = st.radio(
                "Measure by:",
                options=["Revenue", "Quantity"],
                key="top_metric",
                horizontal=True
            )
            
            top_items = AnalyticsEngine.get_top_items(
                filtered_sales,
                metric="revenue" if metric_choice == "Revenue" else "quantity",
                limit=5
            )
            
            if not top_items.empty:
                st.dataframe(top_items, use_container_width=True, hide_index=True)
            else:
                st.info("No sales data available for this period")
        
        with col2:
            st.markdown("#### 📉 Bottom Selling Items")
            metric_choice2 = st.radio(
                "Measure by:",
                options=["Revenue", "Quantity"],
                key="bottom_metric",
                horizontal=True
            )
            
            bottom_items = AnalyticsEngine.get_bottom_items(
                filtered_sales,
                metric="revenue" if metric_choice2 == "Revenue" else "quantity",
                limit=5
            )
            
            if not bottom_items.empty:
                st.dataframe(bottom_items, use_container_width=True, hide_index=True)
            else:
                st.info("No sales data available for this period")
        
        st.divider()
        
        # Daily Performance
        st.markdown("### 📅 Daily Performance")
        daily_perf = AnalyticsEngine.get_daily_performance(filtered_sales)
        
        if not daily_perf.empty:
            st.dataframe(daily_perf, use_container_width=True, hide_index=True)
            
            # Chart
            st.line_chart(data=daily_perf.set_index("Date"), use_container_width=True)
        else:
            st.info("No daily performance data for this period")
        
        st.divider()
        
        # Recent Sales
        st.markdown("### 📋 Recent Sales")
        if not filtered_sales.empty:
            display_sales = filtered_sales[[
                "Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"
            ]].copy()
            display_sales["Date"] = display_sales["Date"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(display_sales, use_container_width=True, hide_index=True)
        else:
            st.info("No sales recorded for this period")
    
    # ========================================================================
    # SALES ENTRY TAB - ADMIN ONLY
    # ========================================================================
    
    elif nav_choice == "Sales Entry":
        if st.session_state.role != "admin":
            st.error("❌ Access Denied")
            st.warning("This section is only available to administrators. You have read-only access.")
            return
        
        st.markdown("## 📝 Sales Entry Form")
        st.markdown("Add a new sale transaction")
        
        with st.form("sales_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                sale_date = st.date_input("Sale Date", value=datetime.now())
                customer_name = st.text_input(
                    "Customer Name",
                    placeholder="Enter customer name"
                )
                item_name = st.text_input(
                    "Item Name",
                    placeholder="Enter product name"
                )
            
            with col2:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    step=1,
                    help="Number of units sold"
                )
                price = st.number_input(
                    "Qiimaha jumlada lagu iibiyey (Unit Price)",
                    min_value=0.01,
                    step=0.01,
                    help="Price per unit for wholesale"
                )
                cost_price = st.number_input(
                    "Qiimaha soo-gadashada (Cost Price)",
                    min_value=0.01,
                    step=0.01,
                    help="Cost price per unit"
                )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total = quantity * price
                st.metric("Total Amount", f"${total:,.2f}")
            
            with col2:
                profit = (price - cost_price) * quantity
                st.metric(
                    "Estimated Profit",
                    f"${profit:,.2f}",
                    delta=f"{((profit/total)*100) if total > 0 else 0:.1f}%"
                )
            
            with col3:
                status = st.selectbox(
                    "Status",
                    options=["Completed", "Pending", "Cancelled"]
                )
            
            # Submit button
            if st.form_submit_button("✅ Record Sale", use_container_width=True):
                if not customer_name.strip():
                    st.error("❌ Please enter customer name")
                elif not item_name.strip():
                    st.error("❌ Please enter item name")
                else:
                    success = DataManager.add_sale(
                        date=sale_date,
                        customer_name=customer_name,
                        item_name=item_name,
                        quantity=quantity,
                        price=price,
                        cost_price=cost_price,
                        total=total,
                        status=status
                    )
                    
                    if success:
                        st.success("✓ Sale recorded successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Error recording sale")
        
        st.divider()
        
        # Recent Sales
        st.markdown("### 📋 All Sales Records")
        sales_all = DataManager.load_sales_data()
        
        if not sales_all.empty:
            display_sales = sales_all[[
                "Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Total", "Status"
            ]].copy()
            display_sales["Date"] = display_sales["Date"].dt.strftime("%Y-%m-%d %H:%M")
            display_sales = display_sales.sort_values("Date", ascending=False)
            st.dataframe(display_sales, use_container_width=True, hide_index=True)
        else:
            st.info("No sales records yet")
    
    # ========================================================================
    # PAYMENT ENTRY TAB - ADMIN ONLY
    # ========================================================================
    
    elif nav_choice == "Payment Entry":
        if st.session_state.role != "admin":
            st.error("❌ Access Denied")
            st.warning("This section is only available to administrators. You have read-only access.")
            return
        
        st.markdown("## 💳 Payment Entry Form")
        st.markdown("Record customer payments")
        
        with st.form("payment_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                payment_date = st.date_input("Payment Date", value=datetime.now())
                customer_name = st.text_input(
                    "Customer Name",
                    placeholder="Enter customer name"
                )
            
            with col2:
                amount_paid = st.number_input(
                    "Amount Paid",
                    min_value=0.01,
                    step=0.01,
                    help="Amount received from customer"
                )
                received_by = st.text_input(
                    "Received By",
                    placeholder="Your name or staff member"
                )
            
            # Submit button
            if st.form_submit_button("✅ Record Payment", use_container_width=True):
                if not customer_name.strip():
                    st.error("❌ Please enter customer name")
                elif not received_by.strip():
                    st.error("❌ Please enter who received the payment")
                else:
                    success = DataManager.add_payment(
                        date=payment_date,
                        customer_name=customer_name,
                        amount_paid=amount_paid,
                        received_by=received_by
                    )
                    
                    if success:
                        st.success("✓ Payment recorded successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Error recording payment")
        
        st.divider()
        
        # Payment Summary
        st.markdown("### 💰 Payment Summary")
        payments_all = DataManager.load_payments_data()
        
        if not payments_all.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Payments", f"${payments_all['Amount_Paid'].sum():,.2f}")
            
            with col2:
                st.metric("Number of Payments", len(payments_all))
            
            with col3:
                st.metric("Avg Payment", f"${payments_all['Amount_Paid'].mean():,.2f}")
            
            st.divider()
            
            # All payments
            st.markdown("### 📋 All Payment Records")
            display_payments = payments_all[[
                "Date", "Customer_Name", "Amount_Paid", "Received_By"
            ]].copy()
            display_payments["Date"] = display_payments["Date"].dt.strftime("%Y-%m-%d %H:%M")
            display_payments = display_payments.sort_values("Date", ascending=False)
            st.dataframe(display_payments, use_container_width=True, hide_index=True)
        else:
            st.info("No payment records yet")
    
    # ========================================================================
    # ANALYTICS TAB - AVAILABLE TO ALL (DOWNLOAD ONLY FOR ADMIN)
    # ========================================================================
    
    elif nav_choice == "Analytics":
        st.markdown("## 📊 Advanced Analytics")
        st.markdown(f"Analyzing data for: **{time_filter}**")
        
        # ====================================================================
        # SYSTEM BACKUP BUTTONS - PLACED DIRECTLY IN ANALYTICS TOP (ADMIN ONLY)
        # ====================================================================
        if st.session_state.role == "admin":
            st.markdown("### 🛠️ System Database Backup")
            st.info("Xisaabiye: Halkan waxaad si toos ah uga soo degsan kartaa dhammaan xogta feylasha CSV-ga ah si aad computer-kaaga ugu kaydsato (Backup).")
            
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                if not sales_df.empty:
                    sales_csv = sales_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download ALL Sales Data (CSV)",
                        data=sales_csv,
                        file_name=f"Backup_Sales_DB_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="analytics_dl_sales"
                    )
                else:
                    st.warning("Sales database is empty.")
            
            with dl_col2:
                if not payments_df.empty:
                    payments_csv = payments_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download ALL Payments Data (CSV)",
                        data=payments_csv,
                        file_name=f"Backup_Payments_DB_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="analytics_dl_payments"
                    )
                else:
                    st.warning("Payments database is empty.")
            st.divider()

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Customer Performance")
            customer_analysis = AnalyticsEngine.get_customer_analysis(filtered_sales)
            
            if not customer_analysis.empty:
                st.dataframe(customer_analysis, use_container_width=True, hide_index=True)
            else:
                st.info("No customer data for this period")
        
        with col2:
            st.markdown("### 📦 Product Performance")
            product_analysis = AnalyticsEngine.get_top_items(filtered_sales, metric="revenue", limit=10)
            
            if not product_analysis.empty:
                st.dataframe(product_analysis, use_container_width=True, hide_index=True)
            else:
                st.info("No product data for this period")
        
        st.divider()
        
        # Profit Analysis
        st.markdown("### 💵 Profit Analysis")
        
        if not filtered_sales.empty:
            profit_by_product = filtered_sales.copy()
            profit_by_product["Profit"] = (
                (profit_by_product["Price"] - profit_by_product["Cost_Price"]) *
                profit_by_product["Quantity"]
            )
            profit_by_product = profit_by_product.groupby("Item_Name").agg({
                "Profit": "sum",
                "Total": "sum",
                "Quantity": "sum"
            }).reset_index()
            profit_by_product["Profit Margin %"] = (
                (profit_by_product["Profit"] / profit_by_product["Total"] * 100)
                .round(2)
            )
            profit_by_product = profit_by_product.sort_values("Profit", ascending=False)
            profit_by_product.columns = ["Item_Name", "Profit", "Revenue", "Qty Sold", "Margin %"]
            
            st.dataframe(profit_by_product, use_container_width=True, hide_index=True)
        else:
            st.info("No profit data for this period")
        
        st.divider()
        
        # Summary Statistics
        st.markdown("### 📈 Summary Statistics")
        
        if not filtered_sales.empty:
            col1, col2, col3 = st.columns(3)
            
            total_revenue = filtered_sales["Total"].sum()
            total_cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum()
            total_profit = total_revenue - total_cost
            
            with col1:
                st.markdown(f"""
                    **Total Revenue:** ${total_revenue:,.2f}  
                    **Total Cost:** ${total_cost:,.2f}  
                    **Total Profit:** ${total_profit:,.2f}
                """)
            
            with col2:
                profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                avg_profit = total_profit / len(filtered_sales) if len(filtered_sales) > 0 else 0
                
                st.markdown(f"""
                    **Profit Margin:** {profit_margin:.2f}%  
                    **Avg Profit/Sale:** ${avg_profit:,.2f}  
                    **Total Sales:** {len(filtered_sales)}
                """)
            
            with col3:
                total_items = filtered_sales["Quantity"].sum()
                avg_items_per_sale = total_items / len(filtered_sales) if len(filtered_sales) > 0 else 0
                
                st.markdown(f"""
                    **Total Items Sold:** {int(total_items):,}  
                    **Avg Items/Sale:** {avg_items_per_sale:.2f}  
                    **Unique Customers:** {filtered_sales['Customer_Name'].nunique()}
                """)
        else:
            st.info("No data available for analysis")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    if check_password():
        main()
