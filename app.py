import streamlit as st
from datetime import datetime
import pytz
import auth
import functions

# Page Config
st.set_page_config(page_title="Remittance Admin System", layout="wide")
yangon_tz = pytz.timezone('Asia/Yangon')

# --- Menu Selection ---
with st.sidebar:
    st.title("Main Menu")
    menu = st.radio("Navigation", ["📊 Dashboard", "📋 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- Page Sync Logic (ဇယားများ Dashboard တွင် ထပ်မနေစေရန်) ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = menu

if st.session_state.current_page != menu:
    st.session_state.current_page = menu
    st.rerun() # Menu ပြောင်းတိုင်း အကုန် Clear လုပ်ပေးပါသည်

# --- Database Connection Fix (AttributeError ဖြေရှင်းချက်) ---
try:
    # auth.py ထဲတွင် init_supabase သို့မဟုတ် init_connection ရှိမရှိ စစ်ဆေးခြင်း
    if hasattr(auth, 'init_supabase'):
        supabase = auth.init_supabase()
    elif hasattr(auth, 'init_connection'):
        supabase = auth.init_connection()
    else:
        st.error("Error: auth.py ထဲတွင် connection function ရှာမတွေ့ပါ။")
        st.stop()
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# --- Content Area ---
if menu == "📊 Dashboard":
    now_yangon = datetime.now(yangon_tz)
    functions.show_dashboard_page(supabase, now_yangon)

elif menu == "📋 Blacklist Info":
    functions.show_blacklist_page(supabase)

elif menu == "🏦 Inward Transaction":
    functions.show_inward_page(supabase, datetime.now(yangon_tz))

elif menu == "⚙️ System Control":
    functions.show_system_control(supabase)
