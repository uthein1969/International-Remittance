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

yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

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
page = st.sidebar.radio("Go to:", ["📊 Dashboard", "📋 Blacklist Info", "🏦 Inward Transaction"])
st.sidebar.markdown("---")
st.sidebar.info("System Version 2.0v")

# --- ၄။ Dashboard Page (Login ဝင်ပြီးလျှင် အရင်ဆုံးမြင်ရမည့်စာမျက်နှာ) ---
if page == "📊 Dashboard":
    st.title("📈 Transaction Dashboard")
    st.markdown(f"**Last Updated:** {now_yangon.strftime('%Y-%m-%d %H:%M:%S')} (Yangon Time)")

    # Daily Section
    st.subheader("Daily Transaction")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.date_input("Start Date", value=now_yangon, key="ds")
    with d_col2:
        st.date_input("End Date", value=now_yangon, key="de")
    
    # ရောင်စုံ Box များ (Daily)
    db1, db2 = st.columns(2)
    db1.info("### 0 \n 📉 Daily Inward") # ပုံထဲကအရောင်အတိုင်း Info/Warning/Error သုံးနိုင်သည်
    db2.info("### 0 \n 📉 Daily Outward")

    st.divider()

    # Monthly Section
    st.subheader("Monthly Transaction")
    m_col1, m_col2 = st.columns(2)
    m_col1.selectbox("Start Month", ["February 2026"])
    m_col2.selectbox("End Month", ["February 2026"])
    
    mb1, mb2 = st.columns(2)
    # ဥပမာ ဒေတာ ၁၁၁၈ အား ပြသခြင်း
    mb1.warning("### 0 \n 📈 Monthly Inward") 
    mb2.warning("### 0 \n 📈 Monthly Outward")

    st.divider()

    # Yearly Section
    st.subheader("Yearly Transaction")
    yb1, yb2 = st.columns(2)
    yb1.error("### 0 \n 📊 Yearly Inward")
    yb2.error("### 0 \n 📊 Yearly Outward")

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
        col_new, col_mod = st.columns(2)
        
        # ၁။ Blacklist အသစ်ထည့်သည့်အပိုင်း
        with col_new:
            with st.form("add_new_form", clear_on_submit=True):
                st.subheader("➕ Add New Blacklist")
                name = st.text_input("Name")
                nrc = st.text_input("NRC Number")
                remark = st.text_area("Remark")
                if st.form_submit_button("Save to Blacklist"):
                    if name and nrc:
                        # NRC တူမတူ စစ်ဆေးခြင်း
                        check = supabase.table("blacklist").select("nrcno").eq("nrcno", nrc).execute()
                        if len(check.data) > 0:
                            st.error(f"⚠️ {nrc} သည် ရှိပြီးသား ဖြစ်ပါသည်။")
                        else:
                            supabase.table("blacklist").insert({"name": name, "nrcno": nrc, "remark": remark}).execute()
                            st.success("Successfully added!")
                            st.rerun()

        # ၂။ Edit & Delete ပြုလုပ်သည့်အပိုင်း
        with col_mod:
            st.subheader("🛠️ Edit or Delete")
            # Database ထဲမှ data များအားလုံးကို ဆွဲထုတ်ခြင်း
            res_all = supabase.table("blacklist").select("*").execute()
            
            if res_all.data:
                # ရွေးချယ်ရလွယ်ကူအောင် အမည်နှင့် NRC ကို တွဲပြခြင်း
                options = {f"{r['name']} ({r['nrcno']})": r for r in res_all.data}
                choice = st.selectbox("Select Record to Modify", options.keys())
                selected = options[choice]

                # ရွေးချယ်လိုက်သော ဒေတာများကို Form ထဲတွင် ပြန်ပြခြင်း
                with st.container(border=True):
                    edit_name = st.text_input("Update Name", value=selected['name'])
                    edit_nrc = st.text_input("Update NRC", value=selected['nrcno'])
                    edit_remark = st.text_area("Update Remark", value=selected['remark'])
                    
                    btn_col1, btn_col2 = st.columns(2)
                    
                    # ပြင်ဆင်ရန် (Update)
                    if btn_col1.button("🆙 Update Now", use_container_width=True):
                        supabase.table("blacklist").update({
                            "name": edit_name, 
                            "nrcno": edit_nrc, 
                            "remark": edit_remark
                        }).eq("srno", selected['srno']).execute()
                        st.success("Updated successfully!")
                        st.rerun()
                    
                    # ဖျက်ပစ်ရန် (Delete)
                    if btn_col2.button("🗑️ Delete Permanently", type="secondary", use_container_width=True):
                        supabase.table("blacklist").delete().eq("srno", selected['srno']).execute()
                        st.warning("Record deleted!")
                        st.rerun()
            else:
                st.info("No records found to edit.")

