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
page = st.sidebar.radio("Go to:", 
["📊 Dashboard", 
 "🔍 Search Transactions", 
 "📋 Blacklist Info", 
 "🏦 Inward Transaction",
"⚙️ System Control"])
st.sidebar.markdown("---")
st.sidebar.info("System Version 2.0v")

# --- ၄။ Dashboard Page (Login ဝင်ပြီးလျှင် အရင်ဆုံးမြင်ရမည့်စာမျက်နှာ) ---
if page == "📊 Dashboard":
    st.title("📈 Transaction Dashboard")
    st.markdown(f"**Last Updated:** {now_yangon.strftime('%Y-%m-%d %H:%M:%S')} (Yangon Time)")

    try:
        # ၁။ ဒေတာဆွဲထုတ်ခြင်း (Column name များအား သေချာစွာ စစ်ဆေးပါ)
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        
        if res.data:
            df_dash = pd.DataFrame(res.data)
            
            # ၂။ Date Conversion (Yangon Time သို့ ပြောင်းလဲခြင်း)
            df_dash['created_at'] = pd.to_datetime(df_dash['created_at']).dt.tz_convert('Asia/Yangon')
            
            # ယနေ့ရက်စွဲ၊ လ၊ နှစ် ကို သတ်မှတ်ခြင်း
            today = now_yangon.date()
            this_month = now_yangon.month
            this_year = now_yangon.year

            # ၃။ Filtering & Summing (ဂဏန်းများ ပေါင်းခြင်း)
            daily_sum = df_dash[df_dash['created_at'].dt.date == today]['amount'].sum()
            monthly_sum = df_dash[(df_dash['created_at'].dt.month == this_month) & 
                                  (df_dash['created_at'].dt.year == this_year)]['amount'].sum()
            yearly_sum = df_dash[df_dash['created_at'].dt.year == this_year]['amount'].sum()
            
            # စမ်းသပ်ရန်အတွက် Data ရှိပါက Console တွင်ပြရန်
            # st.write(f"Debug: Found {len(df_dash)} records") 
        else:
            daily_sum = monthly_sum = yearly_sum = 0
            st.info("ℹ️ Database ထဲတွင် Transaction data မရှိသေးပါ။")

    except Exception as e:
        st.error(f"❌ Dashboard Error: {e}")
        daily_sum = monthly_sum = yearly_sum = 0

    # --- ၄။ UI Display (ရောင်စုံ Card များ) ---
    st.subheader("Daily Transaction")
    d1, d2 = st.columns(2)
    d1.info(f"### {daily_sum:,.2f} \n 📉 Daily Inward")
    d2.info(f"### 0.00 \n 📉 Daily Outward")

    st.divider()

    st.subheader("Monthly Transaction")
    m1, m2 = st.columns(2)
    m1.warning(f"### {monthly_sum:,.2f} \n 📈 Monthly Inward") 
    m2.warning(f"### 0.00 \n 📈 Monthly Outward")

    st.divider()

    st.subheader("Yearly Transaction")
    y1, y2 = st.columns(2)
    y1.error(f"### {yearly_sum:,.2f} \n 📊 Yearly Inward")
    y2.error(f"### 0.00 \n 📊 Yearly Outward")

