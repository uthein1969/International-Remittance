import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        with st.form("login_form"):
            u_id_input = st.text_input("User ID")
            u_pw_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login")

            if submit_btn:
                try:
                    # အောက်ပါ Line ကို အတိအကျဖြစ်အောင် ပြင်ပါ (Password စစ်ဆေးခြင်း ပါရပါမည်)
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id_input.strip()).eq("password", u_pw_input.strip()).execute()
                    
                    if res.data and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = u_id_input.strip()
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
                except Exception as e:
                    st.error(f"Login Error: {e}")
        return False
    return True
