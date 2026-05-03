import streamlit as st
from supabase import create_client
import functions
import auth
from datetime import datetime

# Supabase Connection
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
supabase = create_client(url, key)

# Session State Initialize
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.logged_in:
    # Login Page ခေါ်ခြင်း
    auth.login_page(supabase)
else:
    # Sidebar Navigation
    st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
    st.sidebar.write(f"📍 {st.session_state.user.get('branch', 'Main Branch')} ({st.session_state.user.get('country', 'Thailand')})")
    
    menu = st.sidebar.radio("Navigation", ["Dashboard", "Blacklist Info", "Inward Transaction", "System Control"])
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # Dashboard Page ခေါ်ခြင်း (AttributeError မတက်အောင် user data ထည့်ပေးထားသည်)
    if menu == "Dashboard":
        functions.show_dashboard_page(supabase, st.session_state.user)
    elif menu == "Blacklist Info":
        functions.show_blacklist_page(supabase)
    # ... ကျန်ရှိသော Menu များ ...
