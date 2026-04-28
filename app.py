import pandas as pd
import streamlit as st
import pytz
from supabase import create_client, Client
from datetime import datetime
# --- အချိန်သတ်မှတ်ချက် (Login မဝင်ခင်ကတည်းက သိနေစေရန် ဤနေရာတွင်ထားပါ) ---
yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)
def safe_float(val):
    try:
        if val is None or str(val).strip() == "":
            return 0.0
        return float(val)
    except (ValueError, TypeError):
        return 0.0
# --- ၁။ Setup & Connections ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# --- ၁။ Login Session စတင်ခြင်း ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- ၂။ Login Page ပြသခြင်း ---
if not st.session_state['logged_in']:
    st.title("🔐 Admin Login System")
    
    with st.form("login_form"):
        input_user = st.text_input("User ID")
        input_pass = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            try:
                # Database ထဲတွင် User ID နှင့် Password ကိုက်မကိုက် စစ်ဆေးခြင်း
                res = supabase.table("user_setup")\
                    .select("*")\
                    .eq("user_id", input_user)\
                    .eq("password", input_pass)\
                    .execute()
                
                if res.data:
                    st.session_state['logged_in'] = True
                    st.success("✅ Login Successful!")
                    st.rerun() # Login အောင်မြင်လျှင် စာမျက်နှာကို Refresh လုပ်ရန်
                else:
                    st.error("❌ Invalid User ID or Password")
            except Exception as e:
                st.error(f"Login Error: {e}")
    
    st.stop() # Login မဝင်မချင်း အောက်က Code တွေကို ဆက်မသွားစေရန် တားထားခြင်း

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
elif page == "📋 Blacklist Info":
    st.title("📋 Blacklist Management")
    
    # ၁။ NRC Data ကို ဒေတာအမျိုးအစား မှန်မှန်ကန်ကန် ဆွဲထုတ်ခြင်း
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        if not nrc_df.empty:
            # Database က data များကို စာသားပြောင်းပြီး space များ ဖြတ်ထားပါသည်
            nrc_df['state_no'] = nrc_df['state_no'].astype(str).str.strip()
            nrc_df['short_en'] = nrc_df['short_en'].astype(str).str.strip()
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

# Form clear ဖြစ်စေရန် Initial state သတ်မှတ်ခြင်း
if 'name_input' not in st.session_state:
    st.session_state.name_input = ""
if 'nrc_num_input' not in st.session_state:
    st.session_state.nrc_num_input = ""
if 'remark_input' not in st.session_state:
    st.session_state.remark_input = ""

with st.expander("➕ Add New Blacklist Record", expanded=True):
    # session_state ကို text_input များတွင် ချိတ်ဆက်ထားပါသည်
    name = st.text_input("Full Name (အမည်)", key="name_input")
    
    st.write("🆔 NRC Number (New Format)")
    c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
    
    with c1:
        all_states = sorted(nrc_df['state_no'].unique().tolist(), key=lambda x: int(x) if x.isdigit() else 99)
        selected_state = st.selectbox("State No", all_states, key="st_key")
    with c2:
        filtered_tsps = nrc_df[nrc_df['state_no'] == selected_state]['short_en'].unique().tolist()
        selected_tsp = st.selectbox("Township", sorted(filtered_tsps) if filtered_tsps else ["No Data"], key="tsp_key")
    with c3:
        nrc_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"], key="type_key")
    with c4:
        # NRC Number အတွက် session_state သုံးထားပါသည်
        nrc_num = st.text_input("Number", max_chars=6, key="nrc_num_input")

    reason = st.text_area("Reason for Blacklisting", key="remark_input")
    
    if st.button("Add to Blacklist", type="primary", use_container_width=True):
        if name and nrc_num and selected_tsp != "No Data":
            full_nrc = f"{selected_state}/{selected_tsp}{nrc_type}{nrc_num}"
            
            try:
                # Duplicate Check
                check_exists = supabase.table("blacklist").select("nrcno").eq("nrcno", full_nrc).execute()
                
                if check_exists.data:
                    st.error(f"❌ '{full_nrc}' သည် Database ထဲတွင် ရှိနှင့်ပြီးသားဖြစ်ပါသည်")
                else:
                    # Insert Data
                    supabase.table("blacklist").insert({
                        "name": name, "nrcno": full_nrc, "remark": reason
                    }).execute()
                    
                    st.success("✅ Saved Successfully!")
                    
                    # Form ကို Clear လုပ်ရန် session state များကို reset လုပ်ခြင်း
                    st.session_state.name_input = ""
                    st.session_state.nrc_num_input = ""
                    st.session_state.remark_input = ""
                    
                    import time
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Save Error: {e}")
            else:
                st.warning("⚠️ ကျေးဇူးပြု၍ အချက်အလက်များ ပြည့်စုံစွာ ဖြည့်စွက်ပေးပါ။")
    st.subheader("🛠️ Search & Edit/Delete Blacklist")

