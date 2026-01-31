import streamlit as st
from supabase import create_client, Client

# Secrets ထဲကနေ URL နဲ့ Key ကို ဆွဲယူခြင်း
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

# --- ၂။ စနစ်လုံခြုံရေး (Password သတ်မှတ်ခြင်း) ---
ADMIN_PASSWORD = "admin123" # သင်နှစ်သက်ရာ Password ပြောင်းလဲနိုင်သည်

st.set_page_config(page_title="Secure Admin Dashboard", layout="wide")

# --- ၂။ Custom CSS (ဒီဇိုင်းပိုလှစေရန်) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_all_headers=True)

st.title("🌏 International Remittance - Blacklist System")
st.markdown("---")

# --- ၃။ အပေါ်ဆုံးမှာ ကိန်းဂဏန်းများပြရန် (Dashboard Style) ---
res_count = supabase.table("blacklist").select("*", count="exact").execute()
total_records = res_count.count if res_count.count else 0

col_stat1, col_stat2, col_stat3 = st.columns(3)
col_stat1.metric("Total Records", total_records)
col_stat2.metric("Database Status", "Online ✅")
col_stat3.metric("System Version", "2.0v")

# --- ၄။ Layout ပိုင်းခြားခြင်း ---
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("➕ New Registration")
    with st.container(border=True): # Form ကို ဘောင်လေးခတ်ပေးခြင်း
        with st.form("new_entry_form", clear_on_submit=True):
            name = st.text_input("👤 Full Name", placeholder="Enter name")
            nrc = st.text_input("💳 NRC Number", placeholder="Example: 12/DAGAMA(N)123456")
            remark = st.text_area("📝 Remark", placeholder="Any additional notes...")
            
            submit = st.form_submit_button("Submit to Database")
            if submit:
                if name and nrc:
                    try:
                        # srno ကို ထည့်စရာမလိုပါ (Identity ဖြစ်သောကြောင့်)
                        supabase.table("blacklist").insert({"name": name, "nrcno": nrc, "remark": remark}).execute()
                        st.success(f"Successfully added {name}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Name and NRC are required!")

with right_col:
    st.subheader("🔍 Search & Management")
    search = st.text_input("", placeholder="Search by name or NRC number...")
    
    try:
        res = supabase.table("blacklist").select("*").order("srno", desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Search filtering
            if search:
                df = df[df['name'].str.contains(search, case=False) | df['nrcno'].str.contains(search, case=False)]
            
            # ပြသရန် နံပါတ်စဉ်အသစ် တပ်ခြင်း
            df.insert(0, 'No.', range(1, 1 + len(df)))
            
            # ဇယားကို ပိုလှအောင် ပြသခြင်း
            st.dataframe(
                df.drop(columns=['srno']), 
                use_container_width=True,
                column_config={
                    "name": "Customer Name",
                    "nrcno": "Identity Card",
                    "remark": "Notes"
                }
            )
        else:
            st.info("No data available.")
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
                    supabase.table("blacklist").delete().eq("srno", selected_row['srno']).execute() #
                    st.warning("Deleted!")
                    st.rerun()
