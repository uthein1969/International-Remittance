import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login")
        with st.form("login_form"):
            
            u_id_input = st.text_input("User ID")
            u_pw_input = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login", use_container_width=True)

            if submit_btn:
                try:
                    # Database ထဲက user_id နှင့် password column များကို စစ်ဆေးခြင်း
                    # user_id နှင့် u_id_input တို့ အတိအကျတူရပါမည်
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id_input).eq("password", u_pw_input).execute()
                    
                    if res.data and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = u_id_input
                        st.success("Login Successful!")
                        st.rerun()
                    else:
                        # အကယ်၍ ဝင်မရသေးရင် ရိုက်ထည့်လိုက်တဲ့ ID/PW ကို စစ်ဖို့ error ထုတ်ကြည့်ပါမယ်
                        st.error(f"Invalid Login: {u_id_input} နှင့် {u_pw_input} သည် DB ရှိ data နှင့် မကိုက်ညီပါ။")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        return False
    return True
