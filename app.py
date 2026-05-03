import streamlit as st
from datetime import datetime
import pytz
import auth
import functions

# Page Config
st.set_page_config(page_title="Remittance Admin System", layout="wide")

# Database Connection
try:
    supabase = auth.init_connection()
except Exception as e:
    st.error(f"Secrets Error: {e}")
    st.stop()

# Login စစ်ဆေးခြင်း
if auth.check_login(supabase):
    # Timezone သတ်မှတ်ခြင်း
    target_tz = pytz.timezone(st.session_state.get('target_tz', 'Asia/Yangon'))
    
    # Sidebar Menu
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.user_id}")
        st.write(f"📍 {st.session_state.sel_branch} ({st.session_state.sel_country})")
        st.divider()
        menu = st.radio("Navigation", ["📊 Dashboard", "📋 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"])
        
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # --- Page Sync Logic (ဇယားများ Dashboard တွင် မပေါ်စေရန်) ---
    if 'current_page' not in st.session_state:
        st.session_state.current_page = menu

    if st.session_state.current_page != menu:
        st.session_state.current_page = menu
        st.rerun() # Menu ပြောင်းတိုင်း Page တစ်ခုလုံးကို Clean လုပ်ပေးပါသည်

    # --- Content Display ---
    if menu == "📊 Dashboard":
        functions.show_dashboard_page(supabase, st.session_state.user)

    elif menu == "📋 Blacklist Info":
        functions.show_blacklist_page(supabase)

    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, datetime.now(target_tz))

    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)
