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
    st.title("Inward Module")

elif menu == "📋 Blacklist":
    st.title("Blacklist Module")

elif menu == "⚙️ System":
    st.title("System Module")

