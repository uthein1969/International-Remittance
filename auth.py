import streamlit as st

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        # --- Database မှ Data များကို ကြိုတင်ပြင်ဆင်ခြင်း ---
        country_list = []
        branch_list = []
        tz_map = {}

        try:
            # Country table မှ data ဆွဲထုတ်ခြင်း
            c_query = supabase.table("country_setup").select("country_name, remark").execute()
            if c_query.data:
                country_list = [str(r['country_name']) for r in c_query.data]
                tz_map = {str(r['country_name']): str(r['remark']) for r in c_query.data}
            
            # Branch table မှ data ဆွဲထုတ်ခြင်း
            b_query = supabase.table("branch_setup").select("branch_name").execute()
            if b_query.data:
                branch_list = [str(r['branch_name']) for r in b_query.data]
        except Exception as e:
            st.error(f"⚠️ Connection Error: {e}")

        # အကယ်၍ data လုံးဝမတက်လာပါက ပိုမိုရှင်းလင်းသော error ပြရန်
        if not country_list or not branch_list:
            st.error("❌ Database ထဲတွင် Country သို့မဟုတ် Branch ဒေတာများ မရှိသေးပါ။ (သို့မဟုတ်) RLS Policy ကြောင့် ဖတ်၍မရဖြစ်နေပါသည်။")
            return False

        with st.form("login_form"):
            u_id = st.text_input("User ID")
            u_pw = st.text_input("Password", type="password")
            
            sel_c = st.selectbox("Select Country", options=country_list)
            sel_b = st.selectbox("Select Branch", options=branch_list)
            
            if st.form_submit_button("Login", use_container_width=True):
                # User verification
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
                    st.error("❌ User ID သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
        return False
    return True
