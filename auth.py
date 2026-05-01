import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        # --- Database မှ Data များကို အရင်ဆုံး ကြိုတင်ဆွဲထုတ်ခြင်း ---
        try:
            # Country data ယူခြင်း
            c_res = supabase.table("country_setup").select("country_name, remark").execute()
            # Branch data ယူခြင်း
            b_res = supabase.table("branch_setup").select("branch_name").execute()
            
            if c_res.data and b_res.data:
                country_list = [str(r['country_name']) for r in c_res.data]
                tz_map = {str(r['country_name']): str(r['remark']) for r in c_res.data}
                branch_list = [str(r['branch_name']) for r in b_res.data]
            else:
                st.error("❌ Database ထဲတွင် Country သို့မဟုတ် Branch ဒေတာများ မရှိသေးပါ။")
                return False
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")
            return False

        # Form မပြခင် Data စစ်ဆေးခြင်း
        with st.form("login_form"):
            u_id = st.text_input("User ID")
            u_pw = st.text_input("Password", type="password")
            
            # ဒေတာများ အမှန်တကယ်ရှိမှ Dropdown ပြမည်
            sel_c = st.selectbox("Select Country", options=country_list)
            sel_b = st.selectbox("Select Branch", options=branch_list)
            
            submit_btn = st.form_submit_button("Login", use_container_width=True)
            
            if submit_btn:
                # Login စစ်ဆေးခြင်း
                res = supabase.table("user_setup").select("*").eq("user_id", u_id).eq("password", u_pw).execute()
                if res.data:
                    st.session_state.update({
                        'logged_in': True,
                        'user_id': u_id,
                        'sel_country': sel_c,
                        'sel_branch': sel_b,
                        'target_tz': tz_map.get(sel_c, "Asia/Yangon")
                    })
                    st.success("✅ Login အောင်မြင်ပါသည်။")
                    st.rerun()
                else:
                    st.error("❌ User ID သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
        return False
    return True
