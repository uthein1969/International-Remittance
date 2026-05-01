import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth, functions

# Setup
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)
yangon_tz = pytz.timezone('Asia/Yangon')

if auth.check_login(supabase):
    st.sidebar.title("🚀 Main Menu")
    menu = st.sidebar.radio("Go to:", ["📊 Dashboard", "📜 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"])
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "📊 Dashboard":
        now_yangon = datetime.now(yangon_tz)
        mm_ptr, intl_ptr = functions.show_dashboard_page(supabase, now_yangon)
        
        # Live Time Loop
        target_timezone = pytz.timezone(st.session_state.get('target_tz', 'UTC'))
        
        while True:
            t_mm = datetime.now(yangon_tz).strftime('%I:%M:%S %p')
            t_intl = datetime.now(target_timezone).strftime('%I:%M:%S %p')
            
            mm_ptr.markdown(f"### `{t_mm}`")
            intl_ptr.markdown(f"### `{t_intl}`")
            
            time.sleep(1)
            
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, datetime.now(yangon_tz))
        
    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)
