import streamlit as st
import json
import time
import requests
from github import Github
from datetime import datetime, timedelta
import pytz

# --- CONFIGURATION ---
st.set_page_config(page_title="Islam Jewellery | Live Rates", page_icon="💎", layout="centered")

# --- PROFESSIONAL STYLING (CSS) ---
st.markdown("""
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
        
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Montserrat', sans-serif;
        }
        
        /* Hide Default Streamlit Menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Header Title Styling */
        .header-title {
            text-align: center;
            color: #1a1a1a;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .header-subtitle {
            text-align: center;
            color: #DAA520; /* Golden Rod */
            font-size: 1.2rem;
            margin-bottom: 30px;
            font-weight: 400;
        }

        /* LIVE Status Badge */
        .live-badge {
            background-color: #d4edda;
            color: #155724;
            padding: 8px 15px;
            border-radius: 50px;
            font-weight: bold;
            text-align: center;
            width: fit-content;
            margin: 0 auto 20px auto;
            border: 1px solid #c3e6cb;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* EXPIRED Status Badge */
        .expired-badge {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #f5c6cb;
            margin-bottom: 20px;
        }

        /* Info Cards (USD & Ounce) */
        .info-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s;
        }
        .info-card:hover {
            transform: translateY(-5px);
        }
        .info-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
        }
        .info-value {
            color: #333;
            font-size: 1.5rem;
            font-weight: 700;
        }

        /* MAIN GOLD PRICE CARD */
        .gold-card {
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-top: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #DAA520;
        }
        .gold-label {
            color: #DAA520;
            font-size: 1.2rem;
            letter-spacing: 1px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .gold-price {
            font-size: 3.5rem;
            font-weight: 800;
            color: #fff;
            text-shadow: 0 2px 10px rgba(218, 165, 32, 0.3);
        }
        .gold-footer {
            margin-top: 15px;
            font-size: 0.8rem;
            color: #aaa;
        }
        
        /* Footer Contact */
        .contact-section {
            text-align: center;
            margin-top: 40px;
            color: #555;
            font-size: 0.9rem;
        }

    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
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

# --- ADMIN PANEL ---
st.sidebar.markdown("## ⚙️ **Control Panel**")
password = st.sidebar.text_input("Admin Key", type="password")

if password == "123123":
    st.sidebar.success("🔓 Access Granted")
    st.sidebar.markdown("---")
    
    _, current_manual = load_data()
    
    st.sidebar.markdown("### 💰 Profit Adjustment")
    new_premium = st.sidebar.number_input("Extra Amount (PKR)", value=int(current_manual.get('premium', 0)), step=100)
    
    st.sidebar.markdown("### ⏳ Rate Validity")
    valid_hours = st.sidebar.slider("Hours Active", 1, 24, 4)
    
    if st.sidebar.button("🚀 UPDATE LIVE RATE", type="primary"):
        with st.spinner("Updating Server..."):
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
                    
                st.sidebar.success("✅ Updated Successfully!")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- MAIN APP ---
market, manual = load_data()

last_update_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_update_dt = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
last_update_dt = pytz.timezone('Asia/Karachi').localize(last_update_dt)

current_time = get_time_pk()
hours_passed = (current_time - last_update_dt).total_seconds() / 3600
is_expired = hours_passed > manual.get("valid_hours", 4)

ounce = market['price_ounce_usd']
usd_pkr = market['usd_to_pkr']
premium = manual['premium']
pak_tola = ((ounce / 31.1035) * 11.66 * usd_pkr) + premium

# --- UI DISPLAY ---

# 1. Header
st.markdown("""
    <div class='header-title'>ISLAM JEWELLERY</div>
    <div class='header-subtitle'>Premium Gold Rates • Daily Updates</div>
""", unsafe_allow_html=True)

# 2. Logic Display
if is_expired:
    st.markdown(f"""
        <div class='expired-badge'>
            <h2>⚠️ RATES EXPIRED</h2>
            <p>Market rates are currently closed or pending update.</p>
            <h3>📞 Call for Rates: 0300-1234567</h3>
            <small>Last Update: {last_update_str}</small>
        </div>
    """, unsafe_allow_html=True)
else:
    # Live Badge
    st.markdown(f"<div class='live-badge'>● LIVE MARKET ACTIVE</div>", unsafe_allow_html=True)

    # Info Cards (Grid Layout)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
            <div class='info-card'>
                <div class='info-label'>🌍 Int'l Ounce</div>
                <div class='info-value'>${ounce:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class='info-card'>
                <div class='info-label'>🇺🇸 USD Rate</div>
                <div class='info-value'>Rs {usd_pkr:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    # Big Gold Card
    st.markdown(f"""
        <div class='gold-card'>
            <div class='gold-label'>🇵🇰 Pure Gold Rate (Per Tola)</div>
            <div class='gold-price'>Rs {pak_tola:,.0f}</div>
            <div class='gold-footer'>
                Based on Int'l Market + Premium Adjustment<br>
                Last Updated: {last_update_str}
            </div>
        </div>
    """, unsafe_allow_html=True)

# 3. Footer
st.markdown("""
    <div class='contact-section'>
        <p>Islam Jewellery • Main Sarafa Bazar • Trusted Since 1990</p>
    </div>
""", unsafe_allow_html=True)
