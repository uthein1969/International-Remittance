import streamlit as st
import pandas as pd

def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    # Blacklist logic များ ဤနေရာတွင် ထည့်ပါ
    search_q = st.text_input("Search Name/NRC", key="bl_search")
    if search_q:
        res = supabase.table("blacklist").select("*").or_(f"name.ilike.%{search_q}%,nrcno.ilike.%{search_q}%").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data))

def show_inward_page(supabase):
    st.title("🏦 Inward Transaction")
    # Inward Transaction logic များ ဤနေရာတွင် ထည့်ပါ
    with st.form("inward_form"):
        sender = st.text_input("Sender Name")
        receiver = st.text_input("Receiver Name")
        if st.form_submit_button("Save"):
            st.success("Saved!")
