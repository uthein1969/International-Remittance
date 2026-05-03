import streamlit as st
import pandas as pd

def show_dashboard_page(supabase, now_yangon):
    st.title("📈 Transaction Dashboard")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🇲🇲 Myanmar Standard Time")
        mm_ptr = st.empty()
    with col2:
        # ရွေးချယ်ခဲ့သော နိုင်ငံအမည်ကို ခေါင်းစဉ်တွင်ပြရန်
        st.success(f"🌍 {st.session_state.get('sel_country', 'International')} Live Time")
        intl_ptr = st.empty()

    st.divider()

    # Inward Transactions Summing (အရင်အတိုင်း)
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

import streamlit as st
import pandas as pd
import time

def show_blacklist_page(supabase):
    st.title("📋 Blacklist Management")
    
    # --- ၁။ NRC Data Load ---
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

    # --- ၂။ Add New Blacklist Record ---
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        name = st.text_input("Full Name (အမည်)", key="name_box")
        
        st.write("🆔 NRC Number (New Format)")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        
        with c1:
            all_states = sorted(nrc_df['state_no'].unique().tolist(), key=lambda x: int(x) if str(x).isdigit() else 99) if not nrc_df.empty else ["-"]
            selected_state = st.selectbox("State No", all_states)
        with c2:
            filtered_tsps = nrc_df[nrc_df['state_no'] == selected_state]['short_en'].unique().tolist() if not nrc_df.empty else []
            selected_tsp = st.selectbox("Township", sorted(filtered_tsps) if filtered_tsps else ["No Data"])
        with c3:
            nrc_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"])
        with c4:
            nrc_num = st.text_input("Number", max_chars=6)

        reason = st.text_area("Reason for Blacklisting")
        
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

    # --- ၃။ Search & Manage Section ---
    st.subheader("🛠️ Search & Manage Blacklist")
    search_query = st.text_input("🔍 Search by Name or NRC Number")
    
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

# --- DIALOG FUNCTIONS (Function အပြင်ဘက်တွင် သီးခြားရှိရပါမည်) ---

@st.dialog("ပြင်ဆင်ရန်")
def edit_popup(supabase, row):
    new_name = st.text_input("Name", value=row['name'])
    new_rem = st.text_area("Remark", value=row['remark'])
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
            # Delete logic ကို ဤနေရာတွင် တိုက်ရိုက်ခေါ်ခြင်း
            supabase.table("blacklist").delete().eq("srno", row['srno']).execute()
            st.success("Deleted!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Delete Error: {e}")    

def show_inward_page(supabase, current_time):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
