import pandas as pd
import streamlit as st
import pytz
from supabase import create_client, Client
from datetime import datetime
import time

# --- ၁။ Setup & Connections ---
st.set_page_config(page_title="Admin System 2.0", layout="wide")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

# --- ၂။ Login Session စတင်ခြင်း ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- ၃။ Login Page ပြသခြင်း ---
if not st.session_state['logged_in']:
    st.title("🔐 Admin Login System")
    with st.form("login_form"):
        input_user = st.text_input("User ID")
        input_pass = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            try:
                res = supabase.table("user_setup").select("*").eq("user_id", input_user).eq("password", input_pass).execute()
                if res.data:
                    st.session_state['logged_in'] = True
                    st.success("✅ Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID or Password")
            except Exception as e:
                st.error(f"Login Error: {e}")
    st.stop()

# --- ၄။ Main System (Login ဝင်ပြီးမှသာ ပေါ်လာမည့်အပိုင်း) ---
st.sidebar.success("Logged In ✅")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.title("🚀 Main Menu")
page = st.sidebar.radio("Go to:", 
    ["📊 Dashboard", "🔍 Search Transactions", "📋 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"])
st.sidebar.markdown("---")
st.sidebar.info("System Version 2.0v")

# --- ၅။ Dashboard Page ---
if page == "📊 Dashboard":
    st.title("📈 Transaction Dashboard")
    st.markdown(f"**Last Updated:** {now_yangon.strftime('%Y-%m-%d %H:%M:%S')} (Yangon Time)")

    try:
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        if res.data:
            df_dash = pd.DataFrame(res.data)
            df_dash['created_at'] = pd.to_datetime(df_dash['created_at']).dt.tz_convert('Asia/Yangon')
            
            today = now_yangon.date()
            this_month = now_yangon.month
            this_year = now_yangon.year

            daily_sum = df_dash[df_dash['created_at'].dt.date == today]['amount'].sum()
            monthly_sum = df_dash[(df_dash['created_at'].dt.month == this_month) & (df_dash['created_at'].dt.year == this_year)]['amount'].sum()
            yearly_sum = df_dash[df_dash['created_at'].dt.year == this_year]['amount'].sum()
        else:
            daily_sum = monthly_sum = yearly_sum = 0
            st.info("ℹ️ Database ထဲတွင် Transaction data မရှိသေးပါ။")

        st.subheader("Daily Transaction")
        d1, d2 = st.columns(2)
        d1.info(f"### {daily_sum:,.2f} \n 📉 Daily Inward")
        d2.info(f"### 0.00 \n 📉 Daily Outward")

        st.divider()
        st.subheader("Monthly Transaction")
        m1, m2 = st.columns(2)
        m1.warning(f"### {monthly_sum:,.2f} \n 📈 Monthly Inward") 
        m2.warning(f"### 0.00 \n 📈 Monthly Outward")

        st.divider()
        st.subheader("Yearly Transaction")
        y1, y2 = st.columns(2)
        y1.error(f"### {yearly_sum:,.2f} \n 📊 Yearly Inward")
        y2.error(f"### 0.00 \n 📊 Yearly Outward")

    except Exception as e:
        st.error(f"❌ Dashboard Error: {e}")

# --- ၆။ Search Transactions Page ---
elif page == "🔍 Search Transactions":
    st.title("🔍 Search & Filter Transactions")
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        s_date = col1.date_input("Start Date", value=now_yangon.date())
        e_date = col2.date_input("End Date", value=now_yangon.date())
        btn_search = col3.button("Search Now", type="primary", use_container_width=True)

    try:
        res = supabase.table("inward_transactions").select("*").order("created_at", desc=True).execute()
        if res.data:
            df_search = pd.DataFrame(res.data)
            df_search['created_at'] = pd.to_datetime(df_search['created_at']).dt.tz_convert('Asia/Yangon')
            df_search['Date'] = df_search['created_at'].dt.date
            
            if btn_search:
                mask = (df_search['Date'] >= s_date) & (df_search['Date'] <= e_date)
                result_df = df_search.loc[mask]
                if not result_df.empty:
                    st.success(f"Found {len(result_df)} transactions.")
                    display_cols = ['transaction_no', 'branch', 'r_name', 'r_nrc', 's_name', 'amount', 'currency', 'total_mmk', 'Date']
                    st.dataframe(result_df[display_cols], use_container_width=True)
                else:
                    st.warning("ရွေးချယ်ထားသော ရက်စွဲအတွင်း ဒေတာမရှိပါ။")
    except Exception as e:
        st.error(f"Search Error: {e}")

