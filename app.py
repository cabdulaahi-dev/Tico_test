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

# Initialize session state for Authentication & Data Cache
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Tani waa dambiisha kumeelgaarka ah ee Multiple Items-ka kaydisa
if "current_items" not in st.session_state:
    st.session_state.current_items = []

# ============================================================================
# CUSTOM CSS FOR DARK THEME
# ============================================================================
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        h1, h2, h3, h4 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #ffffff;
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
# DATABASE MANAGEMENT
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
            else: st.caption("Sales database is empty.")
            if not payments_df.empty:
                st.download_button("📥 Download Payments (CSV)", data=payments_df.to_csv(index=False).encode("utf-8"), file_name="Tico_Payments_Backup.csv", mime="text/csv", use_container_width=True, key="dl_payments")
            else: st.caption("Payments database is empty.")
        else:
            menu = st.radio("Menu:", ["Dashboard", "Analytics"], label_visibility="collapsed")
            st.info("📖 Read-Only Mode")

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
    # PAGE: SALES ENTRY (XALLISKII CUSBAA EE MULTIPLE ITEMS)
    # ------------------------------------------------------------------------
    elif menu == "Sales Entry":
        st.markdown("## 📝 Record New Sale (Multi-Item)")
        
        # 1. Customer & Payment Status
        st.markdown("#### 👤 1. Customer & Payment Type")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            s_date = st.date_input("Date", value=datetime.now())
        with col_m2:
            c_name = st.text_input("Customer Name", key="customer_name_input")
        with col_m3:
            status = st.selectbox("Payment Status / Nooca Bixinta", ["Cash", "Invoice"])
            
        st.divider()
        
        # 2. Qaybta alaabta lagu darayo (MA LAHA FORM)
        st.markdown("#### 📦 2. Add Items to current Order")
        col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1, 1, 1])
        with col_i1:
            i_name = st.text_input("Item Name", key="item_name_input")
        with col_i2:
            qty = st.number_input("Quantity", min_value=1, step=1, value=1, key="qty_input")
        with col_i3:
            price = st.number_input("Wholesale Price ($)", min_value=0.00, step=0.01, value=0.00, key="price_input")
        with col_i4:
            c_price = st.number_input("Cost Price ($)", min_value=0.00, step=0.01, value=0.00, key="cost_input")
            
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            discount = st.number_input("⚡ Discount / Qiimo-dhimis ($)", min_value=0.00, step=0.01, value=0.00, key="discount_input")
        with col_d2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Item to List (Ku dar Liiska)", use_container_width=True):
                if not i_name.strip():
                    st.error("Fadlan Geli magaca badeecada!")
                else:
                    sub_total = qty * price
                    if discount > sub_total:
                        st.error("❌ Discount-gu kama badnaan karo qiimaha badeecada oo dhan!")
                    else:
                        tot = sub_total - discount
                        # Waxaa lagu tuurayaa dambiisha kumeelgaarka ah
                        st.session_state.current_items.append({
                            "Item_Name": i_name.strip(),
                            "Quantity": qty,
                            "Price": price,
                            "Cost_Price": c_price,
                            "Discount": discount,
                            "Total": tot
                        })
                        st.success(f"✓ {i_name} waa ku dirmay dambiisha!")
                        st.rerun()

        # 3. Muujinta liiska agabka iyo Kaydinta guud
        if st.session_state.current_items:
            st.markdown("---")
            st.markdown("#### 🛒 Current Basket (Agabka hadda u qoran Macaamilka)")
            basket_df = pd.DataFrame(st.session_state.current_items)
            st.dataframe(basket_df, use_container_width=True, hide_index=True)
            
            grand_total = basket_df["Total"].sum()
            st.markdown(f"### 🏷️ Order Grand Total: **${grand_total:,.2f}** ({status})")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🗑️ Clear Basket (Masax dambiisha)", use_container_width=True):
                    st.session_state.current_items = []
                    st.rerun()
            with col_b2:
                if st.button("💾 Save Full Transaction (Kaydi Dhammaan)", use_container_width=True):
                    if not c_name.strip():
                        st.error("❌ Fadlan marka hore qor magaca macaamilka ku jira qaybta sare!")
                    else:
                        final_rows = []
                        for item in st.session_state.current_items:
                            final_rows.append({
                                "Date": str(s_date),
                                "Customer_Name": c_name.strip(),
                                "Item_Name": item["Item_Name"],
                                "Quantity": item["Quantity"],
                                "Price": item["Price"],
                                "Cost_Price": item["Cost_Price"],
                                "Discount": item["Discount"],
                                "Total": item["Total"],
                                "Status": status
                            })
                        
                        new_sales_df = pd.DataFrame(final_rows)
                        st.session_state.sales_data = pd.concat([st.session_state.sales_data, new_sales_df], ignore_index=True)
                        save_all_dbs()
                        
                        st.session_state.current_items = []
                        st.success(f"✅ Si guul leh ayaa loo kaydiyey dhammaan {len(final_rows)} badeecadood!")
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
        st.markdown("## ⚙️ Advanced Data Management")
        if st.session_state.sales_data.empty:
            st.info("Hadda wax xog ah kuma jiraan Database-ka.")
        else:
            sales_df_display = st.session_state.sales_data.copy()
            selected_row = st.selectbox(
                "Dooro safka:", 
                options=sales_df_display.index,
                format_func=lambda x: f"Safka {x}: {sales_df_display.loc[x, 'Customer_Name']} - {sales_df_display.loc[x, 'Item_Name']}"
            )
            row_data = st.session_state.sales_data.loc[selected_row]
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                edit_qty = st.number_input("Quantity", min_value=1, step=1, value=int(row_data["Quantity"]))
                edit_price = st.number_input("Wholesale Price ($)", min_value=0.00, step=0.01, value=float(row_data["Price"]))
                edit_cost = st.number_input("Cost Price ($)", min_value=0.00, step=0.01, value=float(row_data["Cost_Price"]))
                edit_disc = st.number_input("Discount ($)", min_value=0.00, step=0.01, value=float(row_data["Discount"]))
                edit_status = st.selectbox("Status", ["Cash", "Invoice"], index=["Cash", "Invoice"].index(row_data["Status"]))
                
                if st.button("🔄 Save Changes", use_container_width=True):
                    st.session_state.sales_data.loc[selected_row, "Quantity"] = edit_qty
                    st.session_state.sales_data.loc[selected_row, "Price"] = edit_price
                    st.session_state.sales_data.loc[selected_row, "Cost_Price"] = edit_cost
                    st.session_state.sales_data.loc[selected_row, "Discount"] = edit_disc
                    st.session_state.sales_data.loc[selected_row, "Total"] = (edit_qty * edit_price) - edit_disc
                    st.session_state.sales_data.loc[selected_row, "Status"] = edit_status
                    save_all_dbs()
                    st.success("✓ Bedelidii waa la kaydiyey!")
                    st.rerun()
            with col2:
                confirm_delete = st.checkbox("Xaqiiji tirtirista")
                if st.button("🗑️ Delete Row", use_container_width=True):
                    if confirm_delete:
                        st.session_state.sales_data = st.session_state.sales_data.drop(selected_row).reset_index(drop=True)
                        save_all_dbs()
                        st.rerun()

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
