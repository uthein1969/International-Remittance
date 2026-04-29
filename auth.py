import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login")
        with st.form("login_form"):
            # ဒီနေရာက Variable အမည်တွေကို အောက်က .eq() ထဲမှာ ပြန်သုံးထားပါတယ်
            u_id_input = st.text_input("User ID")
            u_pw_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login", use_container_width=True)

            if submit_btn:
                try:
                    # Database ထဲက user_id နှင့် password column များကို စစ်ဆေးခြင်း
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id_input).eq("password", u_pw_input).execute()
                    
                    if res.data and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = u_id_input
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Login: ID သို့မဟုတ် Password မှားနေပါသည်။")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        return False
    return True
