import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz
import pandas as pd
import altair as alt

# -------------------------------
# 1. CONFIG
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="wide"
)

# -------------------------------
# 2. AUTO REFRESH SETUP
# -------------------------------
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# Refresh every 10 sec
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
elif time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# -------------------------------
# 3. CSS STYLING
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

.price-card {background:#ffffff; border-radius:20px; padding:40px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:30px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:8px 16px; border-radius:30px; font-weight:700; font-size:0.8rem; letter-spacing:1px; display:inline-block; margin-bottom:20px;}
.closed-badge {background-color:#fce8e6; color:#c5221f; padding:8px 16px; border-radius:30px; font-weight:700; font-size:0.8rem; letter-spacing:1px; display:inline-block; margin-bottom:20px;}
.big-price {font-size:4.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:10px;}

.stats-container {display:flex; gap:15px; margin-top:20px;}
.stat-box {flex:1; background:#fafafa; border-radius:15px; padding:20px; text-align:center; border:1px solid #eeeeee;}
.stat-value {font-size:1.4rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.75rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-top:5px;}

.btn-grid {display:flex; gap:15px; margin-top:30px;}
.contact-btn {flex:1; padding:15px; border-radius:12px; text-align:center; text-decoration:none; font-weight:600; transition:transform 0.2s; box-shadow:0 4px 10px rgba(0,0,0,0.05);}
.btn-call {background-color:#111; color:white !important;}
.btn-whatsapp {background-color:#25D366; color:white !important;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 4. DATA LOGIC
# -------------------------------
def get_time():
    return datetime.now(pytz.timezone("Asia/Karachi"))

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

market, manual = load_data()
last_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_dt = pytz.timezone("Asia/Karachi").localize(datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S"))
current_time = get_time()
is_expired = (current_time - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)
pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# 5. MAIN DISPLAY
# -------------------------------
st.markdown("""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

# Price Card
if is_expired:
    st.markdown(f"""
    <div class="price-card">
        <div class="closed-badge">● MARKET CLOSED</div>
        <div class="big-price" style="color:#ccc;">PENDING</div>
        <div class="price-label">Waiting for Rate Update</div>
        <div style="font-size:0.8rem; color:#aaa; margin-top:15px;">Last: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge">● LIVE RATE</div>
        <div class="big-price">Rs {pk_price:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div style="font-size:0.8rem; color:#aaa; margin-top:15px;">Updated: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)

# Stats
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
""", unsafe_allow_html=True)

# Contact Buttons
st.markdown("""
<div class="btn-grid">
    <a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a>
    <a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 6. ADMIN LOGIN & LOGOUT
# -------------------------------
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if st.session_state.admin_authenticated:
    if st.button("🔒 Logout Admin"):
        st.session_state.admin_authenticated = False
        st.experimental_rerun()

with st.expander("Admin Login"):
    if not st.session_state.admin_authenticated:
        key_input = st.text_input("Enter Admin Access Key", type="password")
        if st.button("Login"):
            if key_input == "123123":
                st.session_state.admin_authenticated = True
                st.success("Admin Access Granted ✅")
            else:
                st.error("Incorrect Key ❌")

# -------------------------------
# 7. ADMIN DASHBOARD
# -------------------------------
if st.session_state.admin_authenticated:
    st.markdown("---")
    st.title("⚙️ Admin Dashboard")
    tabs = st.tabs(["Update Prices", "Stats", "History", "Gold Price Chart"])

    # --- TAB 1: Update Prices ---
    with tabs[0]:
        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = manual["premium"]

        col1, col2 = st.columns(2)
        col1.button("- 500", on_click=lambda: st.session_state.update({"admin_premium": st.session_state.admin_premium-500}))
        col2.button("+ 500", on_click=lambda: st.session_state.update({"admin_premium": st.session_state.admin_premium+500}))
        st.number_input("Profit Margin (Rs)", key="admin_premium", step=100)

        if st.button("🚀 Publish Rate"):
            st.success("✅ (Simulation) Price Updated & Logged")  # You can enable GitHub update later

    # --- TAB 2: Stats ---
    with tabs[1]:
        st.subheader("Current Stats")
        st.metric("Current Premium", f"Rs {manual['premium']}")
        st.metric("USD to PKR", f"Rs {market['usd_to_pkr']}")
        st.metric("Gold Price/Ounce", f"${market['price_ounce_usd']}")

    # --- TAB 3: History ---
    with tabs[2]:
        st.subheader("Price Update History")
        st.info("No history yet (enable GitHub integration later)")

    # --- TAB 4: Gold Price Chart ---
    with tabs[3]:
        st.subheader("Gold Price Trend (Last Updates)")
        st.info("No data yet (enable GitHub integration later)")

# -------------------------------
# 8. WEBSITE INFO / DISCLAIMER
# -------------------------------
st.markdown("---")
st.subheader("Website Info & Disclaimer")
st.markdown("""
**Islam Jewellery** shows approximate gold prices.  
Prices update based on market data & admin-set premium.  

⚠️ **Disclaimer:**  
- Prices are indicative & may change anytime.  
- Always verify with the shop before buying.  
- Contact shop directly for confirmed gold rates.
""")
