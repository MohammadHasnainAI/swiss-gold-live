import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# -------------------------------
# 1. PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="centered"
)

# -------------------------------
# 2. CSS STYLING
# -------------------------------
st.markdown("""
<style>
.stApp {background-color: #FFFFFF; font-family: 'Arial', sans-serif;}
h1, h2, h3 {color: #111111;}
.status-box {
    padding: 30px; 
    border: 3px solid #000; 
    background-color: #f8d7da;
    color: #721c24;
    text-align: center; 
    margin-bottom: 20px;
    border-radius: 10px;
}
.live-box {
    padding: 15px;
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 20px;
    font-weight: 700;
}
.footer {
    text-align: center;
    padding: 20px 0;
    margin-top: 50px;
    border-top: 1px solid #ddd;
    color: #555;
    font-size: 0.85rem;
}
.btn-space {margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. HELPER FUNCTIONS
# -------------------------------
def get_time_pk():
    return datetime.now(pytz.timezone('Asia/Karachi'))

def load_data():
    try:
        with open("prices.json", "r") as f:
            market = json.load(f)
    except:
        market = {"price_ounce_usd": 0, "usd_to_pkr": 0}
    try:
        with open("manual.json", "r") as f:
            manual = json.load(f)
    except:
        manual = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}
    return market, manual

# -------------------------------
# 4. ADMIN SIDEBAR
# -------------------------------
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

st.sidebar.header("🔒 Admin Login")

if st.session_state.admin_authenticated:
    st.sidebar.success("✅ Logged In")
    # Admin actions
    st.sidebar.subheader("💰 Update Price")
    market, manual = load_data()
    new_premium = st.sidebar.number_input("Add/Sub Amount (PKR)", value=int(manual.get('premium',0)), step=100)
    valid_hours = st.sidebar.slider("Keep price live for (Hours)", 1, 24, manual.get("valid_hours",4))

    if st.sidebar.button("🔴 UPDATE NOW", key="update_price"):
        with st.spinner("Saving to Database..."):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                
                save_data = {
                    "premium": new_premium,
                    "last_updated": get_time_pk().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": valid_hours
                }
                json_content = json.dumps(save_data, indent=4)
                
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Admin Update", json_content, contents.sha)
                except:
                    repo.create_file("manual.json", "Init Admin", json_content)
                
                st.sidebar.success("✅ Saved! Refreshing...")
                time.sleep(1)
                st.experimental_rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
    
    if st.sidebar.button("🔓 Logout", key="logout"):
        st.session_state.admin_authenticated = False
        st.experimental_rerun()

else:
    password = st.sidebar.text_input("Enter Password", type="password")
    if st.sidebar.button("Login"):
        if password == "123123":
            st.session_state.admin_authenticated = True
            st.sidebar.success("✅ Logged In")
            st.experimental_rerun()
        else:
            st.sidebar.error("❌ Incorrect Password")

# -------------------------------
# 5. MAIN APP LOGIC
# -------------------------------
market, manual = load_data()
last_update_str = manual.get("last_updated","2000-01-01 00:00:00")
last_update_dt = datetime.strptime(last_update_str,"%Y-%m-%d %H:%M:%S")
last_update_dt = pytz.timezone('Asia/Karachi').localize(last_update_dt)

current_time = get_time_pk()
hours_passed = (current_time - last_update_dt).total_seconds() / 3600
is_expired = hours_passed > manual.get("valid_hours",4)

ounce = market['price_ounce_usd']
usd_pkr = market['usd_to_pkr']
premium = manual['premium']
pak_tola = ((ounce/31.1035)*11.66*usd_pkr)+premium

# --- DISPLAY ---
st.title("💎 ISLAM JEWELLERY 💎")
st.markdown("<br>", unsafe_allow_html=True)

if is_expired:
    st.markdown(f"""
    <div class="status-box">
        <h2>⚠️ RATES EXPIRED</h2>
        <p>The rates have not been updated recently.</p>
        <h3>📞 Please Contact: 0349-2114166</h3>
        <p style="font-size:12px">Last Update: {last_update_str}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="live-box">
        ✅ Rates are LIVE (Valid for {manual.get('valid_hours')} hours)
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1,1])
col1.metric("🌍 Int'l Ounce", f"${ounce:,.2f}")
col2.metric("💵 USD Rate", f"Rs {usd_pkr:.2f}")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>🇵🇰 PAKISTAN GOLD RATE</h2>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; font-size:60px;'>Rs {pak_tola:,.0f}</h1>", unsafe_allow_html=True)
st.caption(f"Includes Market Premium: Rs {premium}")
st.caption(f"Last Admin Update: {last_update_str}")
st.markdown("<br>", unsafe_allow_html=True)

# --- CONTACT BUTTONS ---
col1, col2 = st.columns(2)
with col1:
    st.markdown('<a href="tel:03492114166" class="btn-space" style="background:#111;color:white;padding:15px 25px;border-radius:10px;text-align:center;display:block;text-decoration:none;">📞 CALL NOW</a>', unsafe_allow_html=True)
with col2:
    st.markdown('<a href="https://wa.me/923492114166" class="btn-space" style="background:#25D366;color:white;padding:15px 25px;border-radius:10px;text-align:center;display:block;text-decoration:none;">💬 WHATSAPP</a>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("<div class='footer'>© 2026 Islam Jewellery | Rates are indicative. Always verify with shop before buying.</div>", unsafe_allow_html=True)
