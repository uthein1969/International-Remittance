import streamlit as st

def login_page(supabase):
    st.title("🔐 Admin Login System")
    
    with st.form("login_form"):
        # 💡 variable နာမည်ကို input_user ဟု ပြောင်းလဲသတ်မှတ်လိုက်ပါသည်
        input_user = st.text_input("User ID")
        input_pass = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                # 💡 user_id ရော password ပါ စနစ်တကျ တစ်ဆက်တည်း စစ်ဆေးရန် ပြင်ဆင်ပြီး
                res = supabase.table("user_setup")\
                    .select("*")\
                    .eq("user_id", input_user)\
                    .eq("password", input_pass)\
                    .execute()
                
                if res.data:
                    user_data = res.data[0]
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.success("✅ Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid User ID or Password")
            except Exception as e:
                st.error(f"Login Error: {e}")