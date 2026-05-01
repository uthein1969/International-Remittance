import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth       # Login စစ်ဆေးရန်
import functions  # လုပ်ဆောင်ချက်များအတွက်

# --- Setup ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# ရန်ကုန်စံတော်ချိန် သတ်မှတ်ချက်
yangon_tz = pytz.timezone('Asia/Yangon')

# --- Login Check ---
if auth.check_login(supabase):
    # Sidebar Success message
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
        
        # Live Time ပြသရန် နေရာလွတ်တစ်ခု ဖန်တီးခြင်း
        time_placeholder = st.empty()
        
        # Dashboard တွင်ရှိနေစဉ် အချိန်ကို တစ်စက္ကန့်ချင်း Update လုပ်ပေးမည့် Loop
        # (တခြား Menu ကို နှိပ်လိုက်လျှင် ဤ Loop သည် အလိုအလျောက် ရပ်သွားမည်ဖြစ်သည်)
        while True:
            now_live = datetime.now(yangon_tz)
            time_str = now_live.strftime("%Y-%m-%d %H:%M:%S")
            
            # ပုံ ပါအတိုင်း ပြသခြင်း
            time_placeholder.write(f"ယနေ့အချိန်: {time_str}")
            
            # ၁ စက္ကန့်စောင့်ပြီးနောက် ပြန်လည် Update လုပ်ခြင်း
            time.sleep(1)
        
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif menu == "🏦 Inward Transaction":
        # Inward Transaction အတွက် လက်ရှိအချိန်ကို ယူသွားပေးခြင်း
        now_yangon = datetime.now(yangon_tz)
        functions.show_inward_page(supabase, now_yangon)
        
    elif menu == "⚙️ User Setup":
        functions.show_user_setup(supabase)
