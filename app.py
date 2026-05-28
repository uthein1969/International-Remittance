import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from supabase import create_client

# ================= CONFIG =================
st.set_page_config(page_title="International Remittance", layout="wide")

# ================= SUPABASE =================
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= TIME =================
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ================= LOGIN =================
def login_page():
    st.title("🔐 Admin Login")

    user = st.text_input("User ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if supabase is None:
            st.error("Supabase not connected")
            return

        try:
            res = supabase.table("user_setup").select("*").execute()
            users = res.data or []

            for u in users:
                if u["user_id"] == user and u["password"] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()

            st.error("Invalid credentials")

        except Exception as e:
            st.error(f"DB Error: {e}")

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Transaction Dashboard")

    if supabase is None:
        st.error("Supabase not connected")
        return

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        data = res.data or []

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("No transactions found")
            return

        # ================= DATE CONVERT =================
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["Date"] = df["created_at"].dt.date
        df["Month"] = df["created_at"].dt.to_period("M")
        df["Year"] = df["created_at"].dt.year

        # ================= FILTER TABS =================
        tab1, tab2, tab3 = st.tabs(["📅 Daily", "📆 Monthly", "📊 Yearly"])

        # ================= DAILY =================
        with tab1:
            st.subheader("📅 Daily Report")

            selected_date = st.date_input("Select Date")

            daily_df = df[df["Date"] == selected_date]

            st.metric("Transactions", len(daily_df))
            st.metric("Total MMK", f"{daily_df['total_mmk'].sum():,.2f}")

            st.dataframe(daily_df)

        # ================= MONTHLY =================
        with tab2:
            st.subheader("📆 Monthly Report")

            month_list = sorted(df["Month"].astype(str).unique())
            selected_month = st.selectbox("Select Month", month_list)

            monthly_df = df[df["Month"].astype(str) == selected_month]

            st.metric("Transactions", len(monthly_df))
            st.metric("Total MMK", f"{monthly_df['total_mmk'].sum():,.2f}")

            st.dataframe(monthly_df)

        # ================= YEARLY =================
        with tab3:
            st.subheader("📊 Yearly Report")

            year_list = sorted(df["Year"].unique())
            selected_year = st.selectbox("Select Year", year_list)

            yearly_df = df[df["Year"] == selected_year]

            st.metric("Transactions", len(yearly_df))
            st.metric("Total MMK", f"{yearly_df['total_mmk'].sum():,.2f}")

            st.dataframe(yearly_df)

        # ================= SUMMARY CARDS =================
        st.divider()
        st.subheader("📌 Overall Summary")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Total Transactions", len(df))

        with c2:
            st.metric("Total MMK Volume", f"{df['total_mmk'].sum():,.2f}")

        with c3:
            st.metric("Avg Transaction", f"{df['total_mmk'].mean():,.2f}")

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

# ================= LOGIN GATE =================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= AFTER LOGIN ONLY =================

menu = st.sidebar.radio(
    "📌 Menu",
    ["📊 Dashboard", "🔍 Search", "🏦 Inward", "📋 Blacklist", "⚙️ System"]
)

# Logout (SEPARATE - NOT INSIDE ANY IF)
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ================= ROUTER =================
if menu == "📊 Dashboard":
    dashboard()

elif menu == "🔍 Search":
    st.title("🔍 Search Transactions")

    if supabase is None:
        st.error("Supabase not connected")
        st.stop()

    # FILTER UI ALWAYS SHOW
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Start Date")

    with col2:
        end_date = st.date_input("End Date")

    with col3:
        search_btn = st.button("Search")

    # DEFAULT
    filtered_df = pd.DataFrame()

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        data = res.data or []

        if len(data) > 0:
            df = pd.DataFrame(data)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["Date"] = df["created_at"].dt.date

            if search_btn:
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

            filtered_df = df

    except Exception as e:
        st.error(f"Search Error: {e}")

    # ALWAYS SHOW RESULT AREA
    st.subheader("📊 Results")

    if not filtered_df.empty:
        st.metric("Total Transactions", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "transactions.csv", "text/csv")
    else:
        st.info("No data found / no search result")


elif menu == "🏦 Inward":
    st.title("🏦 Inward Transaction")

    if supabase is None:
        st.error("Supabase not connected")
        st.stop()

    from datetime import datetime

    # ================= LIVE TIME =================
    now = datetime.now()
    display_time = now.strftime("%Y-%m-%d %H:%M:%S")
    save_time = now.strftime("%d%m%Y%H%M%S")  # DDMMYYYYHHMMSS

    st.info(f"🕒 Current Time: {display_time}")

    # ================= FORM =================
    with st.form("inward_form", clear_on_submit=True):

        st.subheader("🔵 Receiver Info")
        r_name = st.text_input("Receiver Name")
        r_nrc = st.text_input("Receiver NRC")
        r_phone = st.text_input("Phone")
        r_address = st.text_input("Address")
        r_state = st.text_input("State")
        r_withdraw_point = st.text_input("Withdraw Point")
        r_remark = st.text_area("Remark")

        st.subheader("🟢 Sender Info")
        s_name = st.text_input("Sender Name")
        s_id = st.text_input("Sender ID / Passport")

        # ✅ Country FIRST, then Branch (FIXED)
        s_country = st.text_input("Country")

        branch = st.selectbox(
            "Branch",
            ["Yangon", "Mandalay", "Nay Pyi Taw"]
        )

        currency = st.selectbox("Currency", ["THB", "USD", "SGD"])

        amount = st.number_input("Amount", min_value=0.0)
        mmk_rate = st.number_input("MMK Rate", min_value=0.0)
        mmk_allowance = st.number_input("MMK Allowance", min_value=0.0)

        usd_equiv = st.number_input("USD Equivalent", min_value=0.0)

        total_mmk = (amount * mmk_rate) + mmk_allowance

        st.markdown(f"### 💰 Total MMK: {total_mmk:,.2f}")

        submit = st.form_submit_button("💾 Save Transaction")

    # ================= SAVE =================
    if submit:

        try:
            # 🔴 BLACKLIST CHECK
            check = supabase.table("blacklist") \
                .select("*") \
                .eq("nrcno", r_nrc) \
                .execute()

            if check.data:
                st.error("❌ This user is BLACKLISTED")
                st.stop()

            data = {
                "transaction_no": save_time,
                "branch": branch,
                "r_name": r_name,
                "r_nrc": r_nrc,
                "r_phone": r_phone,
                "r_address": r_address,
                "r_state": r_state,
                "r_withdraw_point": r_withdraw_point,
                "r_remark": r_remark,

                "s_name": s_name,
                "s_id": s_id,
                "s_country": s_country,

                "currency": currency,
                "amount": amount,
                "mmk_rate": mmk_rate,
                "mmk_allowance": mmk_allowance,
                "usd_equiv": usd_equiv,
                "total_mmk": total_mmk,

                "created_at": display_time
            }

            res = supabase.table("inward_transactions").insert(data).execute()

            if res.data:
                st.success("✅ Transaction Saved Successfully")
                st.code(f"Transaction No: {save_time}")

            else:
                st.error("❌ Save Failed")

        except Exception as e:
            st.error(f"Database Error: {e}")

elif menu == "📋 Blacklist":
    st.title("Blacklist Module")

elif menu == "⚙️ System":
    st.title("System Module")

