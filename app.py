import streamlit as st
from supabase import create_client
import functions
import auth

# Supabase Settings
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase = create_client(url, key)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth.login_page(supabase)
else:
    # Sidebar တွင် Branch နှင့် Country ပြန်လည်ပြသခြင်း
    user = st.session_state.user
    st.sidebar.write(f"👤 Welcome, {user['username']}")
    # Table ထဲက column အမည်အတိုင်း branch နှင့် country ကို ယူပါသည်
    st.sidebar.info(f"📍 {user.get('branch', 'N/A')} ({user.get('country', 'N/A')})")
    
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Blacklist Info", "Inward Transaction", "System Control"])
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    if menu == "Dashboard":
        functions.show_dashboard_page(supabase, st.session_state.user)
    elif menu == "Blacklist Info":
        functions.show_blacklist_page(supabase)
    # ... ကျန် menu များ ...
