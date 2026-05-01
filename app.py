import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth, functions

st.set_page_config(page_title="Remittance Admin System", layout="wide")

# Supabase Connect
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

yangon_tz = pytz.timezone('Asia/Yangon')

if auth.check_login(supabase):
    # Sidebar ပြသခြင်း
    st.sidebar.markdown(f"👤 User: **{st.session_state.user_id}**")
    st.sidebar.markdown(f"📍 Branch: **{st.session_state.sel_branch}**")
    
    menu = st.sidebar.radio("Main Menu", ["📊 Dashboard", "📜 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"])
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "📊 Dashboard":
        now_yangon = datetime.now(yangon_tz)
        mm_ptr, intl_ptr = functions.show_dashboard_page(supabase, now_yangon)
        
        # ရွေးချယ်ခဲ့သော နိုင်ငံ၏ Timezone ကိုယူခြင်း
        tz_id = st.session_state.get('target_tz', 'Asia/Yangon')
        try:
            target_tz = pytz.timezone(tz_id)
        except:
            target_tz = pytz.timezone('UTC')

        # Live Update Loop
        while True:
            t_mm = datetime.now(yangon_tz).strftime('%I:%M:%S %p')
            t_intl = datetime.now(target_tz).strftime('%I:%M:%S %p')
            
            mm_ptr.markdown(f"## `{t_mm}`")
            intl_ptr.markdown(f"## `{t_intl}`")
            time.sleep(1)
            
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, datetime.now(yangon_tz))
    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)
