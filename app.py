import pandas as pd
import streamlit as st
import pytz
from supabase import create_client, Client
from datetime import datetime

# --- ၁။ Setup & Connections ---
yangon_tz = pytz.timezone('Asia/Yangon')
now_yangon = datetime.now(yangon_tz)

def safe_float(val):
    try:
        if val is None or str(val).strip() == "":
            return 0.0
        return float(val)
    except (ValueError, TypeError):
        return 0.0

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

# --- ၂။ Blacklist Page Function ---
def show_blacklist_page():
    st.title("📋 Blacklist Management")
    
    # NRC Data Load
    try:
        nrc_res = supabase.table("myanmar_nrc_data").select("state_no, short_en").execute()
        nrc_df = pd.DataFrame(nrc_res.data) if nrc_res.data else pd.DataFrame(columns=["state_no", "short_en"])
    except Exception as e:
        st.error(f"NRC Data Load Error: {e}")
        nrc_df = pd.DataFrame(columns=["state_no", "short_en"])

    # Add New Section
    with st.expander("➕ Add New Blacklist Record", expanded=True):
        name = st.text_input("Full Name (အမည်)")
        st.write("🆔 NRC Number (New Format)")
        c1, c2, c3, c4 = st.columns([1, 1.5, 1, 2])
        
        with c1:
            all_states = sorted(nrc_df['state_no'].unique().tolist(), key=lambda x: int(x) if str(x).isdigit() else 99)
            s_state = st.selectbox("State No", all_states)
        with c2:
            tsps = nrc_df[nrc_df['state_no'] == s_state]['short_en'].unique().tolist()
            s_tsp = st.selectbox("Township", sorted(tsps) if tsps else ["No Data"])
        with c3:
            n_type = st.selectbox("Type", ["(N)", "(E)", "(P)", "(A)"])
        with c4:
            n_num = st.text_input("Number", max_chars=6)

        reason = st.text_area("Reason for Blacklisting")
        
        if st.button("Add to Blacklist", type="primary", use_container_width=True):
            if name and n_num:
                full_nrc = f"{s_state}/{s_tsp}{n_type}{n_num}"
                try:
                    supabase.table("blacklist").insert({"name": name, "nrcno": full_nrc, "remark": reason}).execute()
                    st.success("✅ Saved Successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Save Error: {e}")

    st.divider()

    # Search & Edit/Delete Section
    st.subheader("🔍 Search & Edit/Delete")
    search_q = st.text_input("Search by Name or NRC")

    if search_q:
        try:
            res = supabase.table("blacklist").select("*").or_(f"name.ilike.%{search_q}%,nrcno.ilike.%{search_q}%").execute()
            if res.data:
                options = {f"{r['name']} ({r['nrcno']})": r for r in res.data}
                selected_key = st.selectbox("Select Record to modify", list(options.keys()))
                if selected_key:
                    target = options[selected_key]
                    with st.container(border=True):
                        col_e1, col_e2 = st.columns(2)
                        u_name = col_e1.text_input("Edit Name", value=target['name'])
                        u_nrc = col_e1.text_input("Edit NRC", value=target['nrcno'])
                        u_reason = col_e2.text_area("Edit Reason", value=target['remark'] or "", height=115)
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("🔄 Update Record", type="secondary", use_container_width=True):
                                supabase.table("blacklist").update({"name": u_name, "nrcno": u_nrc, "remark": u_reason}).eq("id", target['id']).execute()
                                st.success("Updated!"); st.rerun()
                        with b2:
                            if st.button("🗑️ Delete Record", type="primary", use_container_width=True):
                                supabase.table("blacklist").delete().eq("id", target['id']).execute()
                                st.warning("Deleted!"); st.rerun()
            else:
                st.info("No records found.")
        except Exception as e:
            st.error(f"Search Error: {e}")

# --- ၃။ Inward Transaction Function ---
def show_inward_page():
    st.header("🏦 Inward Transaction Management")
    
    with st.expander("➕ New Inward Transaction", expanded=True):
        with st.form("inward_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            s_name = col1.text_input("Sender Name")
            r_name = col2.text_input("Receiver Name")
            amt = col1.number_input("Amount (SGD)", min_value=0.0)
            meth = col2.selectbox("Method", ["Kpay", "Wave", "Bank Transfer"])
            remark = st.text_area("Remark")
            
            if st.form_submit_button("💾 Save Transaction", use_container_width=True):
                if s_name and r_name and amt > 0:
                    try:
                        supabase.table("inward_transactions").insert({
                            "sender": s_name, "receiver": r_name, "amount": amt, 
                            "method": meth, "remark": remark, "status": "Pending"
                        }).execute()
                        st.success("✅ Transaction Saved!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- ၄။ User Setup Function ---
def show_user_setup_page():
    st.header("⚙️ User Management System")
    try:
        res_u = supabase.table("user_setup").select("*").execute()
        if res_u.data:
            st.dataframe(pd.DataFrame(res_u.data)[["user_id", "remark"]], use_container_width=True)
            # Add/Edit User Logic များ ဤနေရာတွင် ထည့်သွင်းနိုင်သည်
    except Exception as e:
        st.error(f"User Load Error: {e}")

# --- ၅။ Main App Logic (Routing) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Admin Login System")
    
    # Login Form ကို အလယ်မှာထားခြင်း
    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        with st.form("login_form"):
            u_id = st.text_input("User ID")
            u_pw = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
        if submit_btn:
            try:
                # ၁။ Database ကို စစ်ဆေးခြင်း (try ရဲ့ အထဲမှာ ရှိရပါမယ်)
                res = supabase.table("user_setup").select("*").eq("user_id", input_user).eq("password", input_pass).execute()
                
                # ၂။ ရလဒ် ရှိမရှိ စစ်ဆေးခြင်း (ဒီစာကြောင်းက try ရဲ့ အထဲကို ၄ စပေ့စ် ထပ်ဝင်ရပါမယ်)
                if res.data and len(res.data) > 0:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = input_user
                    st.success("🎉 Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ User ID သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
                    
            except Exception as e:
                # ၃။ Error တက်လျှင် ပြသခြင်း (except က try နဲ့ တန်းနေရပါမယ်)
                st.error(f"Login Error: {e}")
else:
    # Login ဝင်ပြီးသားဆိုလျှင် ပြသရမည့် Sidebar နှင့် Page များ
    st.sidebar.success(f"🔓 Logged in as: {st.session_state.get('user_id', 'Admin')}")
    
    page = st.sidebar.radio("Main Menu", ["📋 Blacklist Info", "🏦 Inward Transaction", "⚙️ User Setup"])
    
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # Page Routing
    if page == "📋 Blacklist Info":
        show_blacklist_page()
    elif page == "🏦 Inward Transaction":
        show_inward_page()
    elif page == "⚙️ User Setup":
        show_user_setup_page()
