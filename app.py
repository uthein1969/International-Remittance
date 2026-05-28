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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ================= TIME =================
yangon = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon)

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

            for u in res.data or []:
                if u["user_id"] == user and u["password"] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                    return

            st.error("Invalid credentials")

        except Exception as e:
            st.error(f"DB Error: {e}")

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Dashboard")

    if supabase is None:
        st.error("No DB connection")
        return

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        df = pd.DataFrame(res.data or [])

        if df.empty:
            st.warning("No data")
            return

        df["created_at"] = pd.to_datetime(df["created_at"])
        df["Date"] = df["created_at"].dt.date
        df["Month"] = df["created_at"].dt.to_period("M").astype(str)
        df["Year"] = df["created_at"].dt.year

        st.dataframe(df)

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

# ================= INWARD =================
def inward():
    st.title("🏦 Inward Transaction")

    st.info(f"🕒 {now_yangon.strftime('%d-%m-%Y %H:%M:%S')}")

    if supabase is None:
        st.error("No DB connection")
        return

    # AUTO NO
    try:
        last = supabase.table("inward_transactions") \
            .select("transaction_no") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        new_no = "0001"
        if last.data:
            new_no = str(int(last.data[0]["transaction_no"]) + 1).zfill(4)
    except:
        new_no = "0001"

    # FORM
    with st.form("inward_form"):
        branch = st.selectbox("Branch", ["Yangon", "Mandalay", "NPT"])

        st.subheader("Receiver")
        r_name = st.text_input("Name")
        r_nrc = st.text_input("NRC")
        r_phone = st.text_input("Phone")
        r_address = st.text_input("Address")
        r_state = st.text_input("State")
        r_point = st.text_input("Withdraw Point")

        st.subheader("Sender")
        s_name = st.text_input("Sender Name")
        s_id = st.text_input("ID")
        s_country = st.text_input("Country")

        currency = st.selectbox("Currency", ["THB", "USD", "SGD"])
        amount = st.number_input("Amount", 0.0)
        rate = st.number_input("MMK Rate", 0.0)
        allow = st.number_input("MMK Allowance", 0.0)

        total = (amount * rate) + allow

        st.markdown(f"### Total: {total:,.2f}")

        submitted = st.form_submit_button("Save")

    # SAVE
    if submitted:
        try:
            check = supabase.table("blacklist").select("*").eq("nrcno", r_nrc).execute()

            if check.data:
                st.error("BLACKLISTED")
                return

            supabase.table("inward_transactions").insert({
                "transaction_no": new_no,
                "branch": branch,
                "r_name": r_name,
                "r_nrc": r_nrc,
                "r_phone": r_phone,
                "r_address": r_address,
                "r_state": r_state,
                "r_withdraw_point": r_point,
                "s_name": s_name,
                "s_id": s_id,
                "s_country": s_country,
                "currency": currency,
                "amount": amount,
                "mmk_rate": rate,
                "mmk_allowance": allow,
                "total_mmk": total,
                "created_at": now_yangon.strftime("%d%m%Y%H%M%S")
            }).execute()

            st.success("Saved Successfully")
            st.rerun()

        except Exception as e:
            st.error(f"Save Error: {e}")

# ================= ROUTER (ONLY ONCE) =================
if not st.session_state.logged_in:
    login_page()
    st.stop()

menu = st.sidebar.radio(
    "Menu",
    ["📊 Dashboard", "🏦 Inward"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

if menu == "📊 Dashboard":
    dashboard()

elif menu == "🏦 Inward":
    inward()