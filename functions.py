import pytz
from datetime import datetime
import streamlit as st
import pandas as pd

def show_dashboard_page(supabase, user_info):
    # ၁။ နိုင်ငံအလိုက် Timezone သတ်မှတ်ခြင်း
    country = user_info.get('country', 'Thailand') if user_info else 'Thailand'
    tz_dict = {
        "Thailand": "Asia/Bangkok",
        "Singapore": "Asia/Singapore",
        "Myanmar": "Asia/Yangon",
        "Malaysia": "Asia/Kuala_Lumpur"
    }
    selected_tz = tz_dict.get(country, "Asia/Bangkok")
    local_now = datetime.now(pytz.timezone(selected_tz))

    # ၂။ Title နှင့် Live Time ပြသခြင်း
    st.title("📊 Transaction Dashboard")
    st.info(f"🕒 Live Time: {local_now.strftime('%I:%M:%S %p')} ({country} Time)")

    try:
        # --- Database မှ Data ဆွဲထုတ်ခြင်း ---
        res = supabase.table("inward_transactions").select("*").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # ၃။ Daily, Monthly, Yearly Total တွက်ချက်ခြင်း
            today_total = df[df['created_at'].dt.date == local_now.date()]['amount'].sum()
            month_total = df[(df['created_at'].dt.month == local_now.month) & (df['created_at'].dt.year == local_now.year)]['amount'].sum()
            year_total = df[df['created_at'].dt.year == local_now.year]['amount'].sum()

            # Metric Cards များ
            c1, c2, c3 = st.columns(3)
            c1.metric("Daily Amount", f"{today_total:,.2f} MMK")
            c2.metric("Monthly Amount", f"{month_total:,.2f} MMK")
            c3.metric("Yearly Amount", f"{year_total:,.2f} MMK")

            st.divider()
            
            # Trends Chart များ
            st.subheader("📈 Inward Transaction Trends")
            m_chart = df.groupby(df['created_at'].dt.strftime('%b'))['amount'].sum()
            st.bar_chart(m_chart)
            
        else:
            st.warning("⚠️ ပြသရန် Transaction Data မရှိသေးပါ။")
    except Exception as e:
        st.error(f"Dashboard Error: {e}")
