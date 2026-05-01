import streamlit as st
import pandas as pd

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        # နိုင်ငံနှင့် Branch စာရင်းများကို Database မှ ကြိုတင်ဆွဲထုတ်ခြင်း
        countries = supabase.table("country_setup").select("country_name, remark").execute()
        branches = supabase.table("branch_setup").select("branch_name").execute()
        
        country_list = [r['country_name'] for r in countries.data] if countries.data else []
        # Timezone များကို သိမ်းဆည်းထားရန် Dictionary
        tz_map = {r['country_name']: r['remark'] for r in countries.data} if countries.data else {}
        branch_list = [r['branch_name'] for r in branches.data] if branches.data else []

        with st.form("login_form"):
            input_user = st.text_input("User ID")
            input_pass = st.text_input("Password", type="password")
            # နိုင်ငံနှင့် Branch ကို ရွေးချယ်ခိုင်းခြင်း
            sel_country = st.selectbox("Select Country", country_list)
            sel_branch = st.selectbox("Select Branch", branch_list)
            
            submit_btn = st.form_submit_button("Login")
            
            if submit_btn:
                res = supabase.table("user_setup").select("*").eq("user_id", input_user).eq("password", input_pass).execute()
                
                if res.data:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = input_user
                    # ရွေးချယ်ခဲ့သော အချက်အလက်များကို Session တွင် သိမ်းခြင်း
                    st.session_state['selected_country'] = sel_country
                    st.session_state['selected_branch'] = sel_branch
                    st.session_state['target_tz'] = tz_map.get(sel_country, "UTC")
                    st.rerun()
                else:
                    st.error("❌ Invalid Login")
        return False
    return True
