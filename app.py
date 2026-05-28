import streamlit as st
import pytz
from datetime import datetime
from supabase import create_client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- TIME ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- SUPABASE ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

# ---------------- LOGIN ----------------
if not st.session_state["logged_in"]:

    st.title("🔐 Admin Login System")

    input_user = st.text_input("User ID")
    input_pass = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn"):

        try:

            response = supabase.table("user_setup").select("*").execute()

            users = response.data

            found = False

            for user in users:

                if (
                    user["user_id"] == input_user
                    and user["password"] == input_pass
                ):

                    found = True
                    break

            if found:

                st.session_state["logged_in"] = True
                st.session_state["username"] = input_user

                st.success("✅ Login Successful")
                st.rerun()

            else:
                st.error("❌ Invalid User ID or Password")

        except Exception as e:

            st.error(f"Database Error: {e}")

    st.stop()

# ---------------- DASHBOARD ----------------
st.title("📈 Transaction Dashboard")

st.success(f"Welcome {st.session_state['username']} 👋")

st.markdown(
    f"**Last Updated:** {now_yangon.strftime('%Y-%m-%d %H:%M:%S')} (Yangon Time)"
)

# ---------------- LOGOUT ----------------
if st.button("Logout", key="logout_btn"):

    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

    st.rerun()