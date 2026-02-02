import pandas as pd
import streamlit as st
from supabase import create_client, Client

# --- ၁။ Setup & Connections ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

ADMIN_PASSWORD = "admin123" # သင်နှစ်သက်ရာ Password ပြောင်းလဲနိုင်သည်

st.set_page_config(page_title="International Remittance System", layout="wide")

# Session State ဖြင့် Login အခြေအနေကို မှတ်ထားခြင်း
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ၂။ Custom CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- ၃။ Login စစ်ဆေးခြင်း ---
if not st.session_state.logged_in:
    st.title("🔐 Admin Access Required")
    pwd_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if pwd_input == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password!")
else:
    # Login အောင်မြင်မှသာ အောက်ပါ Dashboard ကို ပြသမည်
    st.sidebar.success("Logged In ✅")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🌏 International Remittance System")
    st.markdown("---")

    # --- ၄။ Stats & Layout ---
    res_count = supabase.table("blacklist").select("*", count="exact").execute()
    total_records = res_count.count if res_count.count else 0
    st.metric("Total Blacklisted Records", total_records)

    tab1, tab2 = st.tabs(["📊 View & Search", "⚙️ Management (Add/Edit/Delete)"])

    # --- Tab 1: View Data ---
    with tab1:
        search = st.text_input("🔍 Search by Name or NRC", placeholder="Enter details...")
        try:
            res = supabase.table("blacklist").select("*").order("srno", desc=False).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                if search:
                    df = df[df['name'].str.contains(search, case=False) | df['nrcno'].str.contains(search, case=False)]
                
                df.insert(0, 'No.', range(1, 1 + len(df)))
                st.dataframe(df.drop(columns=['srno']), use_container_width=True)
                
                # Excel/CSV ထုတ်ယူရန်
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Data Report", data=csv, file_name='blacklist_report.csv')
        except Exception as e:
            st.error(f"Error fetching data: {e}")

    # --- Tab 2: Add/Edit/Delete ---
    with tab2:
        col_add, col_edit = st.columns(2)
        
        with left_col:
        st.subheader("➕ New Registration")
        with st.container(border=True): 
            # အောက်ပါ စာကြောင်းများအားလုံးသည် 'with' အောက်တွင် Space ၄ ခုစီ ဝင်ရပါမည်
            with st.form("new_entry_form", clear_on_submit=True):
                name = st.text_input("👤 Full Name", placeholder="Enter name")
                nrc = st.text_input("💳 NRC Number", placeholder="Example: 12/DAGAMA(N)123456")
                remark = st.text_area("📝 Remark", placeholder="Any additional notes...")
                
                submit = st.form_submit_button("Submit to Database")
                if submit:
                    if name and nrc:
                        try:
                            # ၁။ NRC တူမတူ အရင်စစ်ဆေးခြင်း
                            check_res = supabase.table("blacklist").select("nrcno").eq("nrcno", nrc).execute()
                            
                            if len(check_res.data) > 0:
                                st.error(f"⚠️ ဤမှတ်ပုံတင်နံပါတ် ({nrc}) သည် ရှိပြီးသားဖြစ်ပါသည်။")
                            else:
                                # ၂။ မရှိမှသာ အသစ်သွင်းပါ
                                supabase.table("blacklist").insert({"name": name, "nrcno": nrc, "remark": remark}).execute()
                                st.success(f"Successfully added {name}!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Name and NRC are required!")

        with col_edit:
            st.subheader("🛠️ Edit or Delete")
            res_all = supabase.table("blacklist").select("*").execute()
            if res_all.data:
                options = {f"{r['name']} ({r['nrcno']})": r for r in res_all.data}
                choice = st.selectbox("Select Record", options.keys())
                selected = options[choice]

                edit_name = st.text_input("Edit Name", value=selected['name'])
                edit_nrc = st.text_input("Edit NRC", value=selected['nrcno'])
                
                c1, c2 = st.columns(2)
                if c1.button("🆙 Update"):
                    supabase.table("blacklist").update({"name": edit_name, "nrcno": edit_nrc}).eq("srno", selected['srno']).execute()
                    st.success("Updated!")
                    st.rerun()
                
                if c2.button("🗑️ Delete"):
                    # srno ကို အခြေခံ၍ ဖျက်ခြင်း
                    supabase.table("blacklist").delete().eq("srno", selected['srno']).execute()
                    st.warning("Deleted!")
                    st.rerun()

