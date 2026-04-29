import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login")
        with st.form("login_form"):
            u_id = st.text_input("User ID")
            u_pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                res = supabase.table("user_setup").select("*").eq("user_id", u_id).eq("password", u_pw).execute()
                if res.data:
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Invalid Login")
        return False
    return True