# --- ၅။ Search Transactions Page Logic ---
if page == "🔍 Search Transactions":
    st.title("🔍 Search & Filter Transactions")
    st.markdown("ရက်စွဲအလိုက် ငွေလွှဲစာရင်းများကို ရှာဖွေရန်")

    # Search Filters
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            s_date = st.date_input("Start Date", value=now_yangon.date())
        with col2:
            e_date = st.date_input("End Date", value=now_yangon.date())
        with col3:
            st.write("##")
            btn_search = st.button("Search Now", type="primary", use_container_width=True)

    # Database မှ ဒေတာရှာဖွေခြင်း
    try:
        # ဒေတာအားလုံးကို အရင်ယူသည် (သို့မဟုတ် date အလိုက် filter တိုက်ရိုက်လုပ်နိုင်သည်)
        res = supabase.table("inward_transactions").select("*").order("created_at", desc=True).execute()
        
        if res.data:
            df_search = pd.DataFrame(res.data)
            # Date format ပြောင်းလဲခြင်း
            df_search['created_at'] = pd.to_datetime(df_search['created_at']).dt.tz_convert('Asia/Yangon')
            df_search['Date'] = df_search['created_at'].dt.date
            
            # Button နှိပ်မှ Filter လုပ်ခြင်း
            if btn_search:
                mask = (df_search['Date'] >= s_date) & (df_search['Date'] <= e_date)
                result_df = df_search.loc[mask]
                
                if not result_df.empty:
                    st.success(f"Found {len(result_df)} transactions.")
                    # လိုအပ်သော Column များကိုသာ ရွေးပြခြင်း
                    display_cols = [
                        'transaction_no', 'branch', 'r_name', 'r_nrc', 
                        's_name', 'amount', 'currency', 'total_mmk', 'Date'
                    ]
                    st.dataframe(result_df[display_cols], use_container_width=True)
                    
                    # Excel ထုတ်ရန် Download Button (Optional)
                    csv = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download as CSV", data=csv, file_name="search_results.csv", mime="text/csv")
                else:
                    st.warning("ရွေးချယ်ထားသော ရက်စွဲအတွင်း ဒေတာမရှိပါ။")
            else:
                st.info("ရှာဖွေရန် ရက်စွဲရွေးပြီး Search Now ကို နှိပ်ပါ။")
        else:
            st.info("Database ထဲတွင် ဒေတာမရှိသေးပါ။")
            
    except Exception as e:
        st.error(f"Search Error: {e}")

# --- ၆။ Blacklist System Page ---
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

