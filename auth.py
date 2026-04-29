import streamlit as st

def check_login(supabase):
    # Session state ကို စစ်ဆေးခြင်း
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Login မဝင်ရသေးလျှင် Login Form ပြသမည်
    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        with st.form("login_form"):
            u_id_raw = st.text_input("User ID")
            u_pw_raw = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login", use_container_width=True)

            if submit_btn:
                u_id_input = u_id_raw.strip()
                u_pw_input = u_pw_raw.strip()
                
                try:
                    # Database မှ data ကို အရင်ယူမည် (Line အစီအစဉ် မှန်ကန်ရမည်)
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id_input).eq("password", u_pw_input).execute()
                    
                    # res.data ရှိမရှိ သေချာစွာ စစ်ဆေးခြင်း
                    if res and hasattr(res, 'data') and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = u_id_input
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
                except Exception as e:
                    st.error(f"⚠️ Connection Error: {str(e)}")
        
        st.stop() # Login မဝင်မချင်း အောက်က code တွေကို ဆက်မသွားစေရန်
        return False
    
    return True
