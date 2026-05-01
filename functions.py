import streamlit as st
import pandas as pd
import pytz
from datetime import datetime

# --- ၁။ Dashboard Page Function ---
def show_dashboard_page(supabase, now_yangon):
    st.title("📈 Transaction Dashboard")
    
    # ရန်ကုန်အချိန် Live ပြရန် Placeholder
    st.subheader("🇲🇲 Myanmar Standard Time")
    mm_time_ptr = st.empty()
    st.divider()

    # နိုင်ငံတကာအချိန်များအတွက် Placeholder များ
    st.subheader("🌍 International Live Times")
    country_placeholders = {}
    
    try:
        # Country Setup မှ နိုင်ငံစာရင်းကို ယူသည်
        countries_res = supabase.table("country_setup").select("country_name, remark").execute()
        if countries_res.data:
            cols = st.columns(len(countries_res.data))
            for i, country in enumerate(countries_res.data):
                with cols[i]:
                    st.info(f"**{country['country_name']}**")
                    # Remark ထဲမှာ 'Asia/Bangkok' စသဖြင့် Timezone ID ရှိရမည်
                    country_placeholders[country['country_name']] = {
                        "ptr": st.empty(),
                        "tz": country['remark'] if country['remark'] else "UTC" 
                    }
    except Exception as e:
        st.error(f"Country Load Error: {e}")

    st.divider()

    # Inward Transaction Summing Logic
    try:
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        if res.data:
            df_dash = pd.DataFrame(res.data)
            df_dash['created_at'] = pd.to_datetime(df_dash['created_at']).dt.tz_convert('Asia/Yangon')
            
            today = now_yangon.date()
            this_month = now_yangon.month
            this_year = now_yangon.year

            daily_sum = df_dash[df_dash['created_at'].dt.date == today]['amount'].sum()
            monthly_sum = df_dash[(df_dash['created_at'].dt.month == this_month) & 
                                  (df_dash['created_at'].dt.year == this_year)]['amount'].sum()
            yearly_sum = df_dash[df_dash['created_at'].dt.year == this_year]['amount'].sum()
        else:
            daily_sum = monthly_sum = yearly_sum = 0
    except Exception as e:
        st.error(f"Summation Error: {e}")
        daily_sum = monthly_sum = yearly_sum = 0

    # UI Display Cards[cite: 1]
    st.subheader("📊 Inward Summary")
    c1, c2, c3 = st.columns(3)
    c1.info(f"**Daily Inward**\n### {daily_sum:,.2f}")
    c2.warning(f"**Monthly Inward**\n### {monthly_sum:,.2f}")
    c3.error(f"**Yearly Inward**\n### {yearly_sum:,.2f}")

    # အရေးကြီးသည်- အပေါ်က variable နှစ်ခုကို app.py သို့ ပြန်ပေးခြင်း
    return mm_time_ptr, country_placeholders

# --- ၂။ Blacklist Info Function (အပြည့်အစုံ) ---[cite: 1]
def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management System")
    # အရင် backup file ထဲက logic များ ပြန်ထည့်ပါ
    st.info("Blacklist Section Ready")

# --- ၃။ Inward Transaction Function (အပြည့်အစုံ) ---[cite: 1]
def show_inward_page(supabase, now_yangon):
    st.header("🏦 Inward Transaction Management")
    # အရင် backup file ထဲက logic များ ပြန်ထည့်ပါ
    st.info("Inward Transaction Section Ready")

# --- ၄။ System Control (အပြည့်အစုံ) ---[cite: 1]
def show_system_control(supabase):
    st.title("⚙️ System Control & Setup")
    tab1, tab2, tab3 = st.tabs(["🌍 Country Setup", "🏢 Branch Setup", "👤 User Setup"])
    # အရင် backup file ထဲက logic များ ပြန်ထည့်ပါ
