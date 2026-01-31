import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# --- CONFIGURATION (Must be first) ---
st.set_page_config(page_title="Islam Jewellery", page_icon="💎", layout="centered")

# --- LUXURY DARK THEME CSS ---
st.markdown("""
    <style>
        /* Import Elegant Font */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
        
        /* 1. Background & Main Colors */
        .stApp {
            background-color: #0e0e0e;
            background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 100%);
            color: #d4af37; /* Gold Color */
        }
        
        /* 2. Typography */
        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            color: #d4af37 !important;
            text-align: center;
        }
        p, div {
            font-family: 'Lato', sans-serif;
        }

        /* 3. The Main Gold Price Card (Glass Effect) */
        .gold-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.1);
            margin: 20px 0;
            animation: fadeIn 1.5s ease-in-out;
        }
        
        /* 4. Price Text */
        .big-price {
            font-size: 80px;
            font-weight: 700;
            background: -webkit-linear-gradient(#fff, #d4af37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 10px 0;
        }
        
        /* 5. Small Info Cards */
        .info-box {
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            color: #888;
        }
        .info-value {
            color: #fff;
            font-size: 24px;
            font-weight: bold;
        }

        /* 6. Animations */
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        /* 7. Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 8. Status Badges */
        .status-live {
            color: #28a745;
            letter-spacing: 2px;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-expired {
            color: #dc3545;
            letter-spacing: 2px;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
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

# --- DATA LOADING ---
market, manual = load_data()
last_update_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_update_dt = pytz.timezone('Asia/Karachi').localize(datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S"))
current_time = get_time_pk()
is_expired = (current_time - last_update_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)

ounce = market['price_ounce_usd']
usd_pkr = market['usd_to_pkr']
premium = manual['premium']
pak_tola = ((ounce / 31.1035) * 11.66 * usd_pkr) + premium

# --- MAIN UI ---

# 1. Logo/Header
st.markdown("<br><h1 style='font-size: 50px;'>ISLAM JEWELLERY</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; letter-spacing: 3px;'>EST. 1990 • SARAFA BAZAR</p>", unsafe_allow_html=True)

# 2. Main Content
if is_expired:
    st.markdown("""
        <div class='gold-card' style='border-color: #dc3545;'>
            <div class='status-expired'>● MARKET CLOSED</div>
            <div class='big-price' style='-webkit-text-fill-color: #555; font-size: 40px;'>Rate Pending</div>
            <p>Please contact us for the latest rates.</p>
            <h3>📞 0300-1234567</h3>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class='gold-card'>
            <div class='status-live'>● LIVE MARKET RATE</div>
            <div style='margin-top: 10px; color: #888;'>24K GOLD PER TOLA</div>
            <div class='big-price'>Rs {pak_tola:,.0f}</div>
            <p style='color: #666; font-size: 12px;'>UPDATED: {last_update_str} (PKT)</p>
        </div>
    """, unsafe_allow_html=True)

    # 3. Small Details (Grid)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='info-box'><div style='font-size:12px;'>INTERNATIONAL OUNCE</div><div class='info-value'>${ounce:,.0f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='info-box'><div style='font-size:12px;'>DOLLAR RATE</div><div class='info-value'>Rs {usd_pkr:.2f}</div></div>", unsafe_allow_html=True)

# --- SECRET ADMIN PANEL (Invisible) ---
st.sidebar.markdown("---")
# We use an 'expander' with a Lock icon. It looks like a tiny button.
with st.sidebar.expander("🔒 Admin Access"):
    password = st.text_input("Key", type="password")
    if password == "123123":
        st.success("Authorized")
        
        # Admin Controls
        new_premium = st.number_input("Profit/Premium", value=int(premium), step=500)
        valid_hours = st.slider("Hours Valid", 1, 24, 4)
        
        if st.button("Update Price"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                save_data = {
                    "premium": new_premium,
                    "last_updated": get_time_pk().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": valid_hours
                }
                # Save to GitHub
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Update", json.dumps(save_data), contents.sha)
                except:
                    repo.create_file("manual.json", "Init", json.dumps(save_data))
                st.success("Updated! Refreshing...")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
