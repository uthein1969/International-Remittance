import streamlit as st
import pytz
from datetime import datetime
import time
from supabase import create_client, Client
import auth, functions

st.set_page_config(page_title="Remittance Admin", layout="wide")

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

    # --- Page Content Logic ---
    
    if menu == "📊 Dashboard":
        # Dashboard Content ကို အရင်ပြပါ
        now_yangon = datetime.now(yangon_tz)
        mm_ptr, intl_ptr = functions.show_dashboard_page(supabase, now_yangon)
        
        # Timezone ID ယူခြင်း
        tz_id = st.session_state.get('target_tz', 'Asia/Yangon')
        try:
            target_tz = pytz.timezone(tz_id)
        except:
            target_tz = pytz.timezone('UTC')

        # Live Time Loop (Dashboard menu ဖြစ်နေမှသာ ပတ်ရန်)
        # Placeholder သုံးပြီး update လုပ်ခြင်းက ပိုမြန်ဆန်စေပါတယ်
        while menu == "📊 Dashboard":
            t_mm = datetime.now(yangon_tz).strftime('%I:%M:%S %p')
            t_intl = datetime.now(target_tz).strftime('%I:%M:%S %p')
            
            mm_ptr.markdown(f"## `{t_mm}`")
            intl_ptr.markdown(f"## `{t_intl}`")
            
            time.sleep(1)
            # အကယ်၍ sidebar က menu ပြောင်းသွားရင် loop ထဲက ထွက်ပေးရပါမယ်
            # သို့သော် Streamlit သည် widget ပြောင်းလျှင် အပေါ်မှ ပြန် run သဖြင့် 
            # ဤ loop သည် menu ပြောင်းလျှင် အလိုအလျောက် ရပ်သွားပါလိမ့်မည်။

    elif menu == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)

    elif menu == "🏦 Inward Transaction":
        functions.show_inward_page(supabase, datetime.now(yangon_tz))

    elif menu == "⚙️ System Control":
        functions.show_system_control(supabase)
