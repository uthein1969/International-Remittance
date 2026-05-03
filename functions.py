import streamlit as st
import pandas as pd
import time

def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    
    # --- ၁။ Add New Section ---
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        # NRC Data Load
        try:
            nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
            nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        except:
            nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

        name = st.text_input("Full Name (အမည်)", key="bl_name")
        
        st.write("🆔 NRC Number")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        with c1:
            states = sorted(nrc_df['state_no'].unique().tolist()) if not nrc_df.empty else ["-"]
            s_state = st.selectbox("State", states)
        with c2:
            tsps = nrc_df[nrc_df['state_no'] == s_state]['short_en'].unique().tolist() if not nrc_df.empty else []
            s_tsp = st.selectbox("Township", sorted(tsps) if tsps else ["-"])
        with c3:
            s_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"])
        with c4:
            s_num = st.text_input("Number", max_chars=6)

        reason = st.text_area("Reason")
        
        if st.button("Add to Blacklist", type="primary"):
            if name and s_num:
                full_nrc = f"{s_state}/{s_tsp}{s_type}{s_num}"
                supabase.table("blacklist").insert({"name": name, "nrcno": full_nrc, "remark": reason}).execute()
                st.success("Saved!")
                time.sleep(1)
                st.rerun()

    st.divider()

    # --- ၂။ Search & Manage (ဒီအပိုင်းကို container နဲ့ ကန့်သတ်ထားပါတယ်) ---
    st.subheader("🛠️ Search & Manage Blacklist")
    search = st.text_input("🔍 Search by Name or NRC")
    
    # ဇယားကွက်များအတွက် သီးသန့်နေရာ
    list_area = st.container() 
    
    try:
        query = supabase.table("blacklist").select("srno, name, nrcno, remark")
        if search:
            res = query.or_(f"name.ilike.%{search}%,nrcno.ilike.%{search}%").execute()
        else:
            res = query.order("srno", desc=True).limit(10).execute()
        
        if res.data:
            with list_area:
                for row in res.data:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([6, 1, 1])
                        col1.write(f"**{row['name']}** - `{row['nrcno']}`")
                        col1.caption(f"Remark: {row['remark']}")
                        
                        # srno ကို သုံးပြီး Edit/Delete လုပ်ခြင်း
                        if col2.button("✏️", key=f"e_{row['srno']}"):
                            edit_popup(supabase, row)
                        if col3.button("🗑️", key=f"d_{row['srno']}"):
                            delete_popup(supabase, row)
        else:
            list_area.info("No data found.")
    except Exception as e:
        st.error(f"Error: {e}")

# --- Dialogs ---
@st.dialog("Edit Record")
def edit_popup(supabase, row):
    u_name = st.text_input("Name", value=row['name'])
    u_rem = st.text_area("Remark", value=row['remark'])
    if st.button("Update"):
        supabase.table("blacklist").update({"name": u_name, "remark": u_rem}).eq("srno", row['srno']).execute()
        st.success("Updated!")
        time.sleep(1)
        st.rerun()

@st.dialog("Delete Record")
def delete_popup(supabase, row):
    st.warning(f"Delete **{row['name']}**?")
    if st.button("Confirm Delete", type="primary"):
        supabase.table("blacklist").delete().eq("srno", row['srno']).execute()
        st.success("Deleted!")
        time.sleep(1)
        st.rerun()

# --- Other Function Stubs ---
def show_dashboard_page(supabase, now):
    st.header("📊 Transaction Dashboard")
    st.write(f"Current Time: {now.strftime('%H:%M:%S %p')}")
    # Dashboard logic များ ဤနေရာတွင် ဆက်ရေးနိုင်ပါသည်

def show_inward_page(supabase, now):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
