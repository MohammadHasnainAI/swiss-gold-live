import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Islam Jewellery", page_icon="💎", layout="centered")

# --- 2. 2026 FUTURISTIC CSS ---
st.markdown("""
    <style>
        /* Import Modern Font (Poppins) */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

        /* MAIN BACKGROUND */
        .stApp {
            background-color: #050505;
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 100% 100%, rgba(255, 215, 0, 0.05) 0%, transparent 50%);
            color: white;
            font-family: 'Poppins', sans-serif;
        }

        /* HIDE DEFAULT MENU */
        #MainMenu, header, footer {visibility: hidden;}

        /* ANIMATED GOLD TEXT (Shimmer Effect) */
        @keyframes shimmer {
            0% {background-position: -200% center;}
            100% {background-position: 200% center;}
        }
        .gold-title {
            font-size: 45px;
            font-weight: 800;
            text-align: center;
            text-transform: uppercase;
            background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
            background-size: 200% auto;
            color: #000;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s linear infinite;
            margin-bottom: 5px;
            letter-spacing: 2px;
        }

        /* SUBTITLE */
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 14px;
            letter-spacing: 4px;
            margin-bottom: 40px;
            text-transform: uppercase;
        }

        /* GLASS CARDS (The "2026" Look) */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 215, 0, 0.15);
            border-radius: 24px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            margin-bottom: 20px;
        }

        /* PULSING LIVE DOT */
        @keyframes pulse-red {
            0% {box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.7);}
            70% {box-shadow: 0 0 0 10px rgba(255, 82, 82, 0);}
            100% {box-shadow: 0 0 0 0 rgba(255, 82, 82, 0);}
        }
        @keyframes pulse-green {
            0% {box-shadow: 0 0 0 0 rgba(50, 205, 50, 0.7);}
            70% {box-shadow: 0 0 0 10px rgba(50, 205, 50, 0);}
            100% {box-shadow: 0 0 0 0 rgba(50, 205, 50, 0);}
        }
        .dot-live {
            height: 12px;
            width: 12px;
            background-color: #32cd32;
            border-radius: 50%;
            display: inline-block;
            animation: pulse-green 2s infinite;
            margin-right: 8px;
        }
        .dot-closed {
            height: 12px;
            width: 12px;
            background-color: #ff5252;
            border-radius: 50%;
            display: inline-block;
            animation: pulse-red 2s infinite;
            margin-right: 8px;
        }

        /* BIG PRICE */
        .price-tag {
            font-size: 65px;
            font-weight: 700;
            color: #fff;
            margin: 10px 0;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        }

        /* SMALL INFO BOXES */
        .stat-box {
            background: rgba(0,0,0,0.5);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #333;
        }
        .stat-label { font-size: 11px; color: #aaa; letter-spacing: 1px; }
        .stat-val { font-size: 20px; font-weight: 600; color: #FFD700; }

    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
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
last_up_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_up_dt = pytz.timezone('Asia/Karachi').localize(datetime.strptime(last_up_str, "%Y-%m-%d %H:%M:%S"))
is_expired = (get_time() - last_up_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)

# Calculations
pk_rate = ((market['price_ounce_usd'] / 31.1035) * 11.66 * market['usd_to_pkr']) + manual['premium']

# --- 4. MAIN DISPLAY ---

# Header
st.markdown("<div class='gold-title'>ISLAM JEWELLERY</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>PREMIUM GOLD & BULLION • SARAFA BAZAR</div>", unsafe_allow_html=True)

if is_expired:
    # --- CLOSED STATE ---
    st.markdown(f"""
        <div class='glass-card' style='border-color: #ff5252;'>
            <div style='color: #ff5252; font-weight: bold; letter-spacing: 2px;'>
                <span class='dot-closed'></span>MARKET CLOSED
            </div>
            <div style='font-size: 40px; color: #555; margin: 20px 0;'>Rate Pending</div>
            <p style='color: #aaa;'>Rates are currently being updated.</p>
            <div style='background: #222; padding: 10px; border-radius: 10px; margin-top: 15px; display: inline-block;'>
                📞 0300-1234567
            </div>
        </div>
    """, unsafe_allow_html=True)

else:
    # --- LIVE STATE ---
    st.markdown(f"""
        <div class='glass-card'>
            <div style='color: #32cd32; font-weight: bold; letter-spacing: 2px;'>
                <span class='dot-live'></span>LIVE MARKET
            </div>
            <div style='color: #888; font-size: 14px; margin-top: 5px;'>24K PURE GOLD (PER TOLA)</div>
            
            <div class='price-tag'>Rs {pk_rate:,.0f}</div>
            
            <div style='color: #666; font-size: 12px; margin-top: 10px;'>
                Updated: {last_up_str}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Small Stats Grid
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>INT'L OUNCE</div>
            <div class='stat-val'>${market['price_ounce_usd']:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>USD TO PKR</div>
            <div class='stat-val'>Rs {market['usd_to_pkr']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 5. HIDDEN ADMIN (GEAR ICON) ---
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Settings"): # Subtle gear icon
    pwd = st.text_input("Access Key", type="password")
    if pwd == "123123":
        st.success("Unlocked")
        new_prem = st.number_input("Profit (PKR)", value=int(manual['premium']), step=100)
        hours = st.slider("Hours Valid", 1, 24, 4)
        if st.button("Update"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                r = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                data = {"premium": new_prem, "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"), "valid_hours": hours}
                try: r.update_file("manual.json", "Upd", json.dumps(data), r.get_contents("manual.json").sha)
                except: r.create_file("manual.json", "Init", json.dumps(data))
                st.rerun()
            except: st.error("Token Error")
