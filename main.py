import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Islam Jewellery", page_icon="💎", layout="centered")

# --- 2. LUXURY CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
        .stApp {
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 0%, #1c1c1c 0%, #000000 70%);
            font-family: 'Outfit', sans-serif;
            color: white;
        }
        #MainMenu, header, footer {visibility: hidden;}
        
        /* CARD DESIGN */
        .glass-panel {
            background: rgba(20, 20, 20, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
        }
        .price-text {
            font-size: 80px;
            font-weight: 700;
            color: white;
            text-shadow: 0 0 20px #D4AF37;
            margin: 0;
            line-height: 1;
        }
        .sub-text { font-size: 14px; color: #888; letter-spacing: 2px; text-transform: uppercase; }
        .gold-title { font-size: 40px; font-weight: 700; color: #D4AF37; text-align: center; letter-spacing: 2px;}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
def get_time(): return datetime.now(pytz.timezone('Asia/Karachi'))

def load_data():
    try:
        with open("prices.json", "r") as f: m = json.load(f)
    except: m = {"price_ounce_usd": 0, "usd_to_pkr": 0}
    try:
        with open("manual.json", "r") as f: a = json.load(f)
    except: a = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}
    return m, a

market, manual = load_data()
last_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_dt = pytz.timezone('Asia/Karachi').localize(datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S"))
is_expired = (get_time() - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)
pk_price = ((market['price_ounce_usd'] / 31.1035) * 11.66 * market['usd_to_pkr']) + manual['premium']

# --- 4. DISPLAY ---
st.markdown("<div class='gold-title'>ISLAM JEWELLERY</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #666; margin-bottom: 30px;'>EST. 1990 • SARAFA BAZAR</div>", unsafe_allow_html=True)

if is_expired:
    st.markdown(f"""
        <div class='glass-panel' style='border-color: #ff4444;'>
            <div style='color: #ff4444; font-weight: bold; letter-spacing: 2px;'>● MARKET CLOSED</div>
            <div style='font-size: 40px; color: #555; margin: 20px 0;'>PENDING</div>
            <div class='sub-text'>Contact: 0300-1234567</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class='glass-panel'>
            <div style='color: #32cd32; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;'>● LIVE RATE</div>
            <div class='price-text'>Rs {pk_price:,.0f}</div>
            <div class='sub-text' style='margin-top: 15px;'>24K Gold Per Tola</div>
            <div style='font-size: 12px; color: #555; margin-top: 10px;'>Updated: {last_str}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 5. ADMIN ---
st.sidebar.markdown("---")
with st.sidebar.expander("🔒 Admin"):
    if st.text_input("Key", type="password") == "123123":
        st.success("Unlocked")
        new_prem = st.number_input("Profit", value=int(manual['premium']), step=100)
        if st.button("Update"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                data = {"premium": new_prem, "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"), "valid_hours": 4}
                try: repo.update_file("manual.json", "Upd", json.dumps(data), repo.get_contents("manual.json").sha)
                except: repo.create_file("manual.json", "Init", json.dumps(data))
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
