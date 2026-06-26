import streamlit as st
import pandas as pd
import pytz
from datetime import datetime
from supabase import create_client

# ================= CONFIG =================
st.set_page_config(page_title="International Remittance", layout="wide")

# ================= SUPABASE =================
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ================= TIME =================
yangon = pytz.timezone("Asia/Yangon")
now_yangon = datetime.now(yangon)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = "user"  # Default role သတ်မှတ်ချက်

# ================= LOGIN =================
def login_page():
    st.title("🔐 Admin Login")

    user = st.text_input("User ID")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if supabase is None:
            st.error("Supabase not connected")
            return

        try:
            # Database မှ userid, password နှင့်အတူ role ကော်လံကိုပါ ဆွဲဖတ်သည်
            res = supabase.table("user_setup").select("*").execute()

            for u in res.data or []:
                if u["user_id"] == user and u["password"] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    # 🎯 ဝန်ထမ်း၏ Role ကို စနစ်မှတ်ဉာဏ်ထဲသို့ ထည့်သွင်းမှတ်သားခြင်း
                    st.session_state.user_role = u.get("role", "user").lower().strip()
                    st.success(f"Welcome {user} ({st.session_state.user_role.upper()})")
                    st.rerun()
                    return

            st.error("Invalid credentials")

        except Exception as e:
            st.error(f"DB Error: {e}")

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Transaction Dashboard")
    st.info(f"👤 User: **{st.session_state.username}** | Role: **{st.session_state.user_role.upper()}**")

    if supabase is None:
        st.error("Supabase not connected")
        return

    try:
        # နောက်ဆုံးထည့်ထားတာ အပေါ်ဆုံးပေါ်အောင် စီပြီး ဆွဲထုတ်ပါသည်
        res = supabase.table("inward_transactions").select("*").order("created_at", desc=True).execute()
        data = res.data or []

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("No transactions found")
            return

        # ================= DATE CONVERT =================
        df["created_at_dt"] = pd.to_datetime(df["created_at"])
        df["Date"] = df["created_at_dt"].dt.date
        df["Month"] = df["created_at_dt"].dt.to_period("M")
        df["Year"] = df["created_at_dt"].dt.year

        # 🎯 ဇယားတွင် ပေါ်စေချင်သော ကော်လံများစာရင်း (ဒီထဲမှာ 'id' ကို ချန်လှပ်ထားခဲ့ပါသည်)
        display_cols = [
            "transaction_no", "branch", "r_name", "r_nrc", "r_phone", 
            "r_address", "r_state", "r_withdraw_point", "s_name", 
            "s_id", "s_country", "currency", "amount", "mmk_rate", 
            "mmk_allowance", "total_mmk", "created_at"
        ]

        # ================= FILTER TABS =================
        tab1, tab2, tab3 = st.tabs(["📅 Daily", "📆 Monthly", "📊 Yearly"])

        # ================= DAILY =================
        with tab1:
            st.subheader("📅 Daily Report")
            selected_date = st.date_input("Select Date")
            daily_df = df[df["Date"] == selected_date]
            st.metric("Transactions", len(daily_df))
            st.metric("Total MMK", f"{daily_df['total_mmk'].sum():,.2f}")

            # 🎯 ADMIN အတွက် Checkbox စနစ်
            if st.session_state.user_role == "admin":
                st.caption("💡 select by Checkbox ")
                # display_cols သုံးထား၍ 'id' ကို Hide ပေးထားသော်လည်း နောက်ကွယ်တွင် target_id ကို ယူနိုင်ရန် ၎င်း df ကို သုံးပါသည်
                event = st.dataframe(daily_df[display_cols], use_container_width=True, selection_mode="single-row", on_select="rerun")
                selected_rows = event.selection.rows
            else:
                st.dataframe(daily_df[display_cols], use_container_width=True)
                selected_rows = []

        # ================= MONTHLY =================
        with tab2:
            st.subheader("📆 Monthly Report")
            month_list = sorted(df["Month"].astype(str).unique())
            selected_month = st.selectbox("Select Month", month_list)
            monthly_df = df[df["Month"].astype(str) == selected_month]
            st.metric("Transactions", len(monthly_df))
            st.metric("Total MMK", f"{monthly_df['total_mmk'].sum():,.2f}")
            # 'id' ကော်လံကို ကွက်တိ ဖယ်ထုတ်ပြသခြင်း
            st.dataframe(monthly_df[display_cols], use_container_width=True)

        # ================= YEARLY =================
        with tab3:
            st.subheader("📊 Yearly Report")
            year_list = sorted(df["Year"].unique())
            selected_year = st.selectbox("Select Year", year_list)
            yearly_df = df[df["Year"] == selected_year]
            st.metric("Transactions", len(yearly_df))
            st.metric("Total MMK", f"{yearly_df['total_mmk'].sum():,.2f}")
            # 'id' ကော်လံကို ကွက်တိ ဖယ်ထုတ်ပြသခြင်း
            st.dataframe(yearly_df[display_cols], use_container_width=True)

        # ================= ADMIN INWARD ENTRY FORM FOR EDIT & DELETE =================
        if st.session_state.user_role == "admin" and len(selected_rows) > 0:
            st.divider()
            
            # ရွေးချယ်လိုက်သော အတန်း၏ မူရင်းဒေတာများကို ဆွဲထုတ်ခြင်း
            row_idx = selected_rows[0]
            target_data = daily_df.iloc[row_idx]
            target_id = target_data["id"] # 💡 နောက်ကွယ်တွင် id ကို သုံး၍ Update/Delete လုပ်ပါမည်
            target_no = target_data["transaction_no"]

            st.subheader(f"🛠️ Admin Entry Form (Editing Transaction No: {target_no})")
            
            # မူရင်း ငွေလွှဲ Form ပုံစံအတိုင်း Layout ဖန်တီးခြင်း
            with st.form("admin_edit_entry_form"):
                # Branch Selectbox (မူရင်းတန်ဖိုးအတိုင်း ရွေးထားပေးခြင်း)
                branches = ["Yangon", "Mandalay", "NPT"]
                edit_branch = st.selectbox("Branch", branches, index=branches.index(target_data["branch"]) if target_data["branch"] in branches else 0)

                st.markdown("#### 📥 Receiver Details")
                edit_r_name = st.text_input("Name", value=str(target_data["r_name"]))
                edit_r_nrc = st.text_input("NRC", value=str(target_data["r_nrc"]))
                edit_r_phone = st.text_input("Phone", value=str(target_data["r_phone"]))
                edit_r_address = st.text_input("Address", value=str(target_data["r_address"]))
                edit_r_state = st.text_input("State", value=str(target_data["r_state"]))
                edit_point = st.text_input("Withdraw Point", value=str(target_data["r_withdraw_point"]))

                st.markdown("#### 📤 Sender Details")
                edit_s_name = st.text_input("Sender Name", value=str(target_data["s_name"]))
                edit_s_id = st.text_input("ID", value=str(target_data["s_id"]))
                edit_s_country = st.text_input("Country", value=str(target_data["s_country"]))

                st.markdown("#### 💰 Financial Details")
                currencies = ["THB", "USD", "SGD"]
                edit_currency = st.selectbox("Currency", currencies, index=currencies.index(target_data["currency"]) if target_data["currency"] in currencies else 0)
                
                edit_amount = st.number_input("Amount", value=float(target_data["amount"]), min_value=0.0)
                edit_rate = st.number_input("MMK Rate", value=float(target_data["mmk_rate"]), min_value=0.0)
                edit_allow = st.number_input("MMK Allowance", value=float(target_data["mmk_allowance"]), min_value=0.0)

                # ကိန်းဂဏန်းတွက်ချက်မှုအသစ်
                new_total = (edit_amount * edit_rate) + edit_allow
                st.markdown(f"### 💰 New Calculated Total: {new_total:,.2f} MMK")

                # ခလုတ်များ
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit_edit = st.form_submit_button("💾 Save Changes", type="secondary")
                with col_btn2:
                    submit_delete = st.form_submit_button("🗑️ Delete This Transaction", type="secondary")

            # --- ပြင်ဆင်ချက်ကို ဒေတာဘေ့စ်ထဲ သိမ်းဆည်းခြင်း ---
            if submit_edit:
                try:
                    supabase.table("inward_transactions").update({
                        "branch": edit_branch,
                        "r_name": edit_r_name,
                        "r_nrc": edit_r_nrc,
                        "r_phone": edit_r_phone,
                        "r_address": edit_r_address,
                        "r_state": edit_r_state,
                        "r_withdraw_point": edit_point,
                        "s_name": edit_s_name,
                        "s_id": edit_s_id,
                        "s_country": edit_s_country,
                        "currency": edit_currency,
                        "amount": edit_amount,
                        "mmk_rate": edit_rate,
                        "mmk_allowance": edit_allow,
                        "total_mmk": new_total
                    }).eq("id", target_id).execute()
                    
                    st.success(f"🎉 Transaction No: {target_no} updated successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update Entry Error: {e}")

            # --- ဒေတာကို အပြီးဖျက်ပစ်ခြင်း ---
            if submit_delete:
                try:
                    supabase.table("inward_transactions").delete().eq("id", target_id).execute()
                    st.success(f"🚀 Transaction No: {target_no} deleted successfully")
                    st.rerun()
                except Exception as e:
                    st.error(f"Delete Entry Error: {e}")

        # ================= SUMMARY CARDS =================
        st.divider()
        st.subheader("📌 Overall Summary")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Transactions", len(df))
        with c2: st.metric("Total MMK Volume", f"{df['total_mmk'].sum():,.2f}")
        with c3: st.metric("Avg Transaction", f"{df['total_mmk'].mean():,.2f}")

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

