import streamlit as st

def login_page(supabase):
    st.title("🔐 Admin Login System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            try:
                # Database ထဲမှာ user ရှိမရှိ စစ်ဆေးခြင်း
                res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
                
                if res.data:
                    user_data = res.data[0]
                    # --- အရေးကြီးသည်: Session ထဲမှာ user data သိမ်းခြင်း ---
                    st.session_state.logged_in = True
                    st.session_state.user = user_data  # ဤနေရာတွင် branch နှင့် country အချက်အလက်များ ပါဝင်သည်
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            except Exception as e:
                st.error(f"Login Error: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()
