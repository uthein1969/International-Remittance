import streamlit as st

# ---------------- PAGE CONFIG (MUST FIRST) ----------------
st.set_page_config(layout="wide")

# ---------------- IMPORTS ----------------
import pytz
from supabase import create_client
from datetime import datetime

# ---------------- SUPABASE ----------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# ---------------- TIMEZONE ----------------
yangon_tz = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon_tz)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = ""

# ---------------- LOGIN PAGE ----------------
if not st.session_state["logged_in"]:

    st.title("🔐 Admin Login System")

    with st.form("login_form"):

        input_user = st.text_input("User ID")
        input_pass = st.text_input("Password", type="password")

        login_btn = st.form_submit_button("Login")

        if login_btn:

            try:
                # ✔ SINGLE SAFE CALL
                res = supabase.table("user_setup").select("*").execute()

                users = res.data or []

                # ✔ PURE PYTHON CHECK (NO NETWORK CHAOS)
                user_found = any(
                    u.get("user_id") == input_user and u.get("password") == input_pass
                    for u in users
                )

                if user_found:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = input_user
                    st.success("Login Successful")
                    st.stop()
                else:
                    st.error("Invalid credentials")

            except Exception as e:
                st.error(f"Login Error: {str(e)}")

    st.stop()

# ---------------- DASHBOARD ----------------
st.title("🏠 Dashboard")

st.success(f"Welcome {st.session_state['username']} 👋")

if st.button("Logout"):

    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

    st.rerun()

# --- ၃။ Main System  ---
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