# --- ၅။ Inward Transaction Page ---
elif page == "🏦 Inward Transaction":
    st.title("🏦 Inward Transaction")
    yangon_tz = pytz.timezone('Asia/Yangon')
    now_yangon = datetime.now(yangon_tz)
    formatted_time = now_yangon.strftime("%Y-%m-%d %H:%M:%S")
    # ၁။ နောက်ဆုံး Transaction No ကို Database မှ ဆွဲထုတ်ခြင်း
    try:
        # inward_transactions table မှ နောက်ဆုံးသွင်းထားသော data ကို ယူသည်
        last_trans = supabase.table("inward_transactions").select("transaction_no").order("created_at", desc=True).limit(1).execute()
        
        if last_trans.data:
            # နောက်ဆုံးနံပါတ်ကို integer ပြောင်းပြီး ၁ ပေါင်းသည်
            last_no = int(last_trans.data[0]['transaction_no'])
            new_no = f"{last_no + 1:04d}" # 0001, 0002 ပုံစံဖြစ်အောင် 0 လေးလုံး format သတ်မှတ်သည်
        else:
            new_no = "0001" # Table ထဲမှာ ဘာမှမရှိသေးရင် 0001 က စမည်
    except Exception:
        new_no = "0001" # Error တက်ခဲ့ရင်လည်း 0001 ကပင် စမည်
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
    if st.button("💾 Save Inward Transaction", type="primary", use_container_width=True):
        # မဖြစ်မနေ လိုအပ်သော field များ ရှိမရှိ အရင်စစ်ပါ
        if r_name and r_nrc and s_name:
            try:
                # ၁။ Blacklist စစ်ဆေးခြင်း
                check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
                
                if len(check_bl.data) > 0:
                    st.error(f"❌ STOP! {r_nrc} သည် Blacklist စာရင်းဝင် ({check_bl.data[0]['name']}) ဖြစ်နေပါသည်။")
                else:
                    # ၂။ အချက်အလက်များကို Dictionary ပုံစံဖြင့် စုစည်းပါ
                    data_to_save = {
                        "branch": branch,
                        "transaction_no": trans_no,
                        "r_name": r_name,
                        "r_nrc": r_nrc,
                        "r_address": r_address,
                        "r_phone": r_phone,
                        "r_purpose": r_purpose,
                        "r_state": r_state,
                        "r_withdraw_point": r_point,
                        "r_remark": r_remark,
                        "s_name": s_name,
                        "s_id": s_id,
                        "s_country": s_country,
                        "currency": currency,
                        "amount": float(amount),
                        "mmk_rate": float(mmk_rate),
                        "mmk_allowance": float(mmk_allowance),
                        "usd_equiv": float(usd_equiv),
                        "total_mmk": float(total_mmk)
                    }

                    # ၃။ Supabase 'inward_transactions' table ထဲသို့ ထည့်သွင်းပါ
                    res = supabase.table("inward_transactions").insert(data_to_save).execute()
                    
                    if res.data:
                        st.success(f"✅ Transaction No. {trans_no} ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
                        st.balloons() # အောင်မြင်မှု အောင်ပွဲခံခြင်း
                        st.rerun() # Form ကို Reset လုပ်ရန်
            
            except Exception as e:
                st.error(f"Database Error: {e}")
        else:
            st.warning("⚠️ Receiver Name, NRC နှင့် Sender Name တို့ကို မဖြစ်မနေ ဖြည့်သွင်းပေးပါ။")
