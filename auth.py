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
                # ၁။ Database query ကို အရင် run မယ်
                res = supabase.table("user_setup").select("*").eq("user_id", u_id_input.strip()).eq("password", u_pw_input.strip()).execute()
                
                # ၂။ res ထဲမှာ data တကယ်ပါလာမှ စစ်ဆေးမယ် (ဒီအဆင့်က အရေးကြီးပါတယ်)
                if res is not None and hasattr(res, 'data') and res.data:
                    st.write("✅ Database မှ အချက်အလက် ရှာဖွေတွေ့ရှိပါသည်။")
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = u_id_input.strip()
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    # Data မရှိရင် (သို့မဟုတ်) password မှားရင် ဒီကို ရောက်မယ်
                    st.error("❌ Invalid User ID or Password")
                    st.write("DEBUG: Database က ဘာမှပြန်မပေးပါ (Empty Result)")
            
            except Exception as e:
                # Database connection error သို့မဟုတ် အခြား error များအတွက်
                st.error(f"⚠️ System Error: {str(e)}")        return False
    return True
