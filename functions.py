import streamlit as st
import pandas as pd
import time

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

def show_dashboard_page(supabase, now):
    st.header("📊 Transaction Dashboard")
    st.info(f"Last Sync: {now.strftime('%I:%M:%S %p')}")

def show_inward_page(supabase, now):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
