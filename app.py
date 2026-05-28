import streamlit as st
import pytz
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide")

# ---------------- TIME ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- SUPABASE ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- TEST ----------------
st.title("🧼 STEP 4 DATABASE TEST")

st.write(now_yangon.strftime("%Y-%m-%d %H:%M:%S"))

# ---------------- DATABASE QUERY ----------------
try:

    response = supabase.table("user_setup").select("*").execute()

    st.success("✅ Database query successful")

    st.write(response.data)

except Exception as e:

    st.error(f"❌ Database Error: {e}")