# --- ၄။ Dashboard Page (Currency အလိုက် သီးသန့် စာရင်းခွဲပြသခြင်းစနစ်) ---
if page == "📊 Dashboard":
    st.title("📈 Transaction Dashboard")
    st.markdown(f"**Last Updated:** {now_yangon.strftime('%Y-%m-%d %H:%M:%S')} (Yangon Time)")

    # --- ၁။ Supabase မှ ဒေတာအားလုံးကို ကြိုတင်ဆွဲထုတ်ခြင်း ---
    try:
        res = supabase.table("inward_transactions").select("amount, total_mmk, currency, created_at").execute()
        if res.data:
            df_dash = pd.DataFrame(res.data)
            df_dash['created_at'] = pd.to_datetime(df_dash['created_at']).dt.tz_convert('Asia/Yangon')
            df_dash['Date'] = df_dash['created_at'].dt.date
            df_dash['Year'] = df_dash['created_at'].dt.year
            df_dash['Month_Num'] = df_dash['created_at'].dt.month
        else:
            df_dash = pd.DataFrame(columns=["amount", "total_mmk", "currency", "created_at", "Date", "Year", "Month_Num"])
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        df_dash = pd.DataFrame(columns=["amount", "total_mmk", "currency", "created_at", "Date", "Year", "Month_Num"])

    # 💡 Currency အလိုက် စာရင်းခွဲထုတ်ပေးမည့် Helper Function
    def display_currency_summary(df_filtered):
        if df_filtered.empty:
            st.markdown("<span style='color:gray;'>ဒီကာလအတွင်း ငွေလွှဲဒေတာ မရှိပါ။</span>", unsafe_allow_html=True)
            return
        
        # Currency အလိုက် Group ဖွဲ့ပြီး ပေါင်းခြင်း
        summary = df_filtered.groupby('currency').agg({
            'amount': 'sum',
            'total_mmk': 'sum'
        }).reset_index()
        
        # စာရင်းများကို Layout အလှပုံစံဖြင့် ထုတ်ပြခြင်း
        for idx, row in summary.iterrows():
            st.markdown(f"💰 **{row['amount']:,.2f} {row['currency']}** *(≈ {row['total_mmk']:,.2f} MMK)*")

    st.divider()

    # =========================================================================
    # 📉 (၁) DAILY TRANSACTION SECTION
    # =========================================================================
    st.subheader("📆 Daily Transaction")
    
    with st.container(border=True):
        col_d1, col_d2, col_d3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
        with col_d1:
            d_s_date = st.date_input("From Date", value=now_yangon.date(), key="d_s")
        with col_d2:
            d_e_date = st.date_input("To Date", value=now_yangon.date(), key="d_e")
        with col_d3:
            btn_d_search = st.button("🔍 Search Daily", type="primary", use_container_width=True, key="btn_d")

    if not df_dash.empty:
        d_mask = (df_dash['Date'] >= d_s_date) & (df_dash['Date'] <= d_e_date)
        df_daily = df_dash.loc[d_mask]
        daily_count = len(df_daily)
    else:
        df_daily = pd.DataFrame()
        daily_count = 0

    d_card1, d_card2 = st.columns([2, 1])
    with d_card1.container(border=True):
        st.markdown("📉 **Daily Inward Subtotals (Currency အလိုက်)**")
        display_currency_summary(df_daily)
    with d_card2.container(border=True):
        st.markdown("🔢 **Transaction Count**")
        st.markdown(f"### {daily_count}")

    st.divider()

    # =========================================================================
    # 📈 (၂) MONTHLY TRANSACTION SECTION
    # =========================================================================
    st.subheader("📅 Monthly Transaction (From Month to To Month)")
    
    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    current_month_name = months_list[now_yangon.month - 1]

    with st.container(border=True):
        m_year_options = sorted(df_dash['Year'].unique().tolist()) if not df_dash.empty else [now_yangon.year]
        if now_yangon.year not in m_year_options:
            m_year_options.append(now_yangon.year)
        selected_m_year = st.selectbox("Select Year for Monthly Report", sorted(m_year_options, reverse=True), key="m_yr_sel")
        
        col_m1, col_m2, col_m3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
        with col_m1:
            from_m_name = st.selectbox("From Month", months_list, index=0, key="from_m")
            from_m_num = months_list.index(from_m_name) + 1
        with col_m2:
            to_m_name = st.selectbox("To Month", months_list, index=months_list.index(current_month_name), key="to_m")
            to_m_num = months_list.index(to_m_name) + 1
        with col_m3:
            btn_m_search = st.button("🔍 Search Months", type="primary", use_container_width=True, key="btn_m")

    if not df_dash.empty:
        m_mask = (df_dash['Year'] == selected_m_year) & (df_dash['Month_Num'] >= from_m_num) & (df_dash['Month_Num'] <= to_m_num)
        df_monthly = df_dash.loc[m_mask]
        monthly_count = len(df_monthly)
    else:
        df_monthly = pd.DataFrame()
        monthly_count = 0

    m_card1, m_card2 = st.columns([2, 1])
    with m_card1.container(border=True):
        st.markdown(f"📈 **Monthly Inward Subtotals ({from_m_name} to {to_m_name})**")
        display_currency_summary(df_monthly)
    with m_card2.container(border=True):
        st.markdown("🔢 **Transaction Count**")
        st.markdown(f"### {monthly_count}")

    st.divider()

    # =========================================================================
    # 📊 (၃) YEARLY TRANSACTION SECTION
    # =========================================================================
    st.subheader("📊 Yearly Transaction (From Year to To Year)")
    
    year_options = sorted(df_dash['Year'].unique().tolist()) if not df_dash.empty else [now_yangon.year]
    if now_yangon.year not in year_options:
        year_options.append(now_yangon.year)
    year_options = sorted(year_options)

    with st.container(border=True):
        col_y1, col_y2, col_y3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
        with col_y1:
            from_year = st.selectbox("From Year", year_options, index=0, key="from_yr")
        with col_y2:
            to_year = st.selectbox("To Year", year_options, index=len(year_options)-1, key="to_yr")
        with col_y3:
            btn_y_search = st.button("🔍 Search Years", type="primary", use_container_width=True, key="btn_y")

    if not df_dash.empty:
        y_mask = (df_dash['Year'] >= from_year) & (df_dash['Year'] <= to_year)
        df_yearly = df_dash.loc[y_mask]
        yearly_count = len(df_yearly)
    else:
        df_yearly = pd.DataFrame()
        yearly_count = 0

    y_card1, y_card2 = st.columns([2, 1])
    with y_card1.container(border=True):
        st.markdown(f"📊 **Yearly Inward Subtotals ({from_year} to {to_year})**")
        display_currency_summary(df_yearly)
    with y_card2.container(border=True):
        st.markdown("🔢 **Transaction Count**")
        st.markdown(f"### {yearly_count}")
    
