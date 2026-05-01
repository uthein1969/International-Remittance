import streamlit as st
import pandas as pd
import pytz
from datetime import datetime

# --- ၁။ Dashboard Page Function ---
def show_dashboard_page(supabase, now_yangon):
    st.title("📈 Transaction Dashboard")
    
    # Live Time ပြသရန် Placeholder (app.py မှ Loop ပတ်၍ update လုပ်မည်)
    time_placeholder = st.empty()
    
    try:
        # ဒေတာဆွဲထုတ်ခြင်း
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        
        if res.data:
            df_dash = pd.DataFrame(res.data)
            
            # Date Conversion (Yangon Time သို့ ပြောင်းလဲခြင်း)[cite: 1]
            df_dash['created_at'] = pd.to_datetime(df_dash['created_at']).dt.tz_convert('Asia/Yangon')
            
            # ရက်စွဲအလိုက် Filter လုပ်ရန် သတ်မှတ်ခြင်း[cite: 1]
            today = now_yangon.date()
            this_month = now_yangon.month
            this_year = now_yangon.year

            # ပမာဏများ ပေါင်းခြင်း[cite: 1]
            daily_sum = df_dash[df_dash['created_at'].dt.date == today]['amount'].sum()
            monthly_sum = df_dash[(df_dash['created_at'].dt.month == this_month) & 
                                  (df_dash['created_at'].dt.year == this_year)]['amount'].sum()
            yearly_sum = df_dash[df_dash['created_at'].dt.year == this_year]['amount'].sum()
        else:
            daily_sum = monthly_sum = yearly_sum = 0
            st.info("ℹ️ Database ထဲတွင် Transaction data မရှိသေးပါ။")[cite: 1]

    except Exception as e:
        st.error(f"❌ Dashboard Error: {e}")[cite: 1]
        daily_sum = monthly_sum = yearly_sum = 0

    # UI Display (ရောင်စုံ Card များ)[cite: 1]
    st.subheader("📅 Daily Transaction")
    d1, d2 = st.columns(2)
    d1.info(f"### {daily_sum:,.2f} \n 📉 Daily Inward")
    d2.info(f"### 0.00 \n 📉 Daily Outward")

    st.divider()

    st.subheader("📅 Monthly Transaction")
    m1, m2 = st.columns(2)
    m1.warning(f"### {monthly_sum:,.2f} \n 📈 Monthly Inward") 
    m2.warning(f"### 0.00 \n 📈 Monthly Outward")

    st.divider()

    st.subheader("📅 Yearly Transaction")
    y1, y2 = st.columns(2)
    y1.error(f"### {yearly_sum:,.2f} \n 📊 Yearly Inward")
    y2.error(f"### 0.00 \n 📊 Yearly Outward")

    return time_placeholder

# --- ၂။ Blacklist Info Function ---
def show_blacklist_page(supabase):
    st.title("📜 Blacklist Information")
    # Blacklist logic များ ဤနေရာတွင် ဆက်လက်ရေးသားနိုင်သည်[cite: 1]
    st.write("Blacklist management system is ready.")

# --- ၃။ Inward Transaction Function ---
def show_inward_page(supabase, now_yangon):
    st.title("🏦 Inward Transaction")
    # Inward Form logic များ ဤနေရာတွင် ဆက်လက်ရေးသားနိုင်သည်[cite: 1]
    st.write(f"Processing Inward for: {now_yangon.strftime('%Y-%m-%d')}")

# --- ၄။ System Control (Country/Branch/User Setup) ---
def show_system_control(supabase):
    st.title("⚙️ System Control")
    tab1, tab2, tab3 = st.tabs(["🌍 Country Setup", "🏢 Branch Setup", "👤 User Setup"])
    
    with tab1:
        st.write("Country Settings") # ကုဒ်ဟောင်းမှ logic များ ထည့်ရန်[cite: 1]
    with tab2:
        st.write("Branch Settings")
    with tab3:
        # User Setup Logic (ကုဒ်ဟောင်းအတိုင်း)[cite: 1]
        st.write("User Account Management")
