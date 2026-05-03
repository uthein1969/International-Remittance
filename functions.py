import streamlit as st
import pandas as pd
import time

# --- ၁။ Dashboard Page ---
def show_dashboard_page(supabase, now_yangon):
    st.title("📈 Transaction Dashboard")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🇲🇲 Myanmar Standard Time")
        mm_ptr = st.empty()
    with col2:
        # ရွေးချယ်ခဲ့သော နိုင်ငံအမည်ကို session state မှ ယူပြရန်
        country = st.session_state.get('sel_country', 'International')
        st.success(f"🌍 {country} Live Time")
        intl_ptr = st.empty()

    st.divider()

    # Inward Transactions Summing
    try:
        res = supabase.table("inward_transactions").select("amount, created_at").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Yangon')
            
            # Sum Calculations
            d_sum = df[df['created_at'].dt.date == now_yangon.date()]['amount'].sum()
            m_sum = df[df['created_at'].dt.month == now_yangon.month]['amount'].sum()
            y_sum = df[df['created_at'].dt.year == now_yangon.year]['amount'].sum()
        else:
            d_sum = m_sum = y_sum = 0
    except Exception:
        d_sum = m_sum = y_sum = 0

    st.subheader("📊 Inward Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Daily Inward", f"{d_sum:,.2f}")
    c2.metric("Monthly Inward", f"{m_sum:,.2f}")
    c3.metric("Yearly Inward", f"{y_sum:,.2f}")

    # အရေးကြီးသည်- Dashboard တွင် Blacklist နှင့် ပတ်သက်သော code လုံးဝ မပါရပါ
    return mm_ptr, intl_ptr

# --- ၂။ Blacklist Page ---
def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    
    # NRC Data Load
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

    # Add New Blacklist Record
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        name = st.text_input("Full Name (အမည်)", key="bl_name_input")
        
        st.write("🆔 NRC Number (New Format)")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        
        with c1:
            all_states = sorted(nrc_df['state_no'].unique().tolist(), key=lambda x: int(x) if str(x).isdigit() else 99) if not nrc_df.empty else ["-"]
            selected_state = st.selectbox("State No", all_states, key="bl_state_select")
        with c2:
            filtered_tsps = nrc_df[nrc_df['state_no'] == selected_state]['short_en'].unique().tolist() if not nrc_df.empty else []
            selected_tsp = st.selectbox("Township", sorted(filtered_tsps) if filtered_tsps else ["No Data"], key="bl_tsp_select")
        with c3:
            nrc_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"], key="bl_type_select")
        with c4:
            nrc_num = st.text_input("Number", max_chars=6, key="bl_num_input")

        reason = st.text_area("Reason for Blacklisting", key="bl_reason_input")
        
        if st.button("Add to Blacklist", type="primary", use_container_width=True):
            if name and nrc_num and selected_tsp != "No Data":
                full_nrc = f"{selected_state}/{selected_tsp}{nrc_type}{nrc_num}"
                try:
                    check_exists = supabase.table("blacklist").select("nrcno").eq("nrcno", full_nrc).execute()
                    if check_exists.data:
                        st.error(f"❌ '{full_nrc}' သည် ရှိပြီးသားဖြစ်သည်")
                    else:
                        supabase.table("blacklist").insert({
                            "name": name, "nrcno": full_nrc, "remark": reason
                        }).execute()
                        st.success("✅ Saved Successfully!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Save Error: {e}")
            else:
                st.warning("⚠️ အချက်အလက်များ ပြည့်စုံစွာ ဖြည့်ပေးပါ")

    st.divider()

    # Search & Manage Section
    st.subheader("🛠️ Search & Manage Blacklist")
    search_query = st.text_input("🔍 Search by Name or NRC Number", key="bl_search_input")
    
    try:
        query = supabase.table("blacklist").select("srno, name, nrcno, remark")
        if search_query:
            bl_res = query.or_(f"name.ilike.%{search_query}%,nrcno.ilike.%{search_query}%").execute()
        else:
            bl_res = query.order("srno", desc=True).limit(10).execute()
        
        if bl_res.data:
            df = pd.DataFrame(bl_res.data)
            for _, row in df.iterrows():
                with st.container():
                    col_info, col_edit, col_del = st.columns([6, 1, 1])
                    col_info.write(f"**{row['name']}** - `{row['nrcno']}`")
                    col_info.caption(f"Note: {row['remark']}")
                    
                    if col_edit.button("✏️", key=f"ed_{row['srno']}"):
                        edit_popup(supabase, row)
                    if col_del.button("🗑️", key=f"dl_{row['srno']}"):
                        delete_popup(supabase, row)
                    st.divider()
        else:
            st.info("ရှာဖွေမှုရလဒ် မရှိပါ။")
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")

# --- ၃။ Helper Dialogs ---

@st.dialog("ပြင်ဆင်ရန်")
def edit_popup(supabase, row):
    new_name = st.text_input("Name", value=row['name'], key="edit_name")
    new_rem = st.text_area("Remark", value=row['remark'], key="edit_remark")
    if st.button("Update", type="primary"):
        try:
            supabase.table("blacklist").update({"name": new_name, "remark": new_rem}).eq("srno", row['srno']).execute()
            st.success("Updated!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Update Error: {e}")

@st.dialog("ပယ်ဖျက်ရန်")
def delete_popup(supabase, row):
    st.warning(f"⚠️ **{row['name']}** ကို ဖျက်ရန် သေချာပါသလား?")
    if st.button("Confirm Delete", type="primary"):
        try:
            supabase.table("blacklist").delete().eq("srno", row['srno']).execute()
            st.success("Deleted!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Delete Error: {e}")    

# --- ၄။ Other Pages ---

def show_inward_page(supabase, current_time):
    st.header("🏦 Inward Transaction")
    # Inward Transaction code များ ဤနေရာတွင် ဆက်ရေးရန်

def show_system_control(supabase):
    st.header("⚙️ System Control")
    # System Control code များ ဤနေရာတွင် ဆက်ရေးရန်