# --- ၅။ Search Transactions Page Logic ---
elif page == "🔍 Search Transactions":
    st.title("🔍 Search & Filter Transactions")
    st.markdown("Search for transactions by date")

    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1.2], vertical_alignment="bottom") #
        with col1:
            s_date = st.date_input("Start Date", value=now_yangon.date()) #
        with col2:
            e_date = st.date_input("End Date", value=now_yangon.date()) #
        with col3:
            
            btn_search = st.button("Search Now", type="primary", use_container_width=True) #

    try:
        res = supabase.table("inward_transactions").select("*").order("created_at", desc=True).execute()
        if res.data:
            df_search = pd.DataFrame(res.data)
            df_search['created_at'] = pd.to_datetime(df_search['created_at']).dt.tz_convert('Asia/Yangon')
            df_search['Date'] = df_search['created_at'].dt.date
            
            if btn_search:
                mask = (df_search['Date'] >= s_date) & (df_search['Date'] <= e_date)
                st.session_state['search_results'] = df_search.loc[mask].to_dict('records')

            # ရှာဖွေထားသော ရလဒ်များ ရှိပါက ပြသမည်
            if 'search_results' in st.session_state and st.session_state['search_results']:
                results_list = st.session_state['search_results']
                df_display = pd.DataFrame(results_list)
                
                st.success(f"Found {len(df_display)} transactions.")
                display_cols = ['transaction_no', 'branch', 'r_name', 'r_nrc', 's_name', 'amount', 'currency', 'total_mmk', 'Date']
                st.dataframe(df_display[display_cols], use_container_width=True)
                
                # CSV Download Button
                csv = df_display.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download as CSV", data=csv, file_name="search_results.csv", mime="text/csv")
                
                st.divider()
                
                # =========================================================================
                # 🖨️ TRANSACTION ရွေးချယ်ပြီး PAYOUT SLIP PRINT ထုတ်သည့်အပိုင်း
                # =========================================================================
                st.subheader("🖨️ Select Transaction to Print Payout Slip")
                
                # Dropdown တွင် ရွေးချယ်ရလွယ်ကူစေရန် format ပြုလုပ်ခြင်း
                trans_options = {f"No: {r['transaction_no']} | Receiver: {r['r_name']} ({r['r_nrc']})": r for r in results_list}
                selected_trans_key = st.selectbox("Choose a transaction from the list:", options=["-- Select Transaction --"] + list(trans_options.keys()))
                
                if selected_trans_key != "-- Select Transaction --":
                    sd = trans_options[selected_trans_key]
                    
                    # မျက်နှာပြင်ပေါ်တွင် Slip Preview ပြသခြင်း
                    with st.container(border=True):
                        st.markdown(f"### **Transaction No:** `{sd['transaction_no']}`")
                        # Database ထဲမှ created_at ကို အသုံးပြု၍ အချိန်ပြသခြင်း
                        formatted_time = pd.to_datetime(sd['created_at']).strftime('%Y-%m-%d %H:%M:%S')
                        st.markdown(f"**Branch:** {sd['branch']} | **Date & Time:** {formatted_time}")
                        st.divider()
                        
                        sc1, sc2 = st.columns(2)
                        with sc1:
                            st.markdown("#### 🔵 Receiver Details")
                            st.markdown(f"**Name:** {sd['r_name']}")
                            st.markdown(f"**NRC:** {sd['r_nrc']}")
                            st.markdown(f"**Phone:** {sd['r_phone']}")
                            st.markdown(f"**Address:** {sd['r_address']}, {sd['r_state']}")
                            st.markdown(f"**Withdraw Point:** {sd['r_withdraw_point']}")
                        with sc2:
                            st.markdown("#### 🟢 Sender Details")
                            st.markdown(f"**Name:** {sd['s_name']}")
                            st.markdown(f"**ID/Passport:** {sd['s_id']}")
                            st.markdown(f"**Country:** {sd['s_country']}")
                            st.markdown(f"**Purpose:** {sd['r_purpose']}")
                        st.divider()
                        st.info(f"## **Total Payout Amount:** {float(sd['total_mmk']):,.2f} MMK")

                    # Printer စနစ်သို့ HTML/JS ဖြင့် လှမ်းချိတ်ခြင်း
                    html_code = f"""
                    <script>
                    function printSlip() {{
                        var printContents = document.getElementById('print-area-search').innerHTML;
                        var originalContents = document.body.innerHTML;
                        document.body.innerHTML = printContents;
                        window.print();
                        document.body.innerHTML = originalContents;
                        window.location.reload();
                    }}
                    </script>
                    <div id="print-area-search" style="padding:20px; font-family:sans-serif; color:#000; background:#fff; border:1px solid #ccc; max-width:600px; margin:auto;">
                        <h2 style="text-align:center; margin-bottom:5px;">PAYOUT SLIP (REMITTANCE)</h2>
                        <p style="text-align:center; font-size:12px; margin-top:0;">Transaction No: <b>{sd['transaction_no']}</b></p>
                        <hr>
                        <p><b>Date:</b> {formatted_time} | <b>Branch:</b> {sd['branch']}</p>
                        <table style="width:100%; border-collapse:collapse; margin-top:15px;">
                            <tr>
                                <td style="width:50%; vertical-align:top; padding:5px; border:1px solid #ddd;">
                                    <h4>[ RECEIVER INFO ]</h4>
                                    <p>Name: {sd['r_name']}<br>NRC: {sd['r_nrc']}<br>Phone: {sd['r_phone']}<br>Point: {sd['r_withdraw_point']}</p>
                                </td>
                                <td style="width:50%; vertical-align:top; padding:5px; border:1px solid #ddd;">
                                    <h4>[ SENDER INFO ]</h4>
                                    <p>Name: {sd['s_name']}<br>ID/Pass: {sd['s_id']}<br>Country: {sd['s_country']}<br>Purpose: {sd['r_purpose']}</p>
                                </td>
                            </tr>
                        </table>
                        <div style="margin-top:20px; padding:15px; background:#f4f4f4; text-align:center; border:1px solid #ccc;">
                            <h3 style="margin:0;">TOTAL PAYOUT AMOUNT</h3>
                            <h2 style="margin:5px 0 0 0; color:#d9534f;">{float(sd['total_mmk']):,.2f} MMK</h2>
                        </div>
                        <br><br>
                        <table style="width:100%; text-align:center; margin-top:30px;">
                            <tr>
                                <td>____________________<br>Staff Signature</td>
                                <td>____________________<br>Customer Signature</td>
                            </tr>
                        </table>
                    </div>
                    """
                    
                    with st.expander("🖨️ Preview Print Layout (A4/Receipt)", expanded=True):
                        st.components.v1.html(html_code + "<br><button onclick='printSlip()' style='width:100%; padding:10px; background-color:#ff4b4b; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;'>🖨️ Click to Print Payout Slip</button>", height=520, scrolling=True)
            else:
                if btn_search:
                    st.warning("No data available for the selected date.")
        else:
            st.info("No Data in Database")
            
    except Exception as e:
        st.error(f"Search Error: {e}")

