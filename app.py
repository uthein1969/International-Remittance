import streamlit as st
import pytz
from datetime import datetime
from supabase import create_client, Client
import auth       # Login စစ်ဆေးရန်
import functions  # လုပ်ဆောင်ချက်များအတွက်

# --- Setup ---
yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# --- Login Check ---
if auth.check_login(supabase):
    # Sidebar Sidebar Success message
    st.sidebar.write(f"👤 User: **{st.session_state.get('user_id')}**")
    
    # --- Sidebar Navigation ---
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("Navigate to:", [
        "🏠 Dashboard",
        "📜 Blacklist Info",
        "🏦 Inward Transaction",
        "⚙️ User Setup"
    ])
    
    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- Page Routing ---
    if menu == "🏠 Dashboard":
        st.title("🚀 Welcome to Admin System")
        st.write(f"ယနေ့အချိန်: {now_yangon.strftime('%Y-%m-%d %H:%M:%S')}")
        
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, now_yangon)
        
    elif menu == "⚙️ User Setup":
        functions.show_user_setup(supabase)