# --- ၇။ Blacklist Info Page ---
elif page == "📋 Blacklist Info":
    st.title("📋 Blacklist Management")
    tab1, tab2 = st.tabs(["📊 View & Search", "⚙️ Management"])
    
    with tab1:
        search = st.text_input("🔍 Search Blacklist", placeholder="Enter Name or NRC...")
        res = supabase.table("blacklist").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            if search:
                df = df[df['name'].str.contains(search, case=False) | df['nrcno'].str.contains(search, case=False)]
            st.dataframe(df, use_container_width=True)

    with tab2:
        col_new, col_mod = st.columns(2)
        with col_new:
            st.subheader("➕ Add New")
            # NRC Dynamic Data ယူခြင်း
            nrc_data = supabase.table("myanmar_nrc_data").select("state_no, state_name, short_en").execute()
            if nrc_data.data:
                states_list = sorted(list(set([f"{i['state_no']} - {i['state_name']}" for i in nrc_data.data])))
                sel_state_full = st.selectbox("State", states_list)
                sel_state_no = sel_state_full.split(" - ")[0]
                townships = sorted(list(set([i['short_en'] for i in nrc_data.data if str(i['state_no']) == sel_state_no])))
                
                with st.form("add_bl_form"):
                    bl_name = st.text_input("Name")
                    bl_town = st.selectbox("Township Code", townships)
                    bl_id = st.text_input("ID Number")
                    bl_remark = st.text_area("Remark")
                    if st.form_submit_button("Save to Blacklist"):
                        full_nrc = f"{sel_state_no}/{bl_town}(N){bl_id}"
                        supabase.table("blacklist").insert({"name": bl_name, "nrcno": full_nrc, "remark": bl_remark}).execute()
                        st.success("Added!")
                        st.rerun()

# --- ၈။ Inward Transaction Page ---
elif page == "🏦 Inward Transaction":
    st.title("🏦 Inward Transaction Entry")
    
    # Auto-generate Transaction No
    try:
        last = supabase.table("inward_transactions").select("transaction_no").order("created_at", desc=True).limit(1).execute()
        new_no = f"{int(last.data[0]['transaction_no']) + 1:04d}" if last.data else "0001"
    except:
        new_no = "0001"

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        branch = c2.selectbox("Branch", ["Yangon", "Mandalay", "Nay Pyi Taw"])
        t_no = c3.text_input("Trans No", value=new_no)

    st.subheader("Receiver Info")
    with st.container(border=True):
        r_name = st.text_input("Receiver Name")
        r_nrc = st.text_input("Receiver NRC (Full)") # ဒီမှာ Blacklist စစ်မယ်
        amount = st.number_input("Amount", min_value=0.0)

    if st.button("💾 Save Transaction", type="primary"):
        if r_nrc:
            # Blacklist Check
            bl_check = supabase.table("blacklist").select("*").eq("nrcno", r_nrc).execute()
            if bl_check.data:
                st.error(f"🛑 STOP! {r_nrc} is BLACKLISTED!")
            else:
                supabase.table("inward_transactions").insert({
                    "branch": branch, "transaction_no": t_no, "r_name": r_name, "r_nrc": r_nrc, "amount": amount
                }).execute()
                st.success("Saved Successfully!")
                time.sleep(1)
                st.rerun()

# --- ၉။ System Control Page ---
elif page == "⚙️ System Control":
    st.title("⚙️ System Control")
    t1, t2, t3 = st.tabs(["Country", "Branch", "Users"])
    
    with t3:
        st.subheader("User Accounts")
        with st.form("new_user"):
            new_uid = st.text_input("New User ID")
            new_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Create"):
                supabase.table("user_setup").insert({"user_id": new_uid, "password": new_pwd}).execute()
                st.success("User created!")
                st.rerun()