# ================= Search_Transaction =================
def search_transactions():
    st.title("🔍 Search Transactions")

    if supabase is None:
        st.error("Supabase not connected")
        st.stop()

    # FILTER UI ALWAYS SHOW
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Start Date")

    with col2:
        end_date = st.date_input("End Date")

    with col3:
        search_btn = st.button("Search")

    # DEFAULT
    filtered_df = pd.DataFrame()

    try:
        res = supabase.table("inward_transactions").select("*").execute()
        data = res.data or []

        if len(data) > 0:
            df = pd.DataFrame(data)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["Date"] = df["created_at"].dt.date

            if search_btn:
                df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

            filtered_df = df

    except Exception as e:
        st.error(f"Search Error: {e}")

    # ALWAYS SHOW RESULT AREA
    st.subheader("📊 Results")

    if not filtered_df.empty:
        st.metric("Total Transactions", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "transactions.csv", "text/csv")
    else:
        st.info("No data found / no search result")

# ================= INWARD =================
def inward():
    st.title("🏦 Inward Transaction")
    st.info(f"🕒 {now_yangon.strftime('%d-%m-%Y %H:%M:%S')}")

    # 🎯 SECURITY CHECK: ရိုးရိုး user ဖြစ်ပါက ဝင်ခွင့်မပြုပါ (Only View)
    if st.session_state.user_role == "user":
        st.warning("⚠️ စနစ်လုံခြုံရေးအရ သင့်တွင် ငွေလွှဲအချက်အလက်သစ်များ ထည့်သွင်းခွင့် (Permission) မရှိပါ။ ဒေတာများကို Dashboard နှင့် Search တွင်သာ ကြည့်ရှုနိုင်ပါသည်။")
        return

    if supabase is None:
        st.error("No DB connection")
        return

    # AUTO NO
    try:
        last = supabase.table("inward_transactions") \
            .select("transaction_no") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        new_no = "0001"
        if last.data:
            new_no = str(int(last.data[0]["transaction_no"]) + 1).zfill(4)

    except:
        new_no = "0001"

    with st.form("inward_form"):
        branch = st.selectbox("Branch", ["Yangon", "Mandalay", "NPT"])

        st.subheader("Receiver")
        r_name = st.text_input("Name")
        r_nrc = st.text_input("NRC")
        r_phone = st.text_input("Phone")
        r_address = st.text_input("Address")
        r_state = st.text_input("State")
        r_point = st.text_input("Withdraw Point")

        st.subheader("Sender")
        s_name = st.text_input("Sender Name")
        s_id = st.text_input("ID")
        s_country = st.text_input("Country")

        currency = st.selectbox("Currency", ["THB", "USD", "SGD"])
        amount = st.number_input("Amount", 0.0)
        rate = st.number_input("MMK Rate", 0.0)
        allow = st.number_input("MMK Allowance", 0.0)

        total = (amount * rate) + allow

        st.markdown(f"### 💰 Total: {total:,.2f}")

        submitted = st.form_submit_button("Save")

    if submitted:
        try:
            check = supabase.table("blacklist").select("*").eq("nrcno", r_nrc).execute()

            if check.data:
                st.error("❌ BLACKLISTED")
                return

            supabase.table("inward_transactions").insert({
                "transaction_no": new_no,
                "branch": branch,
                "r_name": r_name,
                "r_nrc": r_nrc,
                "r_phone": r_phone,
                "r_address": r_address,
                "r_state": r_state,
                "r_withdraw_point": r_point,
                "s_name": s_name,
                "s_id": s_id,
                "s_country": s_country,
                "currency": currency,
                "amount": amount,
                "mmk_rate": rate,
                "mmk_allowance": allow,
                "total_mmk": total,
                "created_at": now_yangon.strftime("%d%m%Y%H%M%S")
            }).execute()

            st.success("Saved Successfully")
            st.rerun()

        except Exception as e:
            st.error(f"Save Error: {e}")

