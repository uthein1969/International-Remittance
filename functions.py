import pytz
from datetime import datetime
import streamlit as st
import pandas as pd

def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    
    # ၁။ အသစ်ထည့်သွင်းခြင်း
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        try:
            nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
            nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        except:
            nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

        name = st.text_input("Full Name", key="bl_name")
        st.write("🆔 NRC Number")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        with c1:
            states = sorted(nrc_df['state_no'].unique().tolist()) if not nrc_df.empty else ["-"]
            s_state = st.selectbox("State", states, key="bl_state")
        with c2:
            tsps = nrc_df[nrc_df['state_no'] == s_state]['short_en'].unique().tolist() if not nrc_df.empty else []
            s_tsp = st.selectbox("Township", sorted(tsps) if tsps else ["-"], key="bl_tsp")
        with c3:
            s_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"], key="bl_type")
        with c4:
            s_num = st.text_input("Number", max_chars=6, key="bl_num")
        
        reason = st.text_area("Reason", key="bl_reason")
        
        if st.button("Save to Blacklist", type="primary"):
            if name and s_num:
                full_nrc = f"{s_state}/{s_tsp}{s_type}{s_num}"
                supabase.table("blacklist").insert({"name": name, "nrcno": full_nrc, "remark": reason}).execute()
                st.success("✅ Saved!")
                time.sleep(1)
                st.rerun()

    st.divider()

    # ၂။ ရှာဖွေခြင်းနှင့် စီမံခြင်း (ဇယားကွက်များ)
    st.subheader("🛠️ Search & Manage Blacklist")
    search = st.text_input("🔍 Search Name/NRC", key="bl_search")
    
    # ဇယားများကို ဤ container ထဲမှာပဲ ကန့်သတ်ထားသည်
    results_area = st.container()
    
    try:
        query = supabase.table("blacklist").select("srno, name, nrcno, remark")
        if search:
            res = query.or_(f"name.ilike.%{search}%,nrcno.ilike.%{search}%").execute()
        else:
            res = query.order("srno", desc=True).limit(10).execute()
        
        if res.data:
            with results_area:
                for row in res.data:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([6, 1, 1])
                        col1.write(f"**{row['name']}** - `{row['nrcno']}`")
                        col1.caption(f"Note: {row['remark']}")
                        
                        if col2.button("✏️", key=f"edit_{row['srno']}"):
                            edit_popup(supabase, row)
                        if col3.button("🗑️", key=f"del_{row['srno']}"):
                            delete_popup(supabase, row)
        else:
            results_area.info("No records found.")
    except Exception as e:
        st.error(f"Error: {e}")

@st.dialog("ပြင်ဆင်ရန်")
def edit_popup(supabase, row):
    new_name = st.text_input("Name", value=row['name'])
    new_rem = st.text_area("Remark", value=row['remark'])
    if st.button("Update"):
        supabase.table("blacklist").update({"name": new_name, "remark": new_rem}).eq("srno", row['srno']).execute()
        st.success("Updated!")
        time.sleep(1)
        st.rerun()

@st.dialog("ပယ်ဖျက်ရန်")
def delete_popup(supabase, row):
    st.warning(f"Delete **{row['name']}**?")
    if st.button("Confirm Delete", type="primary"):
        supabase.table("blacklist").delete().eq("srno", row['srno']).execute()
        st.success("Deleted!")
        time.sleep(1)
        st.rerun()

def show_dashboard_page(supabase, user_info):
    # ၁။ User ရဲ့ နိုင်ငံအချက်အလက်ကို ယူပြီး Timezone သတ်မှတ်ခြင်း
    country = user_info.get('country', 'Thailand') 
    tz_dict = {
        "Thailand": "Asia/Bangkok",
        "Singapore": "Asia/Singapore",
        "Myanmar": "Asia/Yangon",
        "Malaysia": "Asia/Kuala_Lumpur"
    }
    
    selected_tz = tz_dict.get(country, "Asia/Bangkok")
    local_now = datetime.now(pytz.timezone(selected_tz))

    # ၂။ Dashboard Title နှင့် Live Time Display
    st.title(f"📊 {country} Branch Dashboard")
    st.info(f"📍 Location: {country} | 🕒 Current Live Time: {local_now.strftime('%I:%M:%S %p')} ({country} Time)")

    try:
        # --- Database မှ Transaction Data များ ဆွဲထုတ်ခြင်း ---
        # (Table အမည် 'inward_transactions' ဖြစ်ရပါမည်)
        res = supabase.table("inward_transactions").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            # created_at ကို datetime format သို့ပြောင်းခြင်း
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # ၃။ Daily, Monthly, Yearly Total များ တွက်ချက်ခြင်း
            today_total = df[df['created_at'].dt.date == local_now.date()]['amount'].sum()
            month_total = df[(df['created_at'].dt.month == local_now.month) & (df['created_at'].dt.year == local_now.year)]['amount'].sum()
            year_total = df[df['created_at'].dt.year == local_now.year]['amount'].sum()

            # --- Summary Metrics (Card) များဖြင့် ပြသခြင်း ---
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label="📅 Daily Total", value=f"{today_total:,.2f} MMK")
            with c2:
                st.metric(label="📅 Monthly Total", value=f"{month_total:,.2f} MMK")
            with c3:
                st.metric(label="📅 Yearly Total", value=f"{year_total:,.2f} MMK")

            st.divider()

            # --- Chart (ဇယား) များ ပြသခြင်း ---
            st.subheader("📈 Inward Transaction Trends")
            tab1, tab2 = st.tabs(["Monthly Overview", "Daily Detail"])
            
            with tab1:
                # Monthly Chart (လအလိုက် စုစုပေါင်း)
                m_chart = df.groupby(df['created_at'].dt.strftime('%b'))['amount'].sum()
                st.bar_chart(m_chart)
                
            with tab2:
                # Daily Chart (နေ့အလိုက် လိုင်းဇယား)
                d_chart = df.groupby(df['created_at'].dt.date)['amount'].sum()
                st.line_chart(d_chart)
        else:
            st.warning("⚠️ ပြသရန် Transaction Data မရှိသေးပါ။")

    except Exception as e:
        st.error(f"❌ Dashboard Error: {e}")
def show_inward_page(supabase, now):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
