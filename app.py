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
    st.title("📈 Transaction Dashboard")
    st.success(f"Welcome {st.session_state.username}")

    st.markdown(f"Last Updated: {now_yangon.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        df = pd.DataFrame(res.data or [])

        if df.empty:
            st.warning("No transactions found")
        else:
            st.dataframe(df)

    except Exception as e:
        st.error(f"DB Error: {e}")

# ================= LOGIN GATE =================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= AFTER LOGIN ONLY =================
menu = st.sidebar.radio(
    "📌 Menu",
    ["📊 Dashboard", "🔍 Search", "🏦 Inward", "📋 Blacklist", "⚙️ System"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

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

    # ================= SESSION INIT =================
    if "amount" not in st.session_state:
        st.session_state.amount = 0.0

    # ================= FORM =================
    with st.form("inward_form"):
        col1, col2 = st.columns(2)

        with col1:
            branch = st.text_input("Branch")
            r_name = st.text_input("Receiver Name")
            r_nrc = st.text_input("Receiver NRC")
            r_phone = st.text_input("Receiver Phone")

        with col2:
            s_name = st.text_input("Sender Name")
            currency = st.selectbox("Currency", ["THB", "USD", "SGD"])
            amount = st.number_input("Amount", min_value=0.0, step=0.01)

        mmk_rate = st.number_input("MMK Rate", min_value=0.0, step=0.01)
        mmk_allow = st.number_input("MMK Allowance", min_value=0.0, step=0.01)

        total_mmk = (amount * mmk_rate) + mmk_allow
        st.info(f"Total MMK: {total_mmk:,.2f}")

        submit = st.form_submit_button("💾 Save Transaction")

    # ================= SAVE =================
    if submit:
        try:
            data = {
                "branch": branch,
                "r_name": r_name,
                "r_nrc": r_nrc,
                "r_phone": r_phone,
                "s_name": s_name,
                "currency": currency,
                "amount": float(amount),
                "mmk_rate": float(mmk_rate),
                "mmk_allowance": float(mmk_allow),
                "total_mmk": float(total_mmk),
            }

            res = supabase.table("inward_transactions").insert(data).execute()

            if res.data:
                st.success("✅ Transaction Saved Successfully")
                st.balloons()
            else:
                st.error("❌ Save Failed")

        except Exception as e:
            st.error(f"Save Error: {e}")

elif menu == "📋 Blacklist":
    st.title("Blacklist Module")

elif menu == "⚙️ System":
    st.title("System Module")