# --- ၇။ Inward Transaction Page ---
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
        trans_no = st.text_input("Transaction No:", value="0001")

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

    # --- ၈။ SAVE ACTION ---
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
        if r_name and r_nrc:
            try:
                # ၁။ Blacklist အရင်စစ်သည်
                check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
                
                if len(check_bl.data) > 0:
                    st.error(f"❌ Blacklisted User: {check_bl.data[0]['name']}")
                else:
                    # ၂။ ဒေတာများကို စုစည်းသည်
                    new_data = {
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
                        "amount": float(amount) if amount else 0,
                        "mmk_rate": float(mmk_rate) if mmk_rate else 0,
                        "mmk_allowance": float(mmk_allowance) if mmk_allowance else 0,
                        "usd_equiv": float(usd_equiv) if usd_equiv else 0,
                        "total_mmk": float(total_mmk) if total_mmk else 0
                    }

                    # ၃။ Database ထဲသို့ ထည့်သည်
                    response = supabase.table("inward_transactions").insert(new_data).execute()
                    
                    if response.data:
                        st.success("✅ ဒေတာကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
                        st.balloons()
                        # ခဏစောင့်ပြီးမှ Refresh လုပ်ရန်
                        import time
                        time.sleep(2)
                        st.rerun()
            except Exception as e:
                st.error(f"Error saving data: {e}") # ဘာလို့ မသိမ်းလဲဆိုတဲ့ အဖြေကို ဤနေရာတွင် ပြပါလိမ့်မည်
        else:
            st.warning("⚠️ Receiver Name နှင့် NRC ကို ဖြည့်စွက်ပါ။")
            # --- ၂။ System Control Logic ---
if page == "⚙️ System Control":
    st.title("⚙️ System Control & Setup")
    
    # Tab များခွဲခြင်း
    tab1, tab2, tab3 = st.tabs(["🌍 Country Setup", "🏢 Branch Setup", "👤 User Setup"])

    # --- (၁) Country Setup ---
    with tab1:
        st.subheader("Add New Country")
        with st.form("country_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            c_code = c1.text_input("Country Code")
            c_name = c2.text_input("Country Name")
            c_curr = c1.text_input("Currency (e.g. THB, USD)")
            c_remark = c2.text_area("Remark")
            
            if st.form_submit_button("Save Country"):
                if c_code and c_name:
                    supabase.table("country_setup").insert({
                        "country_code": c_code, "country_name": c_name, 
                        "currency": c_curr, "remark": c_remark
                    }).execute()
                    st.success(f"Country {c_name} saved!")
                else:
                    st.warning("Please fill required fields.")

    # --- (၂) Branch Setup ---
    with tab2:
        st.subheader("Add New Branch")
        with st.form("branch_form", clear_on_submit=True):
            b1, b2 = st.columns(2)
            b_code = b1.text_input("Branch Code")
            b_name = b2.text_input("Branch Name")
            
            # Country List ကို Database မှ ပြန်ယူခြင်း
            countries = supabase.table("country_setup").select("country_name").execute()
            c_list = [r['country_name'] for r in countries.data] if countries.data else []
            
            b_country = b1.selectbox("Country", options=c_list)
            b_curr = b2.text_input("Currency")
            b_ph = b1.text_input("Phone No")
            b_addr = b2.text_area("Address")
            
            if st.form_submit_button("Save Branch"):
                supabase.table("branch_setup").insert({
                    "branch_code": b_code, "branch_name": b_name, "country": b_country,
                    "currency": b_curr, "phone_no": b_ph, "address": b_addr
                }).execute()
                st.success(f"Branch {b_name} saved!")

    # --- (၃) User Setup Page Logic ---
with tab3:
    st.subheader("👤 User Management System")
    
    # ၁။ User အသစ်ထည့်ရန် (Expander သုံးထား၍ မျက်စိမရှုပ်ပါ)
    with st.expander("➕ Add New User"):
        with st.form("user_new_form", clear_on_submit=True):
            u_id = st.text_input("User ID")
            u_pwd = st.text_input("Password", type="password")
            u_confirm = st.text_input("Confirm Password", type="password")
            u_remark = st.text_area("Remark")
            
            if st.form_submit_button("Create User"):
                if u_id and u_pwd == u_confirm:
                    try:
                        supabase.table("user_setup").insert({
                            "user_id": u_id, "password": u_pwd, "remark": u_remark
                        }).execute()
                        st.success(f"User {u_id} created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please check ID or Password matching.")

    st.divider()

    # ၂။ လက်ရှိ User များကို ဇယားဖြင့် အရင်ပြခြင်း
    st.subheader("📋 Registered Users List")
    try:
        # User အချက်အလက်များ ဆွဲထုတ်ခြင်း
        res_u = supabase.table("user_setup").select("user_id, remark, created_at, id").execute()
        
        if res_u.data:
            df_u = pd.DataFrame(res_u.data)
            # ဇယားကွက်ဖြင့် ပြသခြင်း
            st.dataframe(df_u[['user_id', 'remark', 'created_at']], use_container_width=True)

            # ၃။ ပြင်ဆင်ရန် သို့မဟုတ် ဖျက်ရန် ရွေးချယ်သည့်အပိုင်း
            st.subheader("🛠️ Select User to Modify")
            # Selectbox ဖြင့် ရွေးချယ်စေခြင်း
            u_list = [u['user_id'] for u in res_u.data]
            target_uid = st.selectbox("Choose a User ID to edit/delete:", options=["-- Select --"] + u_list)
            
            if target_uid != "-- Select --":
                # ရွေးချယ်လိုက်သော User ၏ data ကို ရှာခြင်း
                user_data = next(u for u in res_u.data if u['user_id'] == target_uid)
                
                with st.container(border=True):
                    # ပြင်ဆင်ရန် Field များ
                    edit_uid = st.text_input("Update User ID", value=user_data['user_id'])
                    edit_remark = st.text_area("Update Remark", value=user_data['remark'])
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    # Update Button
                    if col_btn1.button("🆙 Update User Now", type="primary", use_container_width=True):
                        supabase.table("user_setup").update({
                            "user_id": edit_uid, "remark": edit_remark
                        }).eq("id", user_data['id']).execute()
                        st.success("Successfully updated!")
                        st.rerun()
                    
                    # Delete Button
                    if col_btn2.button("🗑️ Delete User Permanently", use_container_width=True):
                        supabase.table("user_setup").delete().eq("id", user_data['id']).execute()
                        st.warning("User deleted!")
                        st.rerun()
        else:
            st.info("No users found in database.")
            
    except Exception as e:
        # ဤနေရာတွင် Syntax မှန်ကန်ရန် try-except ကို သေချာပိတ်ထားပါ
        st.error(f"Connection Error: {e}")
