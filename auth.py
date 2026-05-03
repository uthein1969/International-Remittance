import streamlit as st

def login_page(supabase):
    st.title("🔐 Admin Login System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                # Table အမည်ကို 'user_setup' ဟု ပြောင်းလဲအသုံးပြုထားပါသည်
                res = supabase.table("user_setup").select("*").eq("username", username).eq("password", password).execute()
                
                if res.data:
                    user_data = res.data[0]
                    st.session_state.logged_in = True
                    st.session_state.user = user_data  # ဤနေရာတွင် Country နှင့် Branch အချက်အလက်များ ပါဝင်ပါသည်
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
            except Exception as e:
                st.error(f"Login Error: {e}")
