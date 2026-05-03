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

# --- Page Refresh Logic (ဇယားတွေ Dashboard မှာ ကပ်မပါလာစေရန်) ---
if 'last_menu' not in st.session_state:
    st.session_state.last_menu = menu

if st.session_state.last_menu != menu:
    st.session_state.last_menu = menu
    st.rerun() # Menu ပြောင်းတာနဲ့ အရင် page widget တွေကို အကုန်ရှင်းပစ်ပါတယ်

# --- Database Connection ---
# အကယ်၍ auth.py ထဲမှာ နာမည်က init_connection ဆိုရင် ဒါကို သုံးပါ
# အကယ်၍ init_supabase ဆိုရင် အောက်ကစာကြောင်းကို အဲဒီအတိုင်း ပြင်ပေးပါ
try:
    supabase = auth.init_supabase() 
except AttributeError:
    supabase = auth.init_connection()

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
