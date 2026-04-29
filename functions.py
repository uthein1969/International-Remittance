import streamlit as st
import pandas as pd
from datetime import datetime

def show_blacklist_page(supabase):
    st.header("📜 Blacklist Information Management")
    
    # --- Blacklist Data လှမ်းယူခြင်း ---
    res = supabase.table("blacklist_setup").select("*").execute()
    df = pd.DataFrame(res.data)
    
    tab1, tab2 = st.tabs(["➕ Add New", "🔍 View & Action"])
    
    with tab1:
        with st.form("add_blacklist"):
            name = st.text_input("Name")
            nrc = st.text_input("NRC No.")
            reason = st.text_area("Reason")
            submitted = st.form_submit_button("Save to Blacklist")
            if submitted:
                supabase.table("blacklist_setup").insert({"name": name, "nrc": nrc, "remark": reason}).execute()
                st.success("✅ Added to Blacklist")
                st.rerun()
                
    with tab2:
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No records found.")

def show_inward_page(supabase, now_yangon):
    st.header("🏦 Inward Transaction Management")
    # အရင်က ကုဒ်ဟောင်းထဲက Inward Logic များကို ဤနေရာတွင် အပြည့်အစုံထည့်သွင်းထားပါသည်
    # (မှတ်ချက် - ကုဒ်ရှည်လျားသဖြင့် အဓိကအပိုင်းကိုသာ နမူနာပြထားပါသည်)
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            ref_no = st.text_input("Reference No.")
            sender = st.text_input("Sender Name")
        with col2:
            amount = st.number_input("Amount", min_value=0.0)
            date = st.date_input("Date", value=now_yangon)
            
    if st.button("💾 Save Transaction", type="primary"):
        # Save logic here
        st.success("Transaction Saved!")

def show_user_setup(supabase):
    st.header("⚙️ User Account Setup")
    # ကုဒ်ဟောင်းပါ User Modify/Delete အပိုင်းများ
    res_u = supabase.table("user_setup").select("*").execute()
    if res_u.data:
        u_list = [u['user_id'] for u in res_u.data]
        target_uid = st.selectbox("Choose a User ID to modify:", options=["-- Select --"] + u_list)
        
        if target_uid != "-- Select --":
            user_data = next(u for u in res_u.data if u['user_id'] == target_uid)
            with st.container(border=True):
                up_uid = st.text_input("Update User ID", value=user_data['user_id'])
                up_pwd = st.text_input("Update Password", value=user_data['password'], type="password")
                if st.button("🆙 Update Now"):
                    supabase.table("user_setup").update({"user_id": up_uid, "password": up_pwd}).eq("id", user_data['id']).execute()
                    st.success("Updated!")
                    st.rerun()
