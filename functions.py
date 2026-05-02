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
    
    # --- ၁။ NRC Data ကို Load လုပ်ခြင်း ---
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
        if not nrc_df.empty:
            nrc_df['state_no'] = nrc_df['state_no'].astype(str).str.strip()
            nrc_df['short_en'] = nrc_df['short_en'].astype(str).str.strip()
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

    # --- ၂။ Form Reset Logic (Session State) ---
    if 'name_input' not in st.session_state: st.session_state.name_input = ""
    if 'nrc_num_input' not in st.session_state: st.session_state.nrc_num_input = ""
    if 'remark_input' not in st.session_state: st.session_state.remark_input = ""

    # --- ၃။ Add New Blacklist Record ---
    with st.expander("➕ Add New Blacklist Record", expanded=False):
        name = st.text_input("Full Name (အမည်)", key="name_input")
        
        st.write("🆔 NRC Number (New Format)")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        
        with c1:
            all_states = sorted(nrc_df['state_no'].unique().tolist(), key=lambda x: int(x) if x.isdigit() else 99)
            selected_state = st.selectbox("State No", all_states, key="st_key")
        with c2:
            filtered_tsps = nrc_df[nrc_df['state_no'] == selected_state]['short_en'].unique().tolist()
            selected_tsp = st.selectbox("Township", sorted(filtered_tsps) if filtered_tsps else ["No Data"], key="tsp_key")
        with c3:
            nrc_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"], key="type_key")
        with c4:
            nrc_num = st.text_input("Number", max_chars=6, key="nrc_num_input")

        reason = st.text_area("Reason for Blacklisting", key="remark_input")
        
        if st.button("Add to Blacklist", type="primary", use_container_width=True):
            if name and nrc_num and selected_tsp != "No Data":
                full_nrc = f"{selected_state}/{selected_tsp}{nrc_type}{nrc_num}"
                
                try:
                    # Duplicate Check
                    check_exists = supabase.table("blacklist").select("nrcno").eq("nrcno", full_nrc).execute()
                    if check_exists.data:
                        st.error(f"❌ '{full_nrc}' သည် Database ထဲတွင် ရှိနှင့်ပြီးသားဖြစ်ပါသည်")
                    else:
                        supabase.table("blacklist").insert({
                            "name": name, "nrcno": full_nrc, "remark": reason
                        }).execute()
                        
                        st.success("✅ Saved Successfully!")
                        # Form Clear
                        st.session_state.name_input = ""
                        st.session_state.nrc_num_input = ""
                        st.session_state.remark_input = ""
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"Save Error: {e}")
            else:
                st.warning("⚠️ ကျေးဇူးပြု၍ အချက်အလက်များ ပြည့်စုံစွာ ဖြည့်စွက်ပေးပါ။")

    st.divider()

    # --- ၄။ Search & Edit/Delete Section ---
    st.subheader("🛠️ Search & Manage Blacklist")
    
    search_query = st.text_input("🔍 Search by Name or NRC Number", placeholder="အမည် (သို့) NRC ဖြင့် ရှာဖွေပါ...")
    
    try:
        # Database မှ data အားလုံးဆွဲထုတ်ခြင်း (Search query ရှိလျှင် filter လုပ်မည်)
        if search_query:
            bl_res = supabase.table("blacklist").select("*").or_(f"name.ilike.%{search_query}%,nrcno.ilike.%{search_query}%").execute()
        else:
            bl_res = supabase.table("blacklist").select("*").order("id", desc=True).limit(20).execute()
        
        if bl_res.data:
            df_display = pd.DataFrame(bl_res.data)
            
            # Table ပြသခြင်း
            for index, row in df_display.iterrows():
                with st.container():
                    col_info, col_edit, col_del = st.columns([6, 1, 1])
                    with col_info:
                        st.markdown(f"**Name:** {row['name']} | **NRC:** `{row['nrcno']}`")
                        st.caption(f"Reason: {row['remark']}")
                    
                    # Edit Functionality
                    with col_edit:
                        if st.button("✏️", key=f"edit_{row['id']}"):
                            edit_record(supabase, row)
                    
                    # Delete Functionality
                    with col_del:
                        if st.button("🗑️", key=f"del_{row['id']}"):
                            delete_record(supabase, row['id'], row['name'])
                    st.divider()
        else:
            st.info("ရှာဖွေမှုရလဒ် မရှိပါ။")
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")

# --- Edit Record Modal (Helper Function) ---
@st.dialog("Edit Blacklist Record")
def edit_record(supabase, row):
    new_name = st.text_input("Name", value=row['name'])
    new_remark = st.text_area("Remark", value=row['remark'])
    if st.button("Update Record"):
        try:
            supabase.table("blacklist").update({"name": new_name, "remark": new_remark}).eq("id", row['id']).execute()
            st.success("Updated!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Update Error: {e}")

# --- Delete Record Modal (Helper Function) ---
@st.dialog("Confirm Delete")
def delete_record(supabase, record_id, name):
    st.warning(f"⚠️ '{name}' ကို Blacklist မှ ပယ်ဖျက်ရန် သေချာပါသလား?")
    if st.button("Yes, Delete it"):
        try:
            supabase.table("blacklist").delete().eq("id", record_id).execute()
            st.success("Deleted!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Delete Error: {e}")

def show_inward_page(supabase, now_yangon):
    st.header("🏦 Inward Transaction")

def show_system_control(supabase):
    st.header("⚙️ System Control")
