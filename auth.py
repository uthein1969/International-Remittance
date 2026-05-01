import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        # --- Database မှ Data များကို အသေအချာဆွဲထုတ်ခြင်း ---
        country_list = []
        branch_list = []
        tz_map = {}

        try:
            # Country List ဆွဲထုတ်ခြင်း
            c_res = supabase.table("country_setup").select("country_name, remark").execute()
            if c_res.data:
                country_list = [str(r['country_name']) for r in c_res.data]
                tz_map = {str(r['country_name']): str(r['remark']) for r in c_res.data}
            
            # Branch List ဆွဲထုတ်ခြင်း
            b_res = supabase.table("branch_setup").select("branch_name").execute()
            if b_res.data:
                branch_list = [str(r['branch_name']) for r in b_res.data]
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")

        with st.form("login_form"):
            u_id = st.text_input("User ID")
            u_pw = st.text_input("Password", type="password")
            
            # Data ရှိမှ Selectbox ပြမည်၊ မရှိလျှင် Empty List ပြမည်
            sel_c = st.selectbox("Select Country", options=country_list if country_list else ["Loading..."])
            sel_b = st.selectbox("Select Branch", options=branch_list if branch_list else ["Loading..."])
            
            if st.form_submit_button("Login", use_container_width=True):
                if not country_list or sel_c == "Loading...":
                    st.warning("⚠️ Country/Branch data များ မတက်လာသေးပါ။ စက္ကန့်အနည်းငယ်စောင့်ပြီး Refresh လုပ်ပါ။")
                else:
                    # User Login စစ်ဆေးခြင်း
                    res = supabase.table("user_setup").select("*").eq("user_id", u_id).eq("password", u_pw).execute()
                    if res.data:
                        st.session_state.update({
                            'logged_in': True,
                            'user_id': u_id,
                            'sel_country': sel_c,
                            'sel_branch': sel_b,
                            'target_tz': tz_map.get(sel_c, "Asia/Yangon")
                        })
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
        return False
    return True
