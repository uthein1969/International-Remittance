
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- ၁။ Supabase ချိတ်ဆက်မှု ---
URL = "https://tjkykxuvczmctmxxurew.supabase.co".strip()
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqa3lreHV2Y3ptY3RteHh1cmV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk4NjA5NjYsImV4cCI6MjA4NTQzNjk2Nn0.RYyYOZFAOoSLRe6WCgupj0VnujfcC6XpweZM0S9tJz4
" # သင့် Key ကို ဤနေရာတွင် အစားထိုးပါ
supabase: Client = create_client(URL, KEY)

# --- ၂။ စနစ်လုံခြုံရေး (Password သတ်မှတ်ခြင်း) ---
ADMIN_PASSWORD = "admin123" # သင်နှစ်သက်ရာ Password ပြောင်းလဲနိုင်သည်

st.set_page_config(page_title="Secure Admin Dashboard", layout="wide")

# Session State ထဲတွင် Login အခြေအနေကို သိမ်းဆည်းရန်
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ၃။ Login Form ပြသခြင်း ---
if not st.session_state.logged_in:
    st.subheader("🔐 Admin Login")
    pwd_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password!")
else:
    # Login အောင်မြင်ပြီးမှသာ အောက်ပါ Tabs များကို ပြသမည်
    st.sidebar.success("Logged In as Admin")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["📊 View & Search", "➕ Add New", "⚙️ Actions (Edit/Delete)"])

    # --- Tab 1: View & Search ---
    with tab1:
        st.subheader("📋 Blacklist Database")
        search_query = st.text_input("Quick Search", placeholder="Name or NRC...")
        try:
            res = supabase.table("blacklist").select("*").order("srno").execute() #
            if res.data:
                df = pd.DataFrame(res.data)
                if search_query:
                    df = df[df['name'].str.contains(search_query, case=False) | df['nrcno'].str.contains(search_query, case=False)]
                
                df.insert(0, 'No.', range(1, 1 + len(df)))
                st.dataframe(df.drop(columns=['srno']), use_container_width=True) #
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Report (CSV)", data=csv, file_name='report.csv')
        except Exception as e:
            st.error(e)

    # --- Tab 2: Add New ---
    with tab2:
        st.subheader("➕ Add New Entry")
        with st.form("add_form"):
            name = st.text_input("Name")
            nrc = st.text_input("NRC No")
            rem = st.text_area("Remark")
            if st.form_submit_button("Save to Cloud"): #
                supabase.table("blacklist").insert({"name": name, "nrcno": nrc, "remark": rem}).execute()
                st.success("Successfully Saved!")
                st.rerun()

    # --- Tab 3: Actions (Edit & Delete) ---
    with tab3:
        st.subheader("🛠️ Modify Records")
        res = supabase.table("blacklist").select("*").execute()
        if res.data:
            options = {f"{row['name']} ({row['nrcno']})": row for row in res.data}
            selected_label = st.selectbox("Select Record", options.keys())
            selected_row = options[selected_label]

            col1, col2 = st.columns(2)
            with col1:
                st.write("📝 **Update Info**")
                new_name = st.text_input("Edit Name", value=selected_row['name'])
                new_nrc = st.text_input("Edit NRC", value=selected_row['nrcno'])
                new_rem = st.text_area("Edit Remark", value=selected_row['remark'])
                if st.button("🆙 Update"):
                    supabase.table("blacklist").update({"name": new_name, "nrcno": new_nrc, "remark": new_rem}).eq("srno", selected_row['srno']).execute() #
                    st.success("Updated!")
                    st.rerun()

            with col2:
                st.write("🗑️ **Delete Info**")
                st.write(f"Delete record for **{selected_row['name']}**?")
                if st.button("🗑️ Delete"):
                    supabase.table("blacklist").delete().eq("srno", selected_row['srno']).execute() #
                    st.warning("Deleted!")
                    st.rerun()
