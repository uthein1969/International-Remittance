import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth       # auth.py
import functions  # functions.py

# --- Page Setup ---
st.set_page_config(page_title="International Remittance", page_icon="🏦", layout="wide")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

# --- Security Check ---
if auth.check_login(supabase):
    st.sidebar.write(f"👤 User: **{st.session_state.get('user_id')}**")
    
    st.sidebar.title("📌 Main Menu")
    menu = st.sidebar.radio("Navigate to:", [
        "🏠 Dashboard", "📜 Blacklist Info", "🏦 Inward Transaction", "⚙️ System Control"
    ])
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- Page Routing ---
    if menu == "🏠 Dashboard":
        # Line 35: functions.py မှ return ပြန်လာသော variable နှစ်ခုကို လက်ခံခြင်း[cite: 1]
        mm_ptr, c_ptrs = functions.show_dashboard_page(supabase, now_yangon)
        
        # Live Time Loop
        while True:
            # ၁။ မြန်မာစံတော်ချိန် Update
            now_mm = datetime.now(yangon_tz)
            mm_ptr.markdown(f"### 🕒 `{now_mm.strftime('%I:%M:%S %p')}`")
            
            # ၂။ နိုင်ငံတကာအချိန်များ Update[cite: 1]
            for c_name, c_info in c_ptrs.items():
                try:
                    target_tz = pytz.timezone(c_info['tz'])
                    now_target = datetime.now(target_tz)
                    c_info['ptr'].write(f"🕒 {now_target.strftime('%I:%M:%S %p')}")
                except:
                    c_info['ptr'].write("⚠️ Timezone Error")

            time.sleep(1)
        
    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, datetime.now(yangon_tz))
        
    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)
