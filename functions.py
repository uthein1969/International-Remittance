import streamlit as st
import pandas as pd

def show_dashboard_page(supabase, now_yangon):
    st.title("📈 Transaction Dashboard")
    
    # ရွေးချယ်ခဲ့သော နိုင်ငံနှင့် မြန်မာအချိန်ပြရန် Placeholder များ
    col1, col2 = st.columns(2)
    with col1:
        st.info("🇲🇲 Myanmar Time")
        mm_ptr = st.empty()
    with col2:
        st.success(f"🌍 {st.session_state.get('sel_country')} Time")
        intl_ptr = st.empty()

    st.divider()

    # Inward Transaction Calculation
    try:
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Yangon')
            d_sum = df[df['created_at'].dt.date == now_yangon.date()]['amount'].sum()
            m_sum = df[df['created_at'].dt.month == now_yangon.month]['amount'].sum()
            y_sum = df[df['created_at'].dt.year == now_yangon.year]['amount'].sum()
        else:
            d_sum = m_sum = y_sum = 0
    except:
        d_sum = m_sum = y_sum = 0

    st.subheader("📊 Inward Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Daily Inward", f"{d_sum:,.2f}")
    c2.metric("Monthly Inward", f"{m_sum:,.2f}")
    c3.metric("Yearly Inward", f"{y_sum:,.2f}")

    return mm_ptr, intl_ptr

def show_blacklist_page(supabase):
    st.header("📜 Blacklist Management")
    st.write("Manage your blacklist data here.")

def show_inward_page(supabase, now_yangon):
    st.header("🏦 Inward Transactions")
    st.write(f"Date: {now_yangon.strftime('%Y-%m-%d')}")

def show_system_control(supabase):
    st.header("⚙️ System Control")
    st.tabs(["Country Setup", "Branch Setup", "User Setup"])
