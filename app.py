import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="TICO Secure System", page_icon="🔒", layout="centered")

# ==========================================
# 🔐 QAYBTA AMMAANKA (PASSWORD PROTECTION)
# ==========================================
# Waa kan password-ka rasmiga ah (Wadanku bedeli kartaa hadhow)
OFFICIAL_PASSWORD = "TICO_Admin_2026"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.header("🔒 TICO Secure Core Login")
    st.write("Fadlan geli Password-ka rasmiga ah si aad u gasho nidaamka.")
    
    user_password = st.text_input("Password:", type="password")
    login_button = st.button("Gasho Nidaamka")
    
    if login_button:
        if user_password == OFFICIAL_PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Password-ku waa khaldan yahay! Fadlan iska hubi.")
    st.stop() # Wixii code ah ee hoos ku qoran ma shaqaynayo ilaa password-ka la saxo

# ==========================================
# 📊 BADNAAMIDKA DEFTIISII (MARKII LA LOG IN-GAARO)
# ==========================================
SALES_FILE = "tico_sales_only_db.csv"
PAYMENTS_FILE = "tico_payments_db.csv"

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

sales_df = load_data(SALES_FILE, ["Invoice_ID", "Customer_Name", "Date", "Product_Name", "Quantity", "Cost_Price", "Selling_Price", "Payment_Type", "Profit"])
pay_df = load_data(PAYMENTS_FILE, ["Payment_ID", "Invoice_ID", "Customer_Name", "Date_Paid", "Amount_Paid"])

# Badhanka ka bixitaanka (Log Out) oo ku dhex jira Sidebar-ka
st.sidebar.title("🎛️ TICO Core v1.4")
if st.sidebar.button("🔒 Ka bax (Log Out)"):
    st.session_state["authenticated"] = False
    st.rerun()

menu = ["📊 Dashboard-ka Faa'idada", "📝 Geli Iibka Cusub", "💰 Geli Lacag-bixinta (Payment)"]
choice = st.sidebar.radio("U kala guur:", menu)

