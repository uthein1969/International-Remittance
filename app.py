import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth       
import functions  # ခွဲထုတ်ထားသော function များကို ခေါ်ယူခြင်း

# --- Setup ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)
yangon_tz = pytz.timezone('Asia/Yangon')

# --- Login Check ---
if auth.check_login(supabase):
    st.sidebar.write(f"👤 User: **{st.session_state.get('user_id')}**")
    
    st.sidebar.title("Main Menu")
    menu = st.sidebar.radio("Navigate to:", [
        "🏠 Dashboard",
        "📜 Blacklist Info",
        "🏦 Inward Transaction",
        "⚙️ System Control" # Menu အမည်ကို System Control ဟု ပြောင်းထားပါသည်
    ])
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- Page Routing (Functions များကို လှမ်းခေါ်ခြင်း) ---
    if menu == "🏠 Dashboard":
        st.title("🚀 Welcome to Admin System")
        time_placeholder = st.empty()
        while True:
            now_live = datetime.now(yangon_tz)
            time_placeholder.write(f"ယနေ့အချိန်: {now_live.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(1)
        
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase) # Function ခေါ်ခြင်း
        
    elif menu == "🏦 Inward Transaction":
        now_yangon = datetime.now(yangon_tz)
        functions.show_inward_page(supabase, now_yangon) # Function ခေါ်ခြင်း
        
    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase) # Function ခေါ်ခြင်း
