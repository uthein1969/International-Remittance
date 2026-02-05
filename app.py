import pandas as pd
import streamlit as st
import pytz
from supabase import create_client, Client
from datetime import datetime

# --- ၁။ Setup & Connections ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

ADMIN_PASSWORD = "admin123" # သင်နှစ်သက်ရာ Password ပြောင်းလဲနိုင်သည်

st.set_page_config(page_title="Remittance System", layout="wide")

# Session State ဖြင့် Login အခြေအနေကို မှတ်ထားခြင်း
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- ၂။ Login Page (Login မဝင်ရသေးခင် ပြသမည့်အပိုင်း) ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Login - Remittance System")
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    
    with col_l2:
        with st.container(border=True):
            st.subheader("Admin Login")
            pwd_input = st.text_input("Enter Password", type="password")
            if st.button("Login"):
                if pwd_input == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun() # Login အောင်မြင်လျှင် Page ကို Refresh လုပ်ရန်
                else:
                    st.error("❌ Password မှားယွင်းနေပါသည်။")
    st.stop() # Login မဝင်မချင်း အောက်က Code တွေကို ဆက်မသွားခိုင်းရန်

# --- ၃။ Main System (Login ဝင်ပြီးမှသာ ပေါ်လာမည့်အပိုင်း) ---
# Sidebar မှာ Logout ခလုတ်နှင့် Menu ထားရှိခြင်း
st.sidebar.success("Logged In ✅")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.title("🚀 Main Menu")
page = st.sidebar.radio("Go to:", ["📋 Blacklist Info", "🏦 Inward Transaction"])
st.sidebar.markdown("---")
st.sidebar.info("System Version 2.0v")

# --- ၄။ Blacklist System Page ---
if page == "📋 Blacklist Info":
    st.title("🌏 Blacklist Management")
    tab1, tab2 = st.tabs(["📊 View & Search", "⚙️ Management"])
    
    with tab1:
        search = st.text_input("🔍 Search Blacklist", placeholder="Enter Name or NRC...")
        try:
            # အစဉ်လိုက်ကြည့်ရန် desc=False
            res = supabase.table("blacklist").select("*").order("srno", desc=False).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                if search:
                    df = df[df['name'].str.contains(search, case=False) | df['nrcno'].str.contains(search, case=False)]
                df.insert(0, 'No.', range(1, 1 + len(df)))
                st.dataframe(df.drop(columns=['srno']), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

    with tab2:
        with st.form("blacklist_form", clear_on_submit=True):
            st.subheader("➕ Add New Blacklist")
            name = st.text_input("Name")
            nrc = st.text_input("NRC Number")
            remark = st.text_area("Remark")
            if st.form_submit_button("Save to Blacklist"):
                if name and nrc:
                    check = supabase.table("blacklist").select("nrcno").eq("nrcno", nrc).execute()
                    if len(check.data) > 0:
                        st.error(f"⚠️ {nrc} သည် ရှိပြီးသား ဖြစ်ပါသည်။")
                    else:
                        supabase.table("blacklist").insert({"name": name, "nrcno": nrc, "remark": remark}).execute()
                        st.success("Successfully added to blacklist!")
                        st.rerun()

# --- ၅။ Inward Transaction Page ---
elif page == "🏦 Inward Transaction":
    st.title("🏦 Inward Transaction")
    yangon_tz = pytz.timezone('Asia/Yangon')
    now_yangon = datetime.now(yangon_tz)
    formatted_time = now_yangon.strftime("%Y-%m-%d %H:%M:%S")
    # --- ၁။ Header Information ---
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        st.text_input("Date:", value=formatted_time, disabled=True)
    with h_col2:
        branch = st.selectbox("Select Branch", ["", "Yangon Branch", "Mandalay Branch", "Nay Pyi Taw Branch"])
    with h_col3:
        trans_no = st.text_input("Transaction No:", value="9639")

    # --- ၂။ RECEIVER INFORMATION ---
    st.subheader("🔵 RECEIVER INFORMATION :")
    with st.container(border=True):
        r_col1, r_col2 = st.columns(2)
        r_name = r_col1.text_input("Receiver Name:")
        r_nrc = r_col2.selectbox("Receiver NRC:", ["", "12/THA GA KA (N) 048123", "12/THA GA KA (N) 048127"]) # NRC List များ

        r_addr_col, r_ph_col, r_purp_col = st.columns([2, 1, 1])
        r_address = r_addr_col.text_input("Receiver Address:")
        r_phone = r_ph_col.text_input("Receiver Phone:")
        r_purpose = r_purp_col.selectbox("Purpose of Transaction", ["", "Family Support", "Business", "Gift"])

        r_state_col, r_point_col = st.columns(2)
        r_state = r_state_col.selectbox("State & Division", ["", "Yangon", "Mandalay", "Shan", "Bago"])
        r_point = r_point_col.text_input("Withdraw Point:")
        
        r_remark = st.text_area("Remark for Withdraw Point:")

    # --- ၃။ SENDER INFORMATION ---
    st.subheader("🔵 SENDER INFORMATION :")
    with st.container(border=True):
        s_name_col, s_id_col, s_country_col = st.columns([2, 2, 1])
        s_name = s_name_col.text_input("Sender Name:")
        s_id = s_id_col.text_input("NRC/Passport ID:")
        s_country = s_country_col.text_input("Country", value="Thailand")

        s_cur_col, s_mmk_col, s_usd_col = st.columns(3)
        with s_cur_col:
            currency = st.selectbox("Currency", ["THB", "USD", "SGD"])
            amount = st.number_input("Amount", min_value=0.0)
        with s_mmk_col:
            mmk_rate = st.number_input("MMK Rate", min_value=0.0)
            mmk_allowance = st.number_input("MMK Allowance", min_value=0.0)
        with s_usd_col:
            usd_equiv = st.number_input("USD Equivalent", min_value=0.0)
            total_mmk = st.number_input("Total MMK", min_value=0.0)

    # --- ၄။ UPLOAD FILE ---
    st.subheader("📤 Upload File")
    uploaded_file = st.file_uploader("Choose File", type=['png', 'jpg', 'pdf'])

    # --- ၅။ SAVE ACTION ---
    if st.button("💾 Save", type="primary"):
        if r_nrc:
            # Blacklist စစ်ဆေးခြင်း
            check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
            if len(check_bl.data) > 0:
                st.error(f"❌ STOP! {r_nrc} သည် Blacklist စာရင်းဝင် ({check_bl.data[0]['name']}) ဖြစ်နေပါသည်။")
            else:
                st.success("✅ Transaction အချက်အလက်များကို သိမ်းဆည်းလိုက်ပါပြီ။")
        else:
            st.warning("⚠️ Receiver NRC ကို ဖြည့်သွင်းပေးပါ။")

    # Save Action with Blacklist Check
    if st.button("💾 Save Transaction", type="primary", use_container_width=True):
        if r_nrc:
            # Blacklist ထဲတွင် ရှိမရှိ စစ်ဆေးခြင်း
            check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
            if len(check_bl.data) > 0:
                st.error(f"❌ STOP! {r_nrc} သည် Blacklist စာရင်းဝင် ({check_bl.data[0]['name']}) ဖြစ်ပါသည်။")
            else:
                st.success("✅ Transaction အချက်အလက်များ မှန်ကန်ပါသည်။")
                
                if c2.button("🗑️ Delete"):
                    supabase.table("blacklist").delete().eq("srno", selected['srno']).execute()
                    st.warning("Deleted!")
                    st.rerun()