# ================= LOGIN GATE =================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= AFTER LOGIN (ROLE-BASED MENU) =================
# Role အလိုက် ဘေးဘား Menu များကို စိစစ်ခွဲခြားပြသခြင်း
menu_options = ["📊 Dashboard", "🔍 Search"]

# super သို့မဟုတ် admin ဖြစ်မှသာ Inward နှင့် Blacklist မီနူးများ ပြသမည်
if st.session_state.user_role in ["super", "admin"]:
    menu_options.append("🏦 Inward")
    menu_options.append("📋 Blacklist")

# admin သီးသန့်သာ System setting ကို မြင်တွေ့ခွင့်ရှိမည်
if st.session_state.user_role == "admin":
    menu_options.append("⚙️ System")

menu = st.sidebar.radio("📌 Menu", menu_options)

# Logout ခလုတ်
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_role = "user"
    st.rerun()

# ================= ROUTER =================
if menu == "📊 Dashboard":
    dashboard()

elif menu == "🔍 Search":
    if "search_transactions" in globals():
        search_transactions()
    else:
        st.error("Search module not loaded")

elif menu == "🏦 Inward":
    inward()

elif menu == "📋 Blacklist":
    st.title("📋 Blacklist Management")
    st.write(f"Logged in as: {st.session_state.username} ({st.session_state.user_role})")
    # TODO: Blacklist management UI ကို ဤနေရာတွင် ထည့်သွင်းနိုင်သည်