# --- ၆။ Blacklist System Page ---
elif page == "📋 Blacklist Info":
    st.title("📋 Blacklist Management")
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        if not nrc_df.empty:
            nrc_df['state_no'] = nrc_df['state_no'].astype(str).str.strip()
            nrc_df['short_en'] = nrc_df['short_en'].astype(str).str.strip()
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

    if 'name_input' not in st.session_state:
        st.session_state.name_input = ""
    if 'nrc_num_input' not in st.session_state:
        st.session_state.nrc_num_input = ""
    if 'remark_input' not in st.session_state:
        st.session_state.remark_input = ""

    with st.expander("➕ Add New Blacklist Record", expanded=True):
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
            nrc_num = st.text_input("Number", max_chars=6, key="nrc_num_input")

        reason = st.text_area("Reason for Blacklisting", key="remark_input")
        
        if st.button("Add to Blacklist", type="primary", use_container_width=True):
            if name and nrc_num and selected_tsp != "No Data":
                full_nrc = f"{selected_state}/{selected_tsp}{nrc_type}{nrc_num}"
                try:
                    check_exists = supabase.table("blacklist").select("nrcno").eq("nrcno", full_nrc).execute()
                    if check_exists.data:
                        st.error(f"❌ '{full_nrc}' is already exists")
                    else:
                        supabase.table("blacklist").insert({"name": name, "nrcno": full_nrc, "remark": reason}).execute()
                        st.success("✅ Saved Successfully!")
                        st.session_state.name_input = ""
                        st.session_state.nrc_num_input = ""
                        st.session_state.remark_input = ""
                        import time
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Save Error: {e}")
            else:
                st.warning("⚠️ Pls Fill Complete Information")

    st.subheader("🛠️ Search & Edit/Delete Blacklist")
    search_query = st.text_input("Search by Name or NRC", placeholder="ဥပမာ- 13/nakhana")

    if search_query:
        try:
            search_res = supabase.table("blacklist").select("*").or_(f"name.ilike.%{search_query}%,nrcno.ilike.%{search_query}%").execute()
            if search_res.data:
                st.success(f"Found {len(search_res.data)} matching records.")
                search_options = {f"{r['name']} ({r['nrcno']})": r for r in search_res.data}
                selected_key = st.selectbox("Select precise record to modify", list(search_options.keys()))
                
                if selected_key:
                    target = search_options[selected_key]
                    with st.container(border=True):
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            u_name = st.text_input("Edit Name", value=target.get('name', ''))
                            u_nrc = st.text_input("Edit NRC", value=target.get('nrcno', ''))
                        with col_e2:
                            u_reason = st.text_area("Edit Reason", value=target.get('remark', '') or "", height=115)
                        
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            if st.button("🔄 Update Record", type="secondary", use_container_width=True):
                                try:
                                    supabase.table("blacklist").update({"name": u_name, "nrcno": u_nrc, "remark": u_reason}).eq("id", target['id']).execute()
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
                st.info("No matching records found.")
        except Exception as e:
            st.error(f"Search Error: {e}")