# ၁။ Search Input (အမည် သို့မဟုတ် NRC ဖြင့် ရှာရန်)
search_query = st.text_input("Search by Name or NRC", placeholder="ဥပမာ- 13/nakhana")

if search_query:
    try:
        # ilike ကိုသုံးပြီး ရှာဖွေခြင်း (စာလုံးအကြီးအသေး မရွေးပါ)
        # အမည် သို့မဟုတ် မှတ်ပုံတင်နံပါတ်ထဲမှာ search_query ပါဝင်တာနဲ့ ဆွဲထုတ်ပါမယ်
        search_res = supabase.table("blacklist").select("*").or_(f"name.ilike.%{search_query}%,nrcno.ilike.%{search_query}%").execute()
            
        if search_res.data:
            st.success(f"Found {len(search_res.data)} matching records.")
            search_options = {f"{r['name']} ({r['nrcno']})": r for r in search_res.data}
            selected_key = st.selectbox("Select precise record to modify", list(search_options.keys()))
                
            if selected_key:
                target = search_options[selected_key]
                    
            # Edit Form ကို Box လေးဖြင့် ပြသခြင်း
            with st.container(border=True):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    u_name = st.text_input("Edit Name", value=target.get('name', ''))
                    u_nrc = st.text_input("Edit NRC", value=target.get('nrcno', ''))
                with col_e2:
             # remark ဟု ပြောင်းလဲအသုံးပြုထားပါသည်
                    u_reason = st.text_area("Edit Reason", value=target.get('remark', '') or "", height=115)
                        
                    b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("🔄 Update Record", type="secondary", use_container_width=True):
                        try:
                # ဤစာကြောင်းများအားလုံး try: အောက်တွင် တစ်ဆင့်ဝင်နေရပါမည်
                            supabase.table("blacklist").update({
                            "name": u_name,
                            "nrcno": u_nrc,
                            "remark": u_reason
                        }).eq("id", target['id']).execute()
                
            # အောက်ပါ စာကြောင်း ၂ ကြောင်းကို အထဲသို့ တစ်ဆင့် တိုးပေးပါ
                        st.success("✅ Updated successfully!")
                        st.rerun()
                
                    except Exception as e:
                        st.error(f"Update Error: {e}")
                                    
                with b_col2:
                    if st.button("🗑️ Delete Record", type="primary", use_container_width=True):
                        try:
                            supabase.table("blacklist").delete().eq("id", target['id']).execute()
                            st.warning("🗑️ Deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete Error: {e}")
else:
                st.info("No matching records found. (ရိုက်ထည့်ထားသော စာလုံးပေါင်း မှန်မမှန် ပြန်စစ်ပေးပါ)")
        except Exception as e:
            st.error(f"Search Error: {e}")
    else:
        st.info("Please enter a name or NRC to start searching.")
    # --- ၇။ Inward Transaction Page ---
