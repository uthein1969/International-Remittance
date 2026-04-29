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
    st.sidebar.success(f"Logged in as: {st.session_state['user_id']}")
    # Login အောင်မြင်မှ Sidebar Menu ပြမည်
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Go to:", ["📋 Blacklist Info", "🏦 Inward Transaction"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # Page ရွေးချယ်မှုအလိုက် Function များကို ခေါ်ယူခြင်း
    if page == "📋 Blacklist Info":
        functions.show_blacklist_page(supabase)
    elif page == "🏦 Inward Transaction":
        functions.show_inward_page(supabase)
