import streamlit as st
import pytz
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide")

# ---------------- TIME ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- SECRETS ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# ---------------- CREATE CLIENT ----------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- TEST ----------------
st.title("🧼 STEP 3 SUCCESS")
st.success("Supabase client created successfully")

st.write(now_yangon.strftime("%Y-%m-%d %H:%M:%S"))