# --- ၇။ Inward Transaction Page (Print Slip နှင့် Form Clear စနစ် ပါဝင်ပြီး) ---
elif page == "🏦 Inward Transaction":
    st.title("🏦 Inward Transaction Management")

    # --- ၁။ Form Clear ဖြစ်စေရန်အတွက် Session State Variables များ ကြေညာခြင်း ---
    # Input အကွက်တစ်ခုချင်းစီကို တိုက်ရိုက်ထိန်းချုပ်ရန် ဖြစ်ပါသည်
    if 'r_name_val' not in st.session_state: st.session_state.r_name_val = ""
    if 'r_nrc_val' not in st.session_state: st.session_state.r_nrc_val = ""
    if 'r_addr_val' not in st.session_state: st.session_state.r_addr_val = ""
    if 'r_ph_val' not in st.session_state: st.session_state.r_ph_val = ""
    if 'r_point_val' not in st.session_state: st.session_state.r_point_val = ""
    if 'r_remark_val' not in st.session_state: st.session_state.r_remark_val = ""
    if 's_name_val' not in st.session_state: st.session_state.s_name_val = ""
    if 's_id_val' not in st.session_state: st.session_state.s_id_val = ""
    if 's_country_val' not in st.session_state: st.session_state.s_country_val = "Thailand"
    if 'amount_val' not in st.session_state: st.session_state.amount_val = 0.0
    if 'mmk_rate_val' not in st.session_state: st.session_state.mmk_rate_val = 0.0
    if 'mmk_allow_val' not in st.session_state: st.session_state.mmk_allow_val = 0.0
    if 'usd_equiv_val' not in st.session_state: st.session_state.usd_equiv_val = 0.0
    if 'total_mmk_val' not in st.session_state: st.session_state.total_mmk_val = 0.0
    if 'show_slip' not in st.session_state: st.session_state.show_slip = False
    if 'slip_data' not in st.session_state: st.session_state.slip_data = {}

    # --- ၂။ နောက်ဆုံး Transaction No ကို Database မှ ဆွဲထုတ်ခြင်း ---
    try:
        last_trans = supabase.table("inward_transactions").select("transaction_no").order("created_at", desc=True).limit(1).execute()
        if last_trans.data:
            last_no = int(last_trans.data[0]['transaction_no'])
            new_no = f"{last_no + 1:04d}"
        else:
            new_no = "0001"
    except Exception:
        new_no = "0001"

    # --- ၃။ Slip ပြသရမည့် အခြေအနေ မဟုတ်ပါက Form ကို ပြသမည် ---
    if not st.session_state.show_slip:
        # --- Header Information ---
        h_col1, h_col2, h_col3 = st.columns(3, vertical_alignment="bottom")
        with h_col1:
            st.text_input("Date:", value=now_yangon.strftime("%Y-%m-%d %H:%M:%S"), disabled=True)
        with h_col2:
            branch = st.selectbox("Select Branch", ["Yangon Branch", "Mandalay Branch", "Nay Pyi Taw Branch"])
        with h_col3:
            trans_no = st.text_input("Transaction No:", value=new_no)

        # --- RECEIVER INFORMATION ---
        st.subheader("🔵 RECEIVER INFORMATION :")
        with st.container(border=True):
            r_col1, r_col2 = st.columns(2)
            r_name = r_col1.text_input("Receiver Name:", key="r_name_in", value=st.session_state.r_name_val)
            r_nrc = r_col2.text_input("Receiver NRC:", key="r_nrc_in", value=st.session_state.r_nrc_val)

            r_addr_col, r_ph_col, r_purp_col = st.columns([2, 1, 1])
            r_address = r_addr_col.text_input("Receiver Address:", key="r_addr_in", value=st.session_state.r_addr_val)
            r_phone = r_ph_col.text_input("Receiver Phone:", key="r_ph_in", value=st.session_state.r_ph_val)
            r_purpose = r_purp_col.selectbox("Purpose", ["Family Support", "Business", "Gift"])

            r_state_col, r_point_col = st.columns(2)
            r_state = r_state_col.selectbox("State & Division", ["Yangon", "Mandalay", "Shan", "Bago"])
            r_point = r_point_col.text_input("Withdraw Point:", key="r_point_in", value=st.session_state.r_point_val)
            r_remark = st.text_area("Remark for Withdraw Point:", key="r_remark_in", value=st.session_state.r_remark_val)

        # --- SENDER INFORMATION ---
        st.subheader("🔵 SENDER INFORMATION :")
        with st.container(border=True):
            s_name_col, s_id_col, s_country_col = st.columns([2, 2, 1])
            s_name = s_name_col.text_input("Sender Name:", key="s_name_in", value=st.session_state.s_name_val)
            s_id = s_id_col.text_input("NRC/Passport ID:", key="s_id_in", value=st.session_state.s_id_val)
            s_country = s_country_col.text_input("Country", value=st.session_state.s_country_val, key="s_country_in")

            s_cur_col, s_mmk_col, s_usd_col = st.columns(3)
            with s_cur_col:
                currency = st.selectbox("Currency", ["THB", "USD", "SGD"])
                amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="amount_in", value=st.session_state.amount_val)
            with s_mmk_col:
                mmk_rate = st.number_input("MMK Rate", min_value=0.0, format="%.2f", key="mmk_rate_in", value=st.session_state.mmk_rate_val)
                mmk_allowance = st.number_input("MMK Allowance", min_value=0.0, format="%.2f", key="mmk_allow_in", value=st.session_state.mmk_allow_val)
            with s_usd_col:
                usd_equiv = st.number_input("USD Equivalent", min_value=0.0, key="usd_equiv_in", value=st.session_state.usd_equiv_val)
                total_mmk_input = st.number_input("Total MMK", min_value=0.0, key="total_mmk_in", value=st.session_state.total_mmk_val)
                
            calc_total_mmk = (amount * mmk_rate) + mmk_allowance
            st.markdown(f"### Total MMK: **{calc_total_mmk:,.2f}**")

        # --- SAVE ACTION & BLACKLIST CHECK ---
        if st.button("💾 Save Inward Transaction", type="primary", use_container_width=True):
            if r_name and r_nrc:
                try:
                    check_bl = supabase.table("blacklist").select("name").eq("nrcno", r_nrc).execute()
                    if len(check_bl.data) > 0:
                        st.error(f"❌ Blacklisted User: {check_bl.data[0]['name']}")
                    else:
                        new_data = {
                            "branch": branch, "transaction_no": trans_no, "r_name": r_name, "r_nrc": r_nrc,
                            "r_address": r_address, "r_phone": r_phone, "r_purpose": r_purpose, "r_state": r_state,
                            "r_withdraw_point": r_point, "r_remark": r_remark, "s_name": s_name, "s_id": s_id,
                            "s_country": s_country, "currency": currency, "amount": float(amount), "mmk_rate": float(mmk_rate),
                            "mmk_allowance": float(mmk_allowance), "usd_equiv": float(usd_equiv) if usd_equiv else 0,
                            "total_mmk": float(calc_total_mmk)
                        }
                        response = supabase.table("inward_transactions").insert(new_data).execute()
                        if response.data:
                            # Slip ထဲမှာ ပြသရန်အတွက် ဒေတာများကို ခေတ္တသိမ်းဆည်းခြင်း
                            st.session_state.slip_data = new_data
                            st.session_state.slip_data['date_time'] = now_yangon.strftime('%Y-%m-%d %H:%M:%S')
                            st.session_state.show_slip = True
                            st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("⚠️ Receiver Name နှင့် NRC ကို ဖြည့်စွက်ပါ။")

    # =========================================================================
    # 📄 PAYOUT SLIP DISPLAY & PRINT MODE (Save နှိပ်ပြီးမှ သီးသန့်ပွင့်လာမည့်အပိုင်း)
    # =========================================================================
    else:
        sd = st.session_state.slip_data
        st.success("✅ Save Successfully")
        st.balloons()
        
        st.markdown("---")
        st.subheader("📄 International Remittance - Payout Slip")
        
        # ၁။ မျက်နှာပြင်ပေါ်တွင် ကတ်ပြားပုံစံ လှလှပပ ပြသခြင်း
        with st.container(border=True):
            st.markdown(f"### **Transaction No:** `{sd['transaction_no']}`")
            st.markdown(f"**Branch:** {sd['branch']} | **Date & Time:** {sd['date_time']}")
            st.divider()
            
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("#### 🔵 Receiver Details")
                st.markdown(f"**Name:** {sd['r_name']}")
                st.markdown(f"**NRC:** {sd['r_nrc']}")
                st.markdown(f"**Phone:** {sd['r_phone']}")
                st.markdown(f"**Address:** {sd['r_address']}, {sd['r_state']}")
                st.markdown(f"**Withdraw Point:** {sd['r_withdraw_point']}")
            with sc2:
                st.markdown("#### 🟢 Sender Details")
                st.markdown(f"**Name:** {sd['s_name']}")
                st.markdown(f"**ID/Passport:** {sd['s_id']}")
                st.markdown(f"**Country:** {sd['s_country']}")
                st.markdown(f"**Purpose:** {sd['r_purpose']}")
            st.divider()
            st.info(f"## **Total Payout Amount:** {sd['total_mmk']:,.2f} MMK")

        # ၂။ စာရွက်ဖြင့် Print ထုတ်ရန်အတွက် ကွန်ပျူတာ Printer စနစ်သို့ HTML/JS ဖြင့် လှမ်းချိတ်ခြင်း
        # ဤစနစ်သည် Print ဆွဲလိုက်လျှင် မလိုအပ်သော Sidebar များကို ဖျောက်ပြီး Slip ကိုပဲ သေသပ်စွာ ထုတ်ပေးပါမည်
        html_code = f"""
        <script>
        function printSlip() {{
            var printContents = document.getElementById('print-area').innerHTML;
            var originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload();
        }}
        </script>
        <div id="print-area" style="padding:20px; font-family:sans-serif; color:#000; background:#fff; border:1px solid #ccc; max-width:600px; margin:auto;">
            <h2 style="text-align:center; margin-bottom:5px;">PAYOUT SLIP (REMITTANCE)</h2>
            <p style="text-align:center; font-size:12px; margin-top:0;">Transaction No: <b>{sd['transaction_no']}</b></p>
            <hr>
            <p><b>Date:</b> {sd['date_time']} | <b>Branch:</b> {sd['branch']}</p>
            <table style="width:100%; border-collapse:collapse; margin-top:15px;">
                <tr>
                    <td style="width:50%; vertical-align:top; padding:5px; border:1px solid #ddd;">
                        <h4>[ RECEIVER INFO ]</h4>
                        <p>Name: {sd['r_name']}<br>NRC: {sd['r_nrc']}<br>Phone: {sd['r_phone']}<br>Point: {sd['r_withdraw_point']}</p>
                    </td>
                    <td style="width:50%; vertical-align:top; padding:5px; border:1px solid #ddd;">
                        <h4>[ SENDER INFO ]</h4>
                        <p>Name: {sd['s_name']}<br>ID/Pass: {sd['s_id']}<br>Country: {sd['s_country']}<br>Purpose: {sd['r_purpose']}</p>
                    </td>
                </tr>
            </table>
            <div style="margin-top:20px; padding:15px; background:#f4f4f4; text-align:center; border:1px solid #ccc;">
                <h3 style="margin:0;">TOTAL PAYOUT AMOUNT</h3>
                <h2 style="margin:5px 0 0 0; color:#d9534f;">{sd['total_mmk']:,.2f} MMK</h2>
            </div>
            <br><br>
            <table style="width:100%; text-align:center; margin-top:30px;">
                <tr>
                    <td>____________________<br>Staff Signature</td>
                    <td>____________________<br>Customer Signature</td>
                </tr>
            </table>
        </div>
        """
        
        # Print ထုတ်မည့် HTML ပုံစံကို Expander အနေဖြင့် အောက်တွင် ဖော်ပြပေးထားပါသည်
        with st.expander("🖨️ Preview Print Layout (A4/Receipt)", expanded=False):
            st.components.v1.html(html_code + "<br><button onclick='printSlip()' style='width:100%; padding:10px; background-color:#ff4b4b; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;'>🖨️ Click to Print Payout Slip</button>", height=520, scrolling=True)

        # ၃။ DONE ကို နှိပ်လိုက်ပါက Form Data အားလုံးကို အလိုအလျောက် Clear လုပ်ပြီး Form အသစ်သို့ ပြန်သွားခြင်း
        if st.button("🔄 Done & New Data Input", type="primary", use_container_width=True):
            # Session state value များကို အကုန်လုံး Reset အဖြူထည် ပြန်လုပ်ခြင်း
            st.session_state.r_name_val = ""
            st.session_state.r_nrc_val = ""
            st.session_state.r_addr_val = ""
            st.session_state.r_ph_val = ""
            st.session_state.r_point_val = ""
            st.session_state.r_remark_val = ""
            st.session_state.s_name_val = ""
            st.session_state.s_id_val = ""
            st.session_state.amount_val = 0.0
            st.session_state.mmk_rate_val = 0.0
            st.session_state.mmk_allow_val = 0.0
            st.session_state.usd_equiv_val = 0.0
            st.session_state.total_mmk_val = 0.0
            
            # Slip ပိတ်ပြီး မူရင်း Form ဆီ ပြန်သွားစေခြင်း
            st.session_state.show_slip = False
            st.session_state.slip_data = {}
            st.rerun()

