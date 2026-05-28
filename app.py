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

    # ================= SESSION DEFAULT =================
    if "show_slip" not in st.session_state:
        st.session_state.show_slip = False

    if "slip" not in st.session_state:
        st.session_state.slip = {}

    # ================= GET LAST TRANSACTION NO =================
    try:
        last = supabase.table("inward_transactions") \
            .select("transaction_no") \
            .order("created_at", desc=True) \
            .limit(1).execute()

        if last.data:
            last_no = int(last.data[0]["transaction_no"])
            new_no = f"{last_no + 1:04d}"
        else:
            new_no = "0001"
    except:
        new_no = "0001"

    # ================= FORM =================
    if not st.session_state.show_slip:

        st.subheader("🔵 Receiver Info")

        col1, col2 = st.columns(2)
        r_name = col1.text_input("Receiver Name")
        r_nrc = col2.text_input("Receiver NRC")

        r_phone = st.text_input("Phone")
        r_address = st.text_input("Address")

        col3, col4 = st.columns(2)
        r_state = col3.text_input("State")
        r_point = col4.text_input("Withdraw Point")

        st.subheader("🟢 Sender Info")

        s_name = st.text_input("Sender Name")
        s_id = st.text_input("Sender ID")
        s_country = st.text_input("Country")

        col5, col6, col7 = st.columns(3)
        currency = col5.selectbox("Currency", ["THB", "USD", "SGD"])
        amount = col6.number_input("Amount", min_value=0.0)
        rate = col7.number_input("MMK Rate", min_value=0.0)

        allow = st.number_input("Allowance", min_value=0.0)

        total_mmk = (amount * rate) + allow

        st.markdown(f"### 💰 Total MMK: {total_mmk:,.2f}")

        branch = st.selectbox("Branch", ["Yangon", "Mandalay", "NPT"])
        trans_no = st.text_input("Transaction No", value=new_no)

        # ================= SAVE =================
        if st.button("💾 Save Transaction"):
            try:
                # blacklist check
                bl = supabase.table("blacklist") \
                    .select("*") \
                    .eq("nrcno", r_nrc) \
                    .execute()

                if bl.data:
                    st.error("❌ Blacklisted Customer")
                    st.stop()

                data = {
                    "transaction_no": trans_no,
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
                    "total_mmk": total_mmk,
                }

                res = supabase.table("inward_transactions").insert(data).execute()

                if res.data:
                    st.session_state.slip = data
                    st.session_state.show_slip = True
                    st.rerun()

            except Exception as e:
                st.error(f"Save Error: {e}")

    # ================= SLIP =================
    else:
        sd = st.session_state.slip

        st.success("Saved Successfully 🎉")

        st.markdown("### 📄 Payout Slip")

        st.write("Transaction No:", sd["transaction_no"])
        st.write("Receiver:", sd["r_name"])
        st.write("Sender:", sd["s_name"])
        st.write("Total:", f"{sd['total_mmk']:,.2f} MMK")

        if st.button("🔄 New Transaction"):
            st.session_state.show_slip = False
            st.session_state.slip = {}
            st.rerun()

elif menu == "📋 Blacklist":
    st.title("Blacklist Module")

elif menu == "⚙️ System":
    st.title("System Module")

