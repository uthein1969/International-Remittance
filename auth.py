import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        with st.form("login_form"):
            # Variable အမည်မှ Dot (.) ကို ဖြုတ်လိုက်ပါပြီ
            u_id_raw = st.text_input("User ID")
            u_pw_raw = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login")

            if submit_btn:
                # ရိုက်ထည့်လိုက်သော စာသားများမှ Space များကို ဖယ်ရှားခြင်း
                u_id_input = u_id_raw.strip()
                u_pw_input = u_pw_raw.strip()
                
                try:
                    # Database စစ်ဆေးခြင်း
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id_input).eq("password", u_pw_input).execute()
                    
                    if res.data and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = u_id_input
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
                        # Debug ပြန်လုပ်ရန် (အဆင်ပြေလျှင် ဖြုတ်နိုင်သည်)
                        st.write(f"ID: {u_id_input}, PW: {u_pw_input}")
                        st.write(f"Result: {res.data}")
                except Exception as e:
                    st.error(f"Login Error: {e}")
        return False
    return True
