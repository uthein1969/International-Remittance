import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth       # Login စစ်ဆေးရန် (auth.py)
import functions  # လုပ်ဆောင်ချက်များအတွက် (functions.py)

# --- ၁။ Setup & Configuration ---
# Page Title နဲ့ Icon သတ်မှတ်ခြင်း
st.set_page_config(page_title="Admin System", page_icon="🚀", layout="wide")

# Supabase ချိတ်ဆက်ခြင်း
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# ရန်ကုန်စံတော်ချိန် သတ်မှတ်ချက်
yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

# --- ၂။ Login Check ---
if auth.check_login(supabase):
    # Sidebar တွင် User အမည်ပြခြင်း
    st.sidebar.markdown(f"### 👤 User: **{st.session_state.get('user_id')}**")
    st.sidebar.divider()
    
    # --- Sidebar Navigation Menu ---
    st.sidebar.title("📌 Main Menu")
    menu = st.sidebar.radio("Navigate to:", [
        "🏠 Dashboard",
        "📜 Blacklist Info",
        "🏦 Inward Transaction",
        "⚙️ System Control"
    ])
    
    st.sidebar.divider()
    # Logout Button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- ၃။ Page Routing (Functions ချိတ်ဆက်မှုများ) ---
    
    if menu == "🏠 Dashboard":
        # functions.py မှ Dashboard ကို ခေါ်ယူခြင်း
        # time_placeholder ကို ပြန်ယူထားမှ Live Update လုပ်၍ရမည်
        t_placeholder = functions.show_dashboard_page(supabase, now_yangon)
        
        # Live Time Loop: Dashboard စာမျက်နှာတွင် ရှိနေသရွေ့ အချိန်ပြောင်းနေစေရန်
        while True:
            now_live = datetime.now(yangon_tz)
            time_str = now_live.strftime("%Y-%m-%d %H:%M:%S")
            t_placeholder.markdown(f"**Last Updated:** `{time_str}` (Yangon Time)")
            time.sleep(1) # ၁ စက္ကန့်ခြား Update လုပ်ခြင်း
        
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif menu == "🏦 Inward Transaction":
        # Inward အတွက် လက်ရှိအချိန်အမှန်ကို ထပ်မံရယူပေးခြင်း
        current_now = datetime.now(yangon_tz)
        functions.show_inward_page(supabase, current_now)
        
    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)

# --- ၄။ Login မဝင်ရသေးပါက (auth.py မှ ကိုင်တွယ်ပါသည်) ---