elif menu == "⚙️ System":
    st.title("⚙️ System Control (Admin Only)")
    st.info(f"👤 Admin အကောင့်: **{st.session_state.username}** အဖြစ် ဝင်ရောက်ထားပါသည်။ ဝန်ထမ်းအသစ်များကို ဤနေရာတွင် စနစ်တကျ စာရင်းသွင်းနိုင်ပါသည်။")

    if supabase is None:
        st.error("Supabase not connected")
    else:
        # ================= ADD NEW USER FORM =================
        st.subheader("➕ Add New System User")
        
        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_userid = st.text_input("User ID (ဝန်ထမ်းအကောင့်အမည်)", placeholder="ဥပမာ - thura_oo").strip()
                new_password = st.text_input("Password (လျှို့ဝှက်နံပါတ်)", type="password", placeholder="••••••••")
            
            with col2:
                # 🎯 Admin အလိုရှိသည့်အတိုင်း Role ကို ရွေးချယ်ခိုင်းသည့်နေရာ
                new_role = st.selectbox("Select User Role (လုပ်ပိုင်ခွင့်အဆင့်)", ["user", "super", "admin"])
                st.write("") # နေရာလွတ်လေး ခံပေးခြင်း
                st.write("")
                submit_user = st.form_submit_button("💾 Save New User")

        # ================= SAVE TO SUPABASE =================
        if submit_user:
            # လိုအပ်သော အချက်အလက်များ ဖြည့်မဖြည့် စစ်ဆေးခြင်း
            if not new_userid or not new_password:
                st.error("❌ ဝန်ထမ်းအကောင့်အမည် (User ID) နှင့် လျှို့ဝှက်နံပါတ် (Password) ကို မဖြစ်မနေ ဖြည့်စွက်ပေးရပါမည်။")
            else:
                try:
                    # ၁။ User ID ရှိနှင့်ပြီးသား ဟုတ်မဟုတ် အရင်စစ်ဆေးခြင်း (Duplicate Check)
                    existing_user = supabase.table("user_setup").select("user_id").eq("user_id", new_userid).execute()
                    
                    if existing_user.data:
                        st.error(f"❌ အကောင့်အမည် '**{new_userid}**' သည် စနစ်ထဲတွင် ရှိနှင့်ပြီးသား ဖြစ်နေပါသည်။ အခြားအမည်တစ်ခု ပြောင်းသုံးပေးပါ။")
                    else:
                        # ၂။ အချက်အလက်အသစ်ကို Supabase user_setup table ထဲသို့ သိမ်းဆည်းခြင်း
                        supabase.table("user_setup").insert({
                            "user_id": new_userid,
                            "password": new_password,
                            "role": new_role
                        }).execute()
                        
                        st.success(f"🎉 အကောင့်အသစ် '**{new_userid}**' ({new_role.upper()}) ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီဗျာ။")
                        st.balloons() # အောင်မြင်ကြောင်း အောင်ပွဲခံမိုးပျံပူဖောင်းလေးများ လွှတ်ပေးခြင်း
                        
                except Exception as e:
                    st.error(f"Save User Error: {e}")

        # ================= EXISTING USERS LIST =================
        st.divider()
        st.subheader("👥 Current System Users (လက်ရှိ ဝန်ထမ်းစာရင်း)")
        try:
            # လက်ရှိရှိနေသော အကောင့်များကို ဇယားဖြင့် ပြန်ပြပေးခြင်း
            user_res = supabase.table("user_setup").select("user_id", "role").execute()
            if user_res.data:
                user_df = pd.DataFrame(user_res.data)
                # ကော်လံခေါင်းစဉ်များကို သပ်သပ်ရပ်ရပ် ဖြစ်အောင် ပြောင်းလဲခြင်း
                user_df.columns = ["User ID (အကောင့်အမည်)", "Role (လုပ်ပိုင်ခွင့်ဆင့်)"]
                st.dataframe(user_df, use_container_width=True)
            else:
                st.info("စနစ်ထဲတွင် ဝန်ထမ်းစာရင်း မရှိသေးပါ။")
        except Exception as e:
            st.error(f"Load Users Error: {e}")