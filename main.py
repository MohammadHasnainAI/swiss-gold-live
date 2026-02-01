import streamlit as st
import requests
import json
from datetime import datetime
import pytz
from github import Github
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# 1. PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Islam Jewellery V12", page_icon="💎", layout="centered")
st_autorefresh(interval=240000, key="gold_refresh")

# -----------------------------
# 2. HELPER FUNCTIONS (The "Magic" Fix)
# -----------------------------
def adjust_premium(key, amount):
    """Updates the premium immediately when button is clicked."""
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] += amount

def clear_cache():
    """Forces the app to get fresh prices."""
    get_live_rates.clear()

# -----------------------------
# 3. CSS DESIGN
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* Header */
.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

/* Cards */
.price-card {background:#ffffff; border-radius:20px; padding:30px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:20px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:6px 14px; border-radius:30px; font-weight:700; font-size:0.75rem; letter-spacing:1px; display:inline-block; margin-bottom:15px;}
.big-price {font-size:3.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:5px;}

/* Stats */
.stats-container {display:flex; gap:8px; margin-top:15px; justify-content:center; flex-wrap: wrap;}
.stat-box {background:#fafafa; border-radius:10px; padding:10px; text-align:center; border:1px solid #eeeeee; flex: 1; min-width: 80px;}
.stat-value {font-size:1.0rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase;}

/* Buttons */
.btn-grid {display: flex; gap: 15px; margin-top: 30px; justify-content: center;}
.contact-btn {flex: 1; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 600; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}

/* Footer */
.footer {background:#f9f9f9; padding:25px; text-align:center; font-size:0.85rem; color:#555; margin-top:50px; border-top:1px solid #eee; line-height: 1.6;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 4. DATA ENGINE
# -----------------------------
repo = None
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except:
    pass

@st.cache_data(ttl=3600, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR: Keys Missing"
    
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    try:
        # Metals
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals).json()

        # Currency
        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr).json()
        
        # Process
        gold_price = 0
        silver_price = 0
        
        if "XAU/USD" in metal_res and "price" in metal_res["XAU/USD"]:
            gold_price = float(metal_res['XAU/USD']['price'])
        if "XAG/USD" in metal_res and "price" in metal_res["XAG/USD"]:
            silver_price = float(metal_res['XAG/USD']['price'])
            
        # Fallback to prevent 0
        if gold_price == 0: gold_price = 2750.00
        if silver_price == 0: silver_price = 32.00 
        
        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd_bank": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
        }
    except Exception as e:
        return f"UNKNOWN ERROR: {str(e)}"

# Load Data
live_data = get_live_rates()

if isinstance(live_data, str):
    st.warning(f"⚠️ {live_data}")
    live_data = {"gold": 2750.0, "silver": 32.0, "usd_bank": 278.0, "aed": 3.67, "time": "Offline"}

# Load Settings
settings = {"gold_premium": 0, "silver_premium": 0, "usd_adj": 0}
if repo:
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
    except:
        pass

# Initialize Session State (Important for inputs)
if "gold_premium" not in st.session_state: st.session_state.gold_premium = int(settings.get("gold_premium", 0))
if "silver_premium" not in st.session_state: st.session_state.silver_premium = int(settings.get("silver_premium", 0))
if "usd_adj" not in st.session_state: st.session_state.usd_adj = float(settings.get("usd_adj", 0.0))

# Calculations
final_usd_rate = live_data['usd_bank'] + settings.get("usd_adj", 0)
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * final_usd_rate) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * final_usd_rate) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# -----------------------------
# 5. UI DISPLAY
# -----------------------------
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['gold']:,.0f}</div><div class="stat-label">Int'l Ounce</div></div>
        <div class="stat-box"><div class="stat-value">Rs {final_usd_rate:.2f}</div><div class="stat-label">Dollar Rate</div></div>
        <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai Tola</div></div>
    </div>
    <div style="font-size:0.75rem; color:#aaa; margin-top:15px; padding-top:10px; border-top:1px solid #eee;">
        Last Update: <b>{live_data['time']}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# REFRESH BUTTON (Inside Gold Area)
if st.button("🔄 Check for New Prices", use_container_width=True):
    clear_cache()
    st.rerun()

# SILVER CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background-color:#f0f4f8; color:#4a5568;">● SILVER LIVE</div>
    <div class="big-price" style="font-size:2.5rem;">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['silver']:,.2f}</div><div class="stat-label">Int'l Ounce</div></div>
        <div class="stat-box"><div class="stat-value">{live_data['time']}</div><div class="stat-label">Last Update</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# -----------------------------
# 6. ADMIN DASHBOARD (Bug Free)
# -----------------------------
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        if st.text_input("Password", type="password") == "123123":
            st.session_state.admin_auth = True
            st.rerun()

if st.session_state.admin_auth:
    st.markdown("---")
    st.title("⚙️ Admin Dashboard")
    if st.button("🔴 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    tabs = st.tabs(["Update Prices", "Stats"])

    with tabs[0]:
        # DOLLAR ADJ
        st.subheader("💵 Dollar Adjustment")
        c1, c2, c3 = st.columns([1,1,2])
        # on_click FIXES the jumping bug!
        c1.button("- 0.5", on_click=adjust_premium, args=("usd_adj", -0.5))
        c2.button("+ 0.5", on_click=adjust_premium, args=("usd_adj", 0.5))
        st.number_input("Dollar Adj (Rs)", key="usd_adj", step=0.1)

        st.divider()

        # METAL PREMIUMS
        metal_choice = st.radio("Select Metal:", ["Gold", "Silver"], horizontal=True)
        if metal_choice == "Gold":
            st.subheader("🟡 Gold Premium")
            c1, c2, c3 = st.columns([1,1,2])
            c1.button("- 500", key="g_sub", on_click=adjust_premium, args=("gold_premium", -500))
            c2.button("+ 500", key="g_add", on_click=adjust_premium, args=("gold_premium", 500))
            st.number_input("Gold Premium (Rs)", key="gold_premium", step=100)
        else:
            st.subheader("⚪ Silver Premium")
            d1, d2, d3 = st.columns([1,1,2])
            d1.button("- 50", key="s_sub", on_click=adjust_premium, args=("silver_premium", -50))
            d2.button("+ 50", key="s_add", on_click=adjust_premium, args=("silver_premium", 50))
            st.number_input("Silver Premium (Rs)", key="silver_premium", step=50)

        if st.button("🚀 Publish Changes", type="primary"):
            if repo:
                try:
                    new_settings = {
                        "gold_premium": st.session_state.gold_premium, 
                        "silver_premium": st.session_state.silver_premium,
                        "usd_adj": st.session_state.usd_adj
                    }
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, "Update", json.dumps(new_settings), contents.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
                    st.success("✅ Updated!")
                    clear_cache()
                    st.rerun()
                except Exception as e:
                    st.error(f"GitHub Error: {e}")

    with tabs[1]:
        st.metric("Gold Premium", f"Rs {st.session_state.gold_premium}")
        st.metric("Dollar Adjustment", f"+ Rs {st.session_state.usd_adj}")
        st.metric("Final Dollar Rate", f"Rs {final_usd_rate:.2f}")

# -----------------------------
# 7. FOOTER
# -----------------------------
st.markdown("""
<div class="footer">
**Islam Jewellery** website shows approximate gold prices.<br>
Prices are updated based on market data and admin-set premium.<br><br>
⚠️ **Disclaimer:** Prices are indicative and may change anytime. Always verify with the shop before buying. Contact shop directly for confirmed gold rates.
</div>
""", unsafe_allow_html=True)
