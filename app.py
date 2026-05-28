import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from supabase import create_client

# ================= PAGE CONFIG =================
st.set_page_config(page_title="International Remittance", layout="wide")

# ================= SAFE SUPABASE INIT =================
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

# STEP 2 — LOGIN MODULE (SEPARATE & SAFE)
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
                    return

            st.error("Invalid credentials")

        except Exception as e:
            st.error(f"DB Error: {e}")

# STEP 3 — DASHBOARD (MINIMUM SAFE VERSION)
def dashboard():
    st.title("📈 Transaction Dashboard")

    st.success(f"Welcome {st.session_state.username}")

    st.markdown(
        f"Last Updated: {now_yangon.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    if supabase is None:
        st.error("Supabase not connected")
        return

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        data = res.data or []

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("No transactions found")
        else:
            st.dataframe(df)

    except Exception as e:
        st.error(f"DB Error: {e}")

# STEP 4 — MAIN ROUTER
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()