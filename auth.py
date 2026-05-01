import streamlit as st
import pandas as pd

def check_login(supabase):
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 Admin Login System")
        
        # --- Database မှ Data များကို ဆွဲထုတ်ခြင်း ---
        try:
            countries_res = supabase.table("country_setup").select("country_name, remark").execute()
            branches_res = supabase.table("branch_setup").select("branch_name").execute()
            
            country_list = [r['country_name'] for r in countries_res.data] if countries_res.data else []
            tz_map = {r['country_name']: r['remark'] for r in countries_res.data} if countries_res.data else {}
            branch_list = [r['branch_name'] for r in branches_res.data] if branches_res.data else []
        except Exception as e:
            st.error(f"Data Connection Error: {e}")
            country_list, branch_list, tz_map = [], [], {}

        with st.form("login_form"):
            input_user = st.text_input("User ID")
            input_pass = st.text_input("Password", type="password")
            
            # ဒေတာရှိမှ selectbox ပြရန်၊ မရှိပါက Warning ပြရန်
            sel_country = st.selectbox("Select Country", options=country_list if country_list else ["No Country Found"])
            sel_branch = st.selectbox("Select Branch", options=branch_list if branch_list else ["No Branch Found"])
            
            submit_btn = st.form_submit_button("Login", use_container_width=True)
            
            if submit_btn:
                if not country_list or not branch_list:
                    st.error("❌ Country သို့မဟုတ် Branch ဒေတာများ မရှိသေးပါ။")
                else:
                    res = supabase.table("user_setup").select("*").eq("user_id", input_user).eq("password", input_pass).execute()
                    
                    if res.data:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = input_user
                        st.session_state['selected_country'] = sel_country
                        st.session_state['selected_branch'] = sel_branch
                        
                        # Timezone ID (ဥပမာ- Asia/Bangkok) ကို Session မှာသိမ်းခြင်း
                        st.session_state['target_tz'] = tz_map.get(sel_country, "Asia/Yangon")
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid User ID or Password")
        return False
    return True