# 1. DASHBOARD-KA FAA'IDADA
if choice == "📊 Dashboard-ka Faa'idada":
    st.header("📊 Warbixinta Iibka, Faa'idada iyo Lacag-bixinta")
    
    total_profit = sales_df["Profit"].sum() if not sales_df.empty else 0.0
    
    cash_df = sales_df[sales_df["Payment_Type"] == "Cash"]
    total_cash_sales = (cash_df["Quantity"] * cash_df["Selling_Price"]).sum() if not cash_df.empty else 0.0
    
    credit_df = sales_df[sales_df["Payment_Type"] == "Invoice (Amaah)"]
    total_credit_created = (credit_df["Quantity"] * credit_df["Selling_Price"]).sum() if not credit_df.empty else 0.0
    
    total_payments_received = pay_df["Amount_Paid"].sum() if not pay_df.empty else 0.0
    
    actual_cash_box = total_cash_sales + total_payments_received
    remaining_credit_outstanding = total_credit_created - total_payments_received

    st.write("### 💵 Xaaladda Maaliyadda")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🟢 Cash-ka Sanduuqa ku jira", value=f"${actual_cash_box:,.2f}")
    with col2:
        st.metric(label="🔴 Daynta Dibadda ku dhiman", value=f"${remaining_credit_outstanding:,.2f}")
        
    st.metric(label="📈 Wadarta Faa'idada Shirkadda (Total Net Profit)", value=f"${total_profit:,.2f}")
    
    # --- FALANQAYNTA IIBKA ALAABTA EE BISHA ---
    st.write("---")
    st.subheader("📊 Falanqaynta Alaabta ee Bisha")
    if sales_df.empty:
        st.info("💡 Hadda ma jirto xog iib ah.")
    else:
        sales_df['Date'] = pd.to_datetime(sales_df['Date'])
        sales_df['Month_Year'] = sales_df['Date'].dt.strftime('%B %Y')
        available_months = sales_df['Month_Year'].unique()
        selected_month = st.selectbox("Dooro Bisha:", available_months)
        
        monthly_data = sales_df[sales_df['Month_Year'] == selected_month]
        product_ranks = monthly_data.groupby("Product_Name")["Quantity"].sum().reset_index()
        product_ranks = product_ranks.sort_values(by="Quantity", ascending=False)
        
        if not product_ranks.empty:
            col_top, col_low = st.columns(2)
            with col_top:
                st.success("📈 Ugu iibka Badneyd (Top Selling)")
                top_product = product_ranks.iloc[0]
                st.write(f"**{top_product['Product_Name']}** ({top_product['Quantity']} xabo)")
            with col_low:
                st.error("📉 Ugu iibka Hooseysay (Low Selling)")
                low_product = product_ranks.iloc[-1]
                st.write(f"**{low_product['Product_Name']}** ({low_product['Quantity']} xabo)")

    st.write("---")
    st.subheader("🧾 Liiska Iibka Maalinlaha (Sales Logs)")
    if not sales_df.empty:
        display_sales = sales_df.copy()
        display_sales['Date'] = display_sales['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_sales[["Date", "Invoice_ID", "Customer_Name", "Product_Name", "Quantity", "Selling_Price", "Payment_Type", "Profit"]])

    st.subheader("💰 Taariikhda Lacagaha la soo celiyey (Payment History)")
    st.dataframe(pay_df)

# 2. GELI IIBKA MAALINLAHA
elif choice == "📝 Geli Iibka Cusub":
    st.header("📝 Geli Iibka Maalinlaha")
    with st.form("sales_entry_form", clear_on_submit=True):
        p_name = st.text_input("Magaca Alaabta la gadday:")
        q_qty = st.number_input("Tirada (Quantity):", min_value=1, step=1)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_cost = st.number_input("Qiimihii idinku joogtay 1-xabo ($):", min_value=0.0, step=0.5)
        with col_p2:
            p_sale = st.number_input("Qiimihii aad ku gaddeen 1-xabo ($):", min_value=0.0, step=0.5)
            
        pay_type = st.selectbox("Nooca Iibka:", ["Cash", "Invoice (Amaah)"])
        cust_name = st.text_input("Magaca Macamiilka:", value="Macaamiil Caadi ah")
        
        submit_sale = st.form_submit_with_rows(["Kaydi Iibka"])
        
        if submit_sale and p_name:
            total_cost = p_cost * q_qty
            total_revenue = p_sale * q_qty
            profit = total_revenue - total_cost
            
            inv_id = f"INV-{len(sales_df[sales_df['Payment_Type'] == 'Invoice (Amaah)']) + 1001}" if pay_type == "Invoice (Amaah)" else "CASH-SALE"
            current_date = datetime.today().strftime('%Y-%m-%d')
            
            new_sale = pd.DataFrame([[inv_id, cust_name, current_date, p_name, q_qty, p_cost, p_sale, pay_type, profit]], columns=["Invoice_ID", "Customer_Name", "Date", "Product_Name", "Quantity", "Cost_Price", "Selling_Price", "Payment_Type", "Profit"])
            sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
            sales_df.to_csv(SALES_FILE, index=False)
            st.success(f"👍 Iibkii waa la kaydiyey!")

# 3. GELI LACAG-BIXINTA (RECEIVE PAYMENT)
else:
    st.header("💰 Diiwaangeli Lacag-bixinta")
    credit_invoices = sales_df[sales_df["Payment_Type"] == "Invoice (Amaah)"]
    
    if credit_invoices.empty:
        st.warning("Hadda ma jiraan Invoice-yo amaah ah oo nidaamka ku jira.")
    else:
        with st.form("payment_form", clear_on_submit=True):
            selected_invoice = st.selectbox("Dooro Invoice ID-ga:", credit_invoices["Invoice_ID"].unique())
            customer_real_name = credit_invoices[credit_invoices["Invoice_ID"] == selected_invoice]["Customer_Name"].values[0]
            st.write(f"👤 **Macamiilka:** {customer_real_name}")
            
            amount_paid = st.number_input("Tirada Lacagta ($):", min_value=0.1, step=1.0)
            submit_payment = st.form_submit_with_rows(["Xaqiiji Lacagta"])
            
            if submit_payment:
                pay_id = f"PAY-{len(pay_df) + 5001}"
                current_date = datetime.today().strftime('%Y-%m-%d %H:%M')
                
                new_pay = pd.DataFrame([[pay_id, selected_invoice, customer_real_name, current_date, amount_paid]], columns=pay_df.columns)
                pay_df = pd.concat([pay_df, new_pay], ignore_index=True)
                pay_df.to_csv(PAYMENTS_FILE, index=False)
                st.success(f"🎉 Lacagta waa la guddoomay! Dayntiina waa laga dhimay.")