# --- ⚙️ System Control Page Logic ---
elif page == "⚙️ System Control":
    st.title("⚙️ System Control & Setup")
    
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

    # --- (၃) User Setup ---
    with tab3:
        st.subheader("👤 User Management")
        
        with st.expander("➕ Add New User Account"):
            with st.form("user_new_form", clear_on_submit=True):
                u_id = st.text_input("User ID (Username)")
                u_pwd = st.text_input("Password", type="password")
                u_confirm = st.text_input("Confirm Password", type="password")
                u_remark = st.text_area("Remark (e.g. Admin, Staff, CCO)")
                
                if st.form_submit_button("Create User"):
                    if u_id and u_pwd:
                        if u_pwd == u_confirm:
                            try:
                                supabase.table("user_setup").insert({
                                    "user_id": u_id, 
                                    "password": u_pwd, 
                                    "remark": u_remark
                                }).execute()
                                st.success(f"✅ User '{u_id}' ကို အောင်မြင်စွာ တည်ဆောက်ပြီးပါပြီ။")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.error("❌ Password များ ကိုက်ညီမှု မရှိပါ။")
                    else:
                        st.warning("⚠️ ကျေးဇူးပြု၍ User ID နှင့် Password ကို ဖြည့်စွက်ပေးပါ။")

        st.divider()
        st.subheader("📋 Registered Users List")
        
        try:
            res_u = supabase.table("user_setup").select("*").execute()
            if res_u.data:
                df_u = pd.DataFrame(res_u.data)
                st.dataframe(df_u[['user_id', 'remark', 'created_at']], use_container_width=True)

                st.subheader("🛠️ Modify User Account")
                u_list = [u['user_id'] for u in res_u.data]
                target_uid = st.selectbox("Choose a User ID to modify:", options=["-- Select --"] + u_list)
                
                if target_uid != "-- Select --":
                    user_data = next(u for u in res_u.data if u['user_id'] == target_uid)
                    
                    with st.container(border=True):
                        st.markdown(f"**Modifying User:** `{target_uid}`")
                        up_uid = st.text_input("Update User ID", value=user_data['user_id'])
                        up_pwd = st.text_input("Update Password", value=user_data['password'], type="password")
                        up_remark = st.text_area("Update Remark", value=user_data['remark'] if user_data['remark'] else "")
                        
                        col_u1, col_u2 = st.columns(2)
                        
                        if col_u1.button("🆙 Update User Now", type="primary", use_container_width=True):
                            try:
                                supabase.table("user_setup").update({
                                    "user_id": up_uid, 
                                    "password": up_pwd, 
                                    "remark": up_remark
                                }).eq("id", user_data['id']).execute()
                                st.success("✅ အချက်အလက်များကို ပြင်ဆင်ပြီးပါပြီ။")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update Error: {e}")
                        
                        if col_u2.button("🗑️ Delete User Account", type="secondary", use_container_width=True):
                            try:
                                supabase.table("user_setup").delete().eq("id", user_data['id']).execute()
                                st.warning(f"🗑️ User '{target_uid}' ကို ဖျက်သိမ်းလိုက်ပါပြီ။")
                                st.rerun()
                            except Exception as e:
                                r_text = f"Delete Error: {e}"
                                st.error(r_text)
            else:
                st.info("ℹ️ မှတ်ပုံတင်ထားသော User မရှိသေးပါ။")
        except Exception as e:
            st.error(f"User Load Error: {e}")
