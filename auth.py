import streamlit as st

def check_login(supabase): # supabase ကို parameter အနေနဲ့ လက်ခံရပါမယ်
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        with st.form("login_form"):
            input_user = st.text_input("User ID")
            input_pass = st.text_input("Password", type="password")
            submit_btn = st.form_submit_button("Login")
            
            if submit_btn:
                input_user = u_id_raw.strip() # ရိုက်ထည့်လိုက်တဲ့ space များကို ဖယ်ရှားခြင်း
                input_pass = u_pw_raw.strip()
                st.write(f"ID: {input_user}, PW: {input_pass}")
                
                try:
                    # Database စစ်ဆေးခြင်း
                    res = supabase.table("user_setup")\
                        .select("*")\
                        .like("user_id", f"%{input_user}%")\
                        .eq("password", input_pass)\
                        .execute()
                    st.write(f"Result Data: {res.data}")
                    if res.data and len(res.data) > 0:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = input_user
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
                except Exception as e:
                    st.error(f"Login Error: {e}")
        
        st.stop() # Login မဝင်မချင်း အောက်က code တွေကို ဆက်မသွားစေရန်
        return False
    return True