elif page == "🏦 Inward Transaction":
        # ၁။ နောက်ဆုံး Transaction No ကို Database မှ ဆွဲထုတ်ခြင်း
        try:
            last_trans = supabase.table("inward_transactions").select("transaction_no").order("created_at", desc=True).limit(1).execute()
            if last_trans.data:
                last_no = int(last_trans.data[0]['transaction_no'])
                new_no = f"{last_no + 1:04d}"
            else:
                new_no = "0001"
        except Exception:
            new_no = "0001"

    # --- Header Information ---
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        st.text_input("Date:", value=now_yangon.strftime("%Y-%m-%d %H:%M:%S"), disabled=True)
    with h_col2:
        # Branch တွေကို DB ထဲက ဆွဲထုတ်သုံးရင် ပိုကောင်းပါတယ် (လက်ရှိ version အတွက် selectbox ပဲထားပါဦးမည်)
        branch = st.selectbox("Select Branch", ["Yangon Branch", "Mandalay Branch", "Nay Pyi Taw Branch"])
    with h_col3:
        trans_no = st.text_input("Transaction No:", value=new_no)

    # --- ၂။ RECEIVER INFORMATION ---
    st.subheader("🔵 RECEIVER INFORMATION :")
    with st.container(border=True):
        r_col1, r_col2 = st.columns(2)
        r_name = r_col1.text_input("Receiver Name:")
        r_nrc = r_col2.text_input("Receiver NRC:")

        r_addr_col, r_ph_col, r_purp_col = st.columns([2, 1, 1])
        r_address = r_addr_col.text_input("Receiver Address:")
        r_phone = r_ph_col.text_input("Receiver Phone:")
        r_purpose = r_purp_col.selectbox("Purpose", ["Family Support", "Business", "Gift"])

        r_state_col, r_point_col = st.columns(2)
        r_state = r_state_col.selectbox("State & Division", ["Yangon", "Mandalay", "Shan", "Bago"])
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
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        with s_mmk_col:
            mmk_rate = st.number_input("MMK Rate", min_value=0.0, format="%.2f")
            mmk_allowance = st.number_input("MMK Allowance", min_value=0.0, format="%.2f")
        with s_usd_col:
            usd_equiv = st.number_input("USD Equivalent", min_value=0.0)
            total_mmk = st.number_input("Total MMK", min_value=0.0)
        # တွက်ချက်ရရှိတဲ့ total ကို variable တစ်ခုထဲ သိမ်းထားပါမယ်
        calc_total_mmk = (amount * mmk_rate) + mmk_allowance
        st.markdown(f"### Total MMK: **{calc_total_mmk:,.2f}**")

    # --- ၄။ SAVE ACTION ---
    # မှတ်ချက် - ဒီ button သည် elif page == "🏦 Inward Transaction": ရဲ့ အောက်မှာ Space ခြားပြီး ရှိနေရပါမယ်
    if st.button("💾 Save Inward Transaction", type="primary", use_container_width=True):
        if r_name and r_nrc:
            try:
                # Blacklist Check
                check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
                
                if len(check_bl.data) > 0:
                    st.error(f"❌ Blacklisted User: {check_bl.data[0]['name']}")
                else:
                    # Data Preparation
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
                        "amount": float(amount),
                        "mmk_rate": float(mmk_rate),
                        "mmk_allowance": float(mmk_allowance),
                        "usd_equiv": float(usd_equiv) if usd_equiv else 0,
                        # အပေါ်မှာ တွက်ထားတဲ့ calc_total_mmk ကို တိုက်ရိုက်သိမ်းပါမယ်
                        "total_mmk": float(calc_total_mmk) 
                    }

                    # Database Insert
                    response = supabase.table("inward_transactions").insert(new_data).execute()
                    
                    if response.data:
                        st.success("✅ ဒေတာကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
                        st.balloons()
                        import time
                        time.sleep(1.5)
                        st.rerun()

            except Exception as e:
                st.error(f"Database Error: {e}")
        else:
            st.warning("⚠️ Receiver Name နှင့် NRC ကို ဖြည့်စွက်ပါ။")            
            # --- ၂။ System Control Logic ---
if page == "⚙️ System Control":
    st.title("⚙️ System Control & Setup")
    
    # ၁။ Tab များခွဲခြားခြင်း
    tab1, tab2, tab3 = st.tabs(["🌍 Country Setup", "🏢 Branch Setup", "👤 User Setup"])

    # --- (၁) Country Setup ---
    with tab1:
        st.subheader("Country Management")
        with st.expander("➕ Add New Country"):
            with st.form("country_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                c_code = c1.text_input("Country Code")
                c_name = c2.text_input("Country Name")
                c_curr = c1.text_input("Currency (e.g. THB)")
                c_remark = c2.text_area("Remark")
                if st.form_submit_button("Save Country"):
                    if c_code and c_name:
                        supabase.table("country_setup").insert({
                            "country_code": c_code, "country_name": c_name, "currency": c_curr, "remark": c_remark
                        }).execute()
                        st.success(f"Country {c_name} saved!")
                        st.rerun()

        st.divider()
        st.subheader("📋 Country List")
        res_c = supabase.table("country_setup").select("*").execute()
        if res_c.data:
            df_c = pd.DataFrame(res_c.data)
            st.dataframe(df_c[['country_code', 'country_name', 'currency', 'remark']], use_container_width=True)
            
            # Update/Delete Section
            target_c = st.selectbox("Select Country to Edit", ["-- Select --"] + [r['country_name'] for r in res_c.data])
            if target_c != "-- Select --":
                c_data = next(r for r in res_c.data if r['country_name'] == target_c)
                with st.container(border=True):
                    up_cname = st.text_input("Edit Name", value=c_data['country_name'])
                    up_ccurr = st.text_input("Edit Currency", value=c_data['currency'])
                    if st.button("Update Country"):
                        supabase.table("country_setup").update({"country_name": up_cname, "currency": up_ccurr}).eq("id", c_data['id']).execute()
                        st.success("Updated!")
                        st.rerun()

    # --- (၂) Branch Setup ---
    with tab2:
        st.subheader("Branch Management")
        with st.expander("➕ Add New Branch"):
            with st.form("branch_form", clear_on_submit=True):
                b1, b2 = st.columns(2)
                b_code = b1.text_input("Branch Code")
                b_name = b2.text_input("Branch Name")
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
                    st.rerun()

        st.divider()
        st.subheader("📋 Branch List")
        res_b = supabase.table("branch_setup").select("*").execute()
        if res_b.data:
            df_b = pd.DataFrame(res_b.data)
            st.dataframe(df_b[['branch_code', 'branch_name', 'country', 'phone_no']], use_container_width=True)

    # --- (၃) User Setup (Everything now inside tab3) ---
    with tab3:
        st.subheader("👤 User Management")
        with st.expander("➕ Add New User"):
            with st.form("user_new_form", clear_on_submit=True):
                u_id = st.text_input("User ID")
                u_pwd = st.text_input("Password", type="password")
                u_confirm = st.text_input("Confirm Password", type="password")
                u_remark = st.text_area("Remark")
                if st.form_submit_button("Create User"):
                    if u_id and u_pwd == u_confirm:
                        supabase.table("user_setup").insert({"user_id": u_id, "password": u_pwd, "remark": u_remark}).execute()
                        st.success(f"User {u_id} created!")
                        st.rerun()

        st.divider()
        st.subheader("📋 Registered Users List")
        res_u = supabase.table("user_setup").select("*").execute()
        if res_u.data:
            df_u = pd.DataFrame(res_u.data)
            st.dataframe(df_u[['user_id', 'remark', 'created_at']], use_container_width=True)

            st.subheader("🛠️ Edit User Account")
            u_list = [u['user_id'] for u in res_u.data]
            target_uid = st.selectbox("Choose a User ID to modify:", options=["-- Select --"] + u_list)
            
            if target_uid != "-- Select --":
                user_data = next(u for u in res_u.data if u['user_id'] == target_uid)
                with st.container(border=True):
                    up_uid = st.text_input("Update User ID", value=user_data['user_id'])
                    # Password ကိုပါ ပြင်လို့ရအောင် ထည့်ထားပေးပါတယ်
                    up_pwd = st.text_input("Update Password", value=user_data['password'], type="password")
                    up_remark = st.text_area("Update Remark", value=user_data['remark'])
                    
                    col_u1, col_u2 = st.columns(2)
                    if col_u1.button("🆙 Update User Now", type="primary", use_container_width=True):
                        supabase.table("user_setup").update({
                            "user_id": up_uid, "password": up_pwd, "remark": up_remark
                        }).eq("id", user_data['id']).execute()
                        st.success("✅ Information updated!")
                        st.rerun()
                    
                    if col_u2.button("🗑️ Delete User", use_container_width=True):
                        supabase.table("user_setup").delete().eq("id", user_data['id']).execute()
                        st.warning("User deleted!")
                        st.rerun()
