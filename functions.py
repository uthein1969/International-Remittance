import streamlit as st
import pandas as pd
import time

def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    
    # --- ၁။ Add New Section ---
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        try:
            nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
            nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        except:
            nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

        name = st.text_input("Full Name (အမည်)", key="bl_name_input")
        
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
        
        if st.button("Add to Blacklist", type="primary", use_container_width=True):
            if name and s_num:
                full_nrc = f"{s_state}/{s_tsp}{s_type}{s_num}"
                try:
                    supabase.table("blacklist").insert({"name": name, "nrcno": full_nrc, "remark": reason}).execute()
                    st.success("✅ Saved Successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    # --- ၂။ Search & Manage (ဇယားများ Dashboard တွင် မပေါ်စေရန် container သုံးခြင်း) ---
    st.subheader("🛠️ Search & Manage Blacklist")
    search = st.text_input("🔍 Search by Name or NRC", key="bl_search_box")
    
    # ဇယားများအတွက် သီးသန့် container
    list_container = st.container()
    
    try:
        query = supabase.table("blacklist").select("srno, name, nrcno, remark")
        if search:
            res = query.or_(f"name.ilike.%{search}%,nrcno.ilike.%{search}%").execute()
        else:
            res = query.order("srno", desc=True).limit(10).execute()
        
        if res.data:
            with list_container:
                for row in res.data:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([6, 1, 1])
                        col1.write(f"**{row['name']}** - `{row['nrcno']}`")
                        col1.caption(f"Remark: {row['remark']}")
                        
                        if col2.button("✏️", key=f"edit_{row['srno']}"):
                            edit_popup(supabase, row)
                        if col3.button("🗑️", key=f"del_{row['srno']}"):
                            delete_popup(supabase, row)
        else:
            list_container.info("No record found.")
    except Exception as e:
        st.error(f"Fetch Error: {e}")

@st.dialog("Edit Record")
def edit_popup(supabase, row):
    u_name = st.text_input("Name", value=row['name'])
    u_rem = st.text_area("Remark", value=row['remark'])
    if st.button("Update Record", type="primary"):
        supabase.table("blacklist").update({"name": u_name, "remark": u_rem}).eq("srno", row['srno']).execute()
        st.success("Updated!")
        time.sleep(1)
        st.rerun()

@st.dialog("Delete Record")
def delete_popup(supabase, row):
    st.warning(f"Delete **{row['name']}** from blacklist?")
    if st.button("Confirm Delete", type="primary"):
        supabase.table("blacklist").delete().eq("srno", row['srno']).execute()
        st.success("Deleted!")
        time.sleep(1)
        st.rerun()

# --- Placeholder Functions ---
def show_dashboard_page(supabase, now):
    st.header("📊 Transaction Dashboard")
    st.info(f"Last Updated: {now.strftime('%I:%M:%S %p')}")

def show_inward_page(supabase, now):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
