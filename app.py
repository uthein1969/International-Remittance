import streamlit as st
import pytz
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide")

# ---------------- TIME ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- TEST ----------------
st.title("🧼 STEP 2 SUCCESS")
st.success("Supabase import working")

st.write(now_yangon.strftime("%Y-%m-%d %H:%M:%S"))