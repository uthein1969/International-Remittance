import streamlit as st
from supabase import create_client, Client
import auth       # auth.py ကို ခေါ်ယူခြင်း
import functions  # functions.py ကို ခေါ်ယူခြင်း

# Supabase Connection
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# Login စစ်ဆေးခြင်း
if auth.check_login(supabase):
    st.sidebar.success(f"Logged in as: {st.session_state.get('user_id', 'User')}")
    
    # Sidebar Menu ပြန်လည်တည်ဆောက်ခြင်း
    st.sidebar.title("Menu")
    
    # သင်အသုံးပြုမည့် Menu List ကို ဤနေရာတွင် ပြန်ထည့်ပါ
    page = st.sidebar.radio("Go to:", [
        "📜 Blacklist Info", 
        "🏦 Inward Transaction",
        "📊 Reports",           # ထပ်တိုးလိုသော Menu များ
        "⚙️ Settings"
    ])

    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # ရွေးချယ်လိုက်သော Page အလိုက် Function များ ခေါ်ယူခြင်း
    if page == "📜 Blacklist Info":
        functions.show_blacklist_page(supabase)
        
    elif page == "🏦 Inward Transaction":
        functions.show_inward_page(supabase)
        
    # အခြား Menu များရှိပါက functions ထဲတွင် ဆောက်ပြီး ဤနေရာတွင် ခေါ်နိုင်ပါသည်
    # elif page == "📊 Reports":
    #     functions.show_reports_page(supabase)
