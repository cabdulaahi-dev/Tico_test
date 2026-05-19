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

# Initialize session state for Authentication & Persistent Data Backup
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
        .stTextInput input, .stSelectbox select, .stNumberInput input {
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
        st.markdown("<div style='text-align: center; padding: 2rem 0;'><h1>TICO Wholesale Core</h1><p style='color: #b0b8c1;'>Sales & Profit Analytics Platform</p></div>", unsafe_allow_html=True)
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
# DATABASE MANAGEMENT (WITH SESSION CACHE TO PREVENT REBOOT LOSS)
# ============================================================================
SALES_DB = "tico_sales_only_db.csv"
PAYMENTS_DB = "tico_payments_db.csv"

SALES_COLS = ["Date", "Customer_Name", "Item_Name", "Quantity", "Price", "Cost_Price", "Discount", "Total", "Status"]
PAYMENTS_COLS = ["Date", "Customer_Name", "Amount_Paid", "Received_By"]

if "sales_data" not in st.session_state:
    if os.path.exists(SALES_DB):
        try:
            df = pd.read_csv(SALES_DB)
            if "Discount" not in df.columns: df["Discount"] = 0.0
            st.session_state.sales_data = df
        except: st.session_state.sales_data = pd.DataFrame(columns=SALES_COLS)
    else: st.session_state.sales_data = pd.DataFrame(columns=SALES_COLS)

if "payments_data" not in st.session_state:
    if os.path.exists(PAYMENTS_DB):
        try: st.session_state.payments_data = pd.read_csv(PAYMENTS_DB)
        except: st.session_state.payments_data = pd.DataFrame(columns=PAYMENTS_COLS)
    else: st.session_state.payments_data = pd.DataFrame(columns=PAYMENTS_COLS)

def save_all_dbs():
    st.session_state.sales_data.to_csv(SALES_DB, index=False)
    st.session_state.payments_data.to_csv(PAYMENTS_DB, index=False)

# ============================================================================
# MAIN APPLICATION
# ============================================================================
if check_password():
    sales_df = st.session_state.sales_data.copy()
    payments_df = st.session_state.payments_data.copy()
    
    if not sales_df.empty and "Date" in sales_df.columns:
        sales_df["Date"] = pd.to_datetime(sales_df["Date"], errors="coerce")
    if not payments_df.empty and "Date" in payments_df.columns:
        payments_df["Date"] = pd.to_datetime(payments_df["Date"], errors="coerce")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: st.markdown("# 📊 TICO Wholesale")
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

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### ⏰ Time Filter")
        time_filter = st.radio("Period:", ["Today", "All Time"], label_visibility="collapsed")
        st.divider()
        st.markdown("### 📑 Navigation")
        
        if st.session_state.role == "admin":
            menu = st.radio("Menu:", ["Dashboard", "Sales Entry", "Payment Entry", "Data Management", "Analytics"], label_visibility="collapsed")
            
            st.divider()
            st.markdown("### 🛠️ Database Backup")
            if not sales_df.empty:
                st.download_button("📥 Download Sales (CSV)", data=sales_df.to_csv(index=False).encode("utf-8"), file_name="Tico_Sales_Backup.csv", mime="text/csv", use_container_width=True, key="dl_sales")
            else: st.caption("Sales file is empty.")
            if not payments_df.empty:
                st.download_button("📥 Download Payments (CSV)", data=payments_df.to_csv(index=False).encode("utf-8"), file_name="Tico_Payments_Backup.csv", mime="text/csv", use_container_width=True, key="dl_payments")
            else: st.caption("Payments file is empty.")
        else:
            menu = st.radio("Menu:", ["Dashboard", "Analytics"], label_visibility="collapsed")
            st.info("📖 Read-Only Mode")

    # Time Filter Logic
    filtered_sales = sales_df.copy()
    if time_filter == "Today" and not sales_df.empty:
        filtered_sales = sales_df[sales_df["Date"].dt.date == datetime.now().date()]

    # ------------------------------------------------------------------------
    # PAGE: DASHBOARD
    # ------------------------------------------------------------------------
    if menu == "Dashboard":
        st.markdown(f"## 🏠 Dashboard Summary ({time_filter})")
        if not filtered_sales.empty:
            rev = filtered_sales["Total"].sum()
            cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum()
            prof = rev - cost
            items = filtered_sales["Quantity"].sum()
        else: rev, cost, prof, items = 0.0, 0.0, 0.0, 0

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("💰 Total Revenue (Net)", f"${rev:,.2f}")
        with col2: st.metric("📊 Net Profit", f"${prof:,.2f}")
        with col3: st.metric("📦 Items Sold", f"{int(items):,}")
        with col4: st.metric("🛍️ Total Orders", len(filtered_sales))

        st.divider()
        st.markdown("### 📋 Recent Recorded Sales")
        if not filtered_sales.empty:
            df_disp = filtered_sales.copy()
            df_disp["Date"] = df_disp["Date"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(df_disp.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        else: st.warning("Wax xog ah ma jirto mudadan loo doortay.")

    # ------------------------------------------------------------------------
    # PAGE: SALES ENTRY
    # ------------------------------------------------------------------------
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
                price = st.number_input("Wholesale Price ($)", min_value=0.00, step=0.01, value=0.00)
                c_price = st.number_input("Cost Price ($)", min_value=0.00, step=0.01, value=0.00)
            
            st.divider()
            col3, col4 = st.columns(2)
            with col3:
                discount = st.number_input("⚡ Discount / Qiimo-dhimis ($)", min_value=0.00, step=0.01, value=0.00)
            with col4:
                status = st.selectbox("Payment Status / Nooca Bixinta", ["Cash", "Invoice"])
                
            submitted = st.form_submit_button("💾 Save Sale Record", use_container_width=True)

        if submitted:
            if not c_name.strip() or not i_name.strip():
                st.error("Fadlan buuxi dhammaan meelaha banaan!")
            else:
                sub_total = qty * price
                if discount > sub_total:
                    st.error("❌ Discount-gu kama badnaan karo qiimaha badeecada oo dhan!")
                else:
                    tot = sub_total - discount
                    new_sale = pd.DataFrame([{
                        "Date": str(s_date), "Customer_Name": c_name.strip(), "Item_Name": i_name.strip(),
                        "Quantity": qty, "Price": price, "Cost_Price": c_price, "Discount": discount, "Total": tot, "Status": status
                    }])
                    st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_sale], ignore_index=True)
                    save_all_dbs()
                    st.success(f"✅ La kaydiyey! Qaabka: {status} | Total: ${tot:,.2f}")
                    st.rerun()

    # ------------------------------------------------------------------------
    # PAGE: PAYMENT ENTRY
    # ------------------------------------------------------------------------
    elif menu == "Payment Entry":
        st.markdown("## 💳 Record Customer Payment")
        with st.form("payment_form", clear_on_submit=True):
            p_date = st.date_input("Payment Date", value=datetime.now())
            c_name = st.text_input("Customer Name")
            amt = st.number_input("Amount Paid ($)", min_value=0.01, step=0.01, value=0.01)
            rcv = st.text_input("Received By")
            submitted_p = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

        if submitted_p:
            if not c_name.strip() or not rcv.strip():
                st.error("Fadlan geli magaca macaamilka iyo qofka gudaasay!")
            else:
                new_payment = pd.DataFrame([{
                    "Date": str(p_date), "Customer_Name": c_name.strip(), "Amount_Paid": amt, "Received_By": rcv.strip()
                }])
                st.session_state.payments_data = pd.concat([st.session_state.payments_data, new_payment], ignore_index=True)
                save_all_dbs()
                st.success("✅ Payment-gii si sax ah ayaa loo qoray!")
                st.rerun()

    # ------------------------------------------------------------------------
    # PAGE: DATA MANAGEMENT
    # ------------------------------------------------------------------------
    elif menu == "Data Management":
        st.markdown("## ⚙️ Advanced Data Management (Edit, Delete, Discount)")
        
        if st.session_state.sales_data.empty:
            st.info("Hadda wax xog ah kuma jiraan Database-ka.")
        else:
            st.markdown("### Select a Transaction row to Edit or Delete:")
            sales_df_display = st.session_state.sales_data.copy()
            
            selected_row = st.selectbox(
                "Dooro safka aad rabto inaad wax ka bedesho ama tirtirto:", 
                options=sales_df_display.index,
                format_func=lambda x: f"Safka {x}: {sales_df_display.loc[x, 'Customer_Name']} - {sales_df_display.loc[x, 'Item_Name']} [{sales_df_display.loc[x, 'Status']}]"
            )
            
            row_data = st.session_state.sales_data.loc[selected_row]
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ✏️ Update / Edit Item details")
                edit_qty = st.number_input("Quantity", min_value=1, step=1, value=int(row_data["Quantity"]), key="e_qty")
                edit_price = st.number_input("Wholesale Price ($)", min_value=0.00, step=0.01, value=float(row_data["Price"]), key="e_prc")
                edit_cost = st.number_input("Cost Price ($)", min_value=0.00, step=0.01, value=float(row_data["Cost_Price"]), key="e_cst")
                edit_disc = st.number_input("Discount ($)", min_value=0.00, step=0.01, value=float(row_data["Discount"]), key="e_dsc")
                
                current_status = row_data["Status"] if row_data["Status"] in ["Cash", "Invoice"] else "Cash"
                edit_status = st.selectbox("Status", ["Cash", "Invoice"], index=["Cash", "Invoice"].index(current_status), key="e_sts")
                
                if st.button("🔄 Save Changes (Wax ka bedel)", use_container_width=True):
                    sub_tot = edit_qty * edit_price
                    new_tot = sub_tot - edit_disc
                    
                    st.session_state.sales_data.loc[selected_row, "Quantity"] = edit_qty
                    st.session_state.sales_data.loc[selected_row, "Price"] = edit_price
                    st.session_state.sales_data.loc[selected_row, "Cost_Price"] = edit_cost
                    st.session_state.sales_data.loc[selected_row, "Discount"] = edit_disc
                    st.session_state.sales_data.loc[selected_row, "Total"] = new_tot
                    st.session_state.sales_data.loc[selected_row, "Status"] = edit_status
                    
                    save_all_dbs()
                    st.success("✓ Xogtii si guul leh ayaa loo bedelay!")
                    st.rerun()
                    
            with col2:
                st.markdown("#### ❌ Safe Delete Action")
                st.warning(f"Ogow: Haddi aad badhanka riixdo, waxaad tirtiraysaa safkan.")
                confirm_delete = st.checkbox("Haa, waxaan xaqiijinayaa inaan safkan kaliya tirtiro")
                if st.button("🗑️ Delete Selected Row (Iska saar safkan)", use_container_width=True):
                    if confirm_delete:
                        st.session_state.sales_data = st.session_state.sales_data.drop(selected_row).reset_index(drop=True)
                        save_all_dbs()
                        st.success("✓ Safkii waa la tirtiray!")
                        st.rerun()
                    else: st.error("Fadlan guji check-box-ka xaqiijinta!")

    # ------------------------------------------------------------------------
    # PAGE: ANALYTICS
    # ------------------------------------------------------------------------
    elif menu == "Analytics":
        st.markdown("## 📊 Advanced Profit & Customer Analytics")
        if not filtered_sales.empty:
            rev = filtered_sales["Total"].sum()
            cost = (filtered_sales["Quantity"] * filtered_sales["Cost_Price"]).sum()
            prof = rev - cost
            margin = (prof / rev * 100) if rev > 0 else 0.0

            col1, col2, col3 = st.columns(3)
            with col1: st.metric("💰 Net Revenue", f"${rev:,.2f}")
            with col2: st.metric("📊 Total Profit", f"${prof:,.2f}")
            with col3: st.metric("📈 Profit Margin", f"{margin:.1f}%")
        else: st.info("Xog xisaabeed diyaar ah ma jirto hadda.")
