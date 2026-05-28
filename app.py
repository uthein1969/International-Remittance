import streamlit as st
import pytz
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------- TIME ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- TEST ----------------
st.title("🧼 STEP 1 SUCCESS")
st.success("Imports working")

st.write(now_yangon.strftime("%Y-%m-%d %H:%M:%S"))