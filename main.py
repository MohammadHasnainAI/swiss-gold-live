import streamlit as st
import requests
import json
import time
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# 1. PAGE CONFIG & AUTO REFRESH
# -------------------------------
st.set_page_config(page_title="Islam Jewellery", page_icon="💎", layout="centered")

# Refresh every 4 minutes (240000ms) to match your API Limit
# This keeps you SAFE (800 requests/day)
st_autorefresh(interval=240000, key="gold_refresh")

# -------------------------------
# 2. CSS STYLING (Your Design)
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}
.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}
.price-card {background:#ffffff; border-radius:20px; padding:30px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:20px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:6px 14px; border-radius:30px; font-weight:700; font-size:0.75rem; letter-spacing:1px; display:inline-block; margin-bottom:15px;}
.big-price {font-size:3.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:5px;}
.stats-container {display:flex; gap:10px; margin-top:15px; justify-content:center;}
.stat-box {background:#fafafa; border-radius:10px; padding:10px 15px; text-align:center; border:1px solid #eeeeee; min-width: 100px;}
.stat-value {font-size:1.1rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase;}
.btn-grid {display: flex; gap: 15px; margin-top: 30px; justify-content: center;}
.contact-btn {flex: 1; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 600; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}
.footer {background:#f9f9f9; padding:25px; text-align:center; font-size:0.85rem; color:#555; margin-top:50px; border-top:1px solid #eee;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. LIVE FETCHING (The New Engine)
# -------------------------------
@st.cache_data(ttl=240, show_spinner=False)
def get_live_rates():
    try:
        # Get Keys
        TD_KEY = st.secrets["TWELVE_DATA_KEY"]
        CURR_KEY = st.secrets["CURR_KEY"]

        # Fetch Gold/Silver
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals).json()
        
        # Fetch Currency
        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr).json()

        return {
            "gold": float(metal_res['XAU/USD']['price']),
            "silver": float(metal_res['XAG/USD']['price']),
            "usd": curr_res['conversion_rates']['PKR'],
            "aed": curr_res['conversion_rates']['AED'],
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p")
        }
    except:
        return None

# -------------------------------
# 4. LOAD DATA & SETTINGS
# -------------------------------
live_data = get_live_rates()

if not live_data:
    st.error("⚠️ Connection weak. Refreshing...")
    st.stop()

# Load Admin Premium from GitHub (manual.json)
try:
    g = Github(st.secrets["GIT_TOKEN"])
    repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
    
    # Try to load manual.json
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
    except:
        settings = {"gold_premium": 0, "silver_premium": 0}
except:
    # If GitHub fails, use defaults (Safe Mode)
    settings = {"gold_premium": 0, "silver_premium": 0}

# Calculate Final Prices
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai = (live_data['gold'] / 31.1035) * live_data['aed']

# -------------------------------
# 5. DASHBOARD UI
# -------------------------------
st.markdown("""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

# GOLD CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">${live_data['gold']:,.0f}</div>
            <div class="stat-label">Int'l Ounce</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">AED {gold_dubai:,.0f}</div>
            <div class="stat-label">Dubai Gram</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# SILVER CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background-color:#f0f4f8; color:#4a5568;">● SILVER LIVE</div>
    <div class="big-price" style="font-size:2.5rem;">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
     <div style="font-size:0.8rem; color:#aaa; margin-top:10px;">Updated: {live_data['time']}</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 6. CONTACT
# -------------------------------
st.markdown("""
<div class="btn-grid">
    <a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a>
    <a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 7. ADMIN PANEL (Saving to GitHub)
# -------------------------------
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        if st.text_input("Password", type="password") == "123123":
            st.session_state.admin_auth = True
            st.rerun()

if st.session_state.admin_auth:
    st.markdown("---")
    st.subheader("⚙️ Update Premiums")
    
    # Use Session State to handle inputs
    if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
    if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)

    c1, c2 = st.columns(2)
    st.session_state.new_gold = c1.number_input("Gold Premium", value=st.session_state.new_gold, step=100)
    st.session_state.new_silver = c2.number_input("Silver Premium", value=st.session_state.new_silver, step=50)

    if st.button("💾 Save to GitHub"):
        try:
            # 1. Update manual.json (Premium Settings)
            new_settings = {
                "gold_premium": st.session_state.new_gold,
                "silver_premium": st.session_state.new_silver,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                contents = repo.get_contents("manual.json")
                repo.update_file(contents.path, "Update Settings", json.dumps(new_settings), contents.sha)
            except:
                repo.create_file("manual.json", "Init Settings", json.dumps(new_settings))

            # 2. Update History (For Charts)
            try:
                h_content = repo.get_contents("history.json")
                history = json.loads(h_content.decoded_content.decode())
            except:
                history = []
            
            history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "gold_pk": gold_tola,
                "silver_pk": silver_tola
            })
            if len(history) > 50: history = history[-50:] # Keep last 50
            
            try:
                repo.update_file(h_content.path, "Update History", json.dumps(history), h_content.sha)
            except:
                repo.create_file("history.json", "Init History", json.dumps(history))

            st.success("✅ Saved! Website will update in a moment.")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"GitHub Error: {e}")

# Footer
st.markdown(f"""
<div class="footer">
<b>Islam Jewellery</b> • Sarafa Bazar <br>
Dollar Rate: Rs {live_data['usd']:.2f}
</div>
""", unsafe_allow_html=True)
