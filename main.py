import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# -------------------------------
# 1. CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="wide"
)

# -------------------------------
# 2. EUROPEAN CLEAN CSS
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.stApp {background-color:#ffffff; font-family:'Outfit',sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

.header-box {text-align:center; padding-bottom:20px; margin-bottom:20px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

.price-card {background:#ffffff; border-radius:20px; padding:40px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:30px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:8px 16px; border-radius:30px; font-weight:700; font-size:0.8rem; letter-spacing:1px; display:inline-block; margin-bottom:20px;}
.closed-badge {background-color:#fce8e6; color:#c5221f; padding:8px 16px; border-radius:30px; font-weight:700; font-size:0.8rem; letter-spacing:1px; display:inline-block; margin-bottom:20px;}
.big-price {font-size:4.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:10px;}

.stats-container {display:flex; gap:15px; margin-top:20px;}
.stat-box {flex:1; background:#fafafa; border-radius:15px; padding:20px; text-align:center; border:1px solid #eee;}
.stat-value {font-size:1.4rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.75rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-top:5px;}

.btn-grid {display:flex; gap:15px; margin-top:30px;}
.contact-btn {flex:1; padding:15px; border-radius:12px; text-align:center; text-decoration:none; font-weight:600; transition: transform 0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.05);}
.btn-call {background-color:#111; color:white !important;}
.btn-whatsapp {background-color:#25D366; color:white !important;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}

.admin-container {padding:20px; background:#f8f9fa; border-radius:20px; margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. DATA LOGIC
# -------------------------------
def get_time():
    return datetime.now(pytz.timezone("Asia/Karachi"))

def load_data():
    try:
        with open("prices.json","r") as f: market=json.load(f)
    except: market={"price_ounce_usd":0,"usd_to_pkr":0}
    try:
        with open("manual.json","r") as f: manual=json.load(f)
    except: manual={"premium":0,"last_updated":"2000-01-01 00:00:00","valid_hours":4}
    return market, manual

market, manual = load_data()
last_str = manual.get("last_updated","2000-01-01 00:00:00")
last_dt = pytz.timezone("Asia/Karachi").localize(datetime.strptime(last_str,"%Y-%m-%d %H:%M:%S"))
current_time = get_time()
is_expired = (current_time-last_dt).total_seconds()/3600 > manual.get("valid_hours",4)
pk_price = ((market["price_ounce_usd"]/31.1035)*11.66*market["usd_to_pkr"])+manual["premium"]

# -------------------------------
# 4. CUSTOMER PAGE
# -------------------------------
st.markdown(f"""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""",unsafe_allow_html=True)

if is_expired:
    st.markdown(f"""
    <div class="price-card">
        <div class="closed-badge">● MARKET CLOSED</div>
        <div class="big-price" style="color:#ccc;">PENDING</div>
        <div class="price-label">Waiting for Rate Update</div>
        <div style="font-size:0.8rem; color:#aaa; margin-top:15px;">Last: {last_str}</div>
    </div>
    """,unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge">● LIVE RATE</div>
        <div class="big-price">Rs {pk_price:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div style="font-size:0.8rem; color:#aaa; margin-top:15px;">Updated: {last_str}</div>
    </div>
    """,unsafe_allow_html=True)

st.markdown(f"""
<div class="stats-container">
    <div class="stat-box">
        <div class="stat-value">${market['price_ounce_usd']:,.0f}</div>
        <div class="stat-label">Int'l Ounce</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">Rs {market['usd_to_pkr']:.2f}</div>
        <div class="stat-label">USD Rate</div>
    </div>
</div>
""",unsafe_allow_html=True)

st.markdown("""
<div class="btn-grid">
    <a href="tel:03001234567" class="contact-btn btn-call">📞 Call Now</a>
    <a href="https://wa.me/923001234567" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""",unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:40px; font-size:0.75rem; color:#999; text-align:center;">
    ⚠️ Disclaimer: Gold prices are indicative and may vary. Always contact for final confirmation. We are not responsible for trading losses.
</div>
""",unsafe_allow_html=True)

# -------------------------------
# 5. FULL ADMIN DASHBOARD
# -------------------------------
st.markdown("---")
st.markdown("<h2 style='text-align:center;'>Admin Dashboard</h2>", unsafe_allow_html=True)

if "GIT_TOKEN" not in st.secrets:
    st.error("GitHub Token Missing in Secrets!")
else:
    pwd = st.text_input("Enter Admin Key to Access Dashboard", type="password")
    if pwd == "123123":
        st.success("Access Granted")

        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = int(manual["premium"])

        tabs = st.tabs(["📊 Dashboard","⚙️ Update Prices","📜 History"])

        # -------------------
        # TAB 1: DASHBOARD
        # -------------------
        with tabs[0]:
            st.markdown('<div class="admin-container">',unsafe_allow_html=True)
            st.subheader("Current Stats")
            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Gold Price", f"Rs {pk_price:,.0f}")
            col2.metric("USD Rate", f"Rs {market['usd_to_pkr']:.2f}")
            col3.metric("Premium", f"Rs {st.session_state.admin_premium}")
            col4.metric("Last Updated", last_str)
            st.markdown("</div>",unsafe_allow_html=True)

        # -------------------
        # TAB 2: UPDATE PRICES
        # -------------------
        with tabs[1]:
            st.subheader("Update Premium")
            def update_val(val):
                st.session_state.admin_premium += val
            c1,c2 = st.columns(2)
            c1.button("-500", on_click=update_val,args=(-500,))
            c2.button("+500", on_click=update_val,args=(500,))
            st.number_input("Premium Amount (Rs)", key="admin_premium", step=100)
            if st.button("🚀 Publish Rate"):
                try:
                    g = Github(st.secrets["GIT_TOKEN"])
                    repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                    data={
                        "premium": st.session_state.admin_premium,
                        "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                        "valid_hours":4
                    }
                    try:
                        contents=repo.get_contents("manual.json")
                        repo.update_file(contents.path,"Update",json.dumps(data),contents.sha)
                    except:
                        repo.create_file("manual.json","Init",json.dumps(data))
                    st.success("✅ Updated!")
                    time.sleep(1)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        # -------------------
        # TAB 3: HISTORY
        # -------------------
        with tabs[2]:
            st.subheader("Price Update History")
            st.info("History logs can be integrated using Git commit logs or manual JSON tracking. For now, this will display last update only.")
            st.write(manual)
