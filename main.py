import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
import time
import yfinance as yf

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery v28.0", page_icon="💎", layout="centered")

# 2. HELPER FUNCTIONS
def clear_all_caches():
    """Clear all caches to ensure fresh data"""
    st.cache_data.clear()
    get_live_rates.clear()
    load_settings.clear()

# 3. CSS STYLES
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
.block-container {padding-top: 0rem !important; padding-bottom: 1rem !important; margin-top: -10px !important; max-width: 700px;}
.header-box {text-align:center; padding: 20px 0; margin-bottom:15px; margin-top: 10px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
.brand-title {font-size:2.2rem; font-weight:800; color:#d4af37; letter-spacing:1px; text-transform:uppercase; line-height: 1.2; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
.brand-subtitle {font-size:0.8rem; color:#fff; font-weight:500; letter-spacing:3px; text-transform:uppercase; opacity: 0.9;}
.price-card {background:#ffffff; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.04); border:1px solid #eef0f2; margin-bottom:8px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; line-height:1; margin:4px 0; letter-spacing:-1px;}
.price-label {font-size:0.85rem; color:#666; font-weight:500;}
.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {background:#f1f3f5; border-radius:8px; padding:8px; text-align:center; border:1px solid #ebebeb; flex: 1;}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.55rem; color:#888; font-weight:600; text-transform:uppercase;}
.btn-grid {display: flex; gap: 8px; margin-top: 12px; justify-content: center;}
.contact-btn {flex: 1; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#222;}
.btn-whatsapp {background-color:#25D366;}
.footer {background:#f1f3f5; padding:10px; border-radius: 10px; text-align:center; font-size:0.7rem; color:#666; margin-top:15px;}
.login-card {background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 400px; margin: 2rem auto; text-align: center; border-top: 4px solid #d4af37;}
.admin-title {font-size: 1.8rem; font-weight: 800; color: #d4af37; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 2px;}
.metric-card-pro {background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-bottom: 3px solid #d4af37; text-align: center;}
.control-box {background: #fafafa; border-radius: 16px; padding: 2rem; border: 1px solid #e0e0e0; margin-top: 1rem;}
.success-msg {background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;}
.error-msg {background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0;}
.warning-banner {background: #fff3cd; color: #856404; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 1rem 0;}
.reset-container {background: #fff5f5; border: 2px solid #feb2b2; border-radius: 12px; padding: 1rem; margin: 1rem 0; text-align: center;}
.update-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #d4af37 0%, #f4e5c2 100%);
    color: #1a1a1a;
    padding: 15px 25px;
    border-radius: 12px;
    font-weight: 700;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    z-index: 9999;
    animation: slideIn 0.5s ease-out;
    border: 2px solid #d4af37;
}
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
.checking-indicator {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #1a1a1a;
    color: #d4af37;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    z-index: 9999;
    border: 1px solid #d4af37;
}
</style>
""", unsafe_allow_html=True)

# 4. GITHUB CONNECTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    st.error(f"GitHub Connection Failed: {e}")

# 5. SETTINGS ENGINE - OPTIMIZED CACHE
@st.cache_data(ttl=10, show_spinner=False)
def load_settings():
    """Load settings from GitHub with optimized cache"""
    default_settings = {"gold_premium": 0, "silver_premium": 0, "last_update": 0}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            data = json.loads(content.decoded_content.decode())
            for key in default_settings:
                data.setdefault(key, default_settings[key])
            return data
        except Exception as e:
            print(f"Load settings error: {e}")
            return default_settings
    return default_settings

# 6. DATA ENGINE - GOLD ONLY (SILVER MOVED TO YAHOO)
@st.cache_data(ttl=15, show_spinner=False)
def get_live_rates():
    """Get live market rates - Gold from API, Silver from Yahoo"""
    try:
        # GOLD: Use TwelveData (paid, reliable)
        if "TWELVE_DATA_KEY" in st.secrets:
            TD_KEY = st.secrets["TWELVE_DATA_KEY"]
            url_gold = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TD_KEY}"
            gold_res = requests.get(url_gold, timeout=10).json()
            gold_price = float(gold_res.get('price', 2750.0))
        else:
            gold_price = 2750.0
        
        # SILVER: Use Yahoo Finance (FREE, unlimited)
        try:
            silver_ticker = yf.Ticker("XAG-USD")
            silver_data = silver_ticker.history(period="1d", interval="1m")
            silver_price = float(silver_data['Close'].iloc[-1]) if not silver_data.empty else 32.0
        except:
            silver_price = 32.0
        
        # USD/PKR: Use ExchangeRate-API
        if "CURR_KEY" in st.secrets:
            CURR_KEY = st.secrets["CURR_KEY"]
            url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
            curr_res = requests.get(url_curr, timeout=10).json()
            usd_rate = float(curr_res.get('conversion_rates', {}).get('PKR', 278.0))
            aed_rate = float(curr_res.get('conversion_rates', {}).get('AED', 3.67))
        else:
            usd_rate, aed_rate = 278.0, 3.67
        
        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd": usd_rate,
            "aed": aed_rate,
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        st.error(f"API Error: {e} (Using safe fallback values)")
        return {
            "gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67,
            "time": "Error", 
            "full_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# 7. LOAD DATA WITH ERROR HANDLING
try:
    live_data = get_live_rates()
except:
    live_data = {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Error", "full_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

try:
    settings = load_settings()
except:
    settings = {"gold_premium": 0, "silver_premium": 0, "last_update": 0}

# 8. SESSION STATE MANAGEMENT
# Initialize with defaults if not exists
if "admin_auth" not in st.session_state: 
    st.session_state.admin_auth = False
if "selected_metal" not in st.session_state: 
    st.session_state.selected_metal = "Gold"
if "confirm_reset_history" not in st.session_state: 
    st.session_state.confirm_reset_history = False
if "confirm_reset_chart" not in st.session_state: 
    st.session_state.confirm_reset_chart = False
if "publishing" not in st.session_state:
    st.session_state.publishing = False
if "last_seen_update" not in st.session_state:
    st.session_state.last_seen_update = settings.get("last_update", 0)

# CRITICAL: Always sync premiums from settings (authoritative source)
st.session_state.new_gold = int(settings.get("gold_premium", 0))
st.session_state.new_silver = int(settings.get("silver_premium", 0))

# 9. UPDATE DETECTION WITH ANTI-RACE PROTECTION
current_update_time = settings.get("last_update", 0)

if current_update_time > st.session_state.last_seen_update:
    # Prevent self-triggering on admin's own publish
    if not st.session_state.get("is_admin_publishing", False):
        st.session_state.last_seen_update = current_update_time
        clear_all_caches()
        settings = load_settings()
        live_data = get_live_rates()
        st.session_state.show_update_notification = True

# 10. CALCULATIONS WITH VALIDATION
try:
    # Validate and convert to float
    gold_ounce = float(live_data.get('gold', 2750.0))
    silver_ounce = float(live_data.get('silver', 32.0))
    usd_rate = float(live_data.get('usd', 278.0))
    aed_rate = float(live_data.get('aed', 3.67))
    
    # Safety bounds check
    if not (2000 <= gold_ounce <= 4000):
        st.warning(f"Gold ounce ${gold_ounce:.2f} seems unusual. Using fallback.")
        gold_ounce = 2750.0
    
    # Get premiums from settings
    gold_premium = float(settings.get("gold_premium", 0))
    silver_premium = float(settings.get("silver_premium", 0))
    
    # Calculate prices
    gold_tola = ((gold_ounce / 31.1035) * 11.66 * usd_rate) + gold_premium
    silver_tola = ((silver_ounce / 31.1035) * 11.66 * usd_rate) + silver_premium
    gold_dubai_tola = (gold_ounce / 31.1035) * 11.66 * aed_rate
    
    # Ensure positive values
    gold_tola = max(0, gold_tola)
    silver_tola = max(0, silver_tola)
    gold_dubai_tola = max(0, gold_dubai_tola)
    
except Exception as e:
    st.error(f"Calculation error: {e}")
    gold_tola = silver_tola = gold_dubai_tola = 0
    gold_ounce, silver_ounce, usd_rate = 2750.0, 32.0, 278.0
    gold_premium, silver_premium = 0, 0

# 11. MAIN DISPLAY
st.markdown("""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${gold_ounce:,.0f}</div><div class="stat-label">Ounce USD</div></div>
        <div class="stat-box"><div class="stat-value">Rs {usd_rate:.2f}</div><div class="stat-label">USD Rate</div></div>
        <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai/Tola</div></div>
    </div>
    <div style="font-size:0.6rem; color:#aaa; margin-top:8px; padding-top:5px; border-top:1px solid #eee;">
        Data as of: <b>{live_data.get('full_date', 'Unknown')}</b>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Refresh Rates", use_container_width=True):
    clear_all_caches()
    st.rerun()

st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
    <div class="big-price">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${silver_ounce:.2f}</div><div class="stat-label">Ounce USD</div></div>
        <div class="stat-box"><div class="stat-value">{live_data.get('time', '--:--')}</div><div class="stat-label">Time</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 12. ADMIN DASHBOARD
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""<div class="login-card"><div style="font-size: 2.5rem; margin-bottom: 1rem;">🔐</div><div class="admin-title">Admin Portal</div><p style="color: #666; margin-bottom: 2rem;">Authorized Personnel Only</p></div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password...", key="admin_pass")
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if password == "123123":
                    st.session_state.admin_auth = True
                    clear_all_caches()
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">⚠️ Invalid password</div>', unsafe_allow_html=True)

if st.session_state.admin_auth:
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="admin-title" style="margin-bottom: 0;">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666; margin-top: 0;">Manage premium rates & analytics</p>', unsafe_allow_html=True)
    with col2:
        if st.button("🔴 Logout", type="secondary", key="logout_btn"):
            st.session_state.admin_auth = False
            st.session_state.publishing = False
            clear_all_caches()
            st.rerun()
    
    tabs = st.tabs(["💰 Update Rates", "📊 Statistics", "📜 History", "📈 Charts"])
    
    # TAB 1: Update Rates
    with tabs[0]:
        st.markdown("### Select Metal")
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("🟡 GOLD", use_container_width=True, type="primary" if st.session_state.selected_metal == "Gold" else "secondary"):
                st.session_state.selected_metal = "Gold"
                st.rerun()
        with btn_cols[1]:
            if st.button("⚪ SILVER", use_container_width=True, type="primary" if st.session_state.selected_metal == "Silver" else "secondary"):
                st.session_state.selected_metal = "Silver"
                st.rerun()
        
        if st.session_state.selected_metal == "Gold":
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### 🟡 Gold Premium Control")
            step = 500
            current = int(st.session_state.new_gold)
            
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 500", use_container_width=True, key="g_minus"):
                    st.session_state.new_gold = max(0, current - 500)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 500", use_container_width=True, key="g_plus"):
                    st.session_state.new_gold = current + 500
                    st.rerun()
            
            val = st.number_input("Gold Premium (Rs)", value=current, step=step, key="gold_input")
            st.session_state.new_gold = int(val)
            
            # FIXED: Get fresh data for accurate preview
            preview_rates = get_live_rates()
            preview_gold = ((preview_rates['gold'] / 31.1035) * 11.66 * preview_rates['usd']) + st.session_state.new_gold
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Premium</div><div style="font-size: 1.8rem; font-weight: 800; color: #d4af37;">Rs {int(st.session_state.new_gold):,}</div></div>
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Final Rate</div><div style="font-size: 1.8rem; font-weight: 800;">Rs {preview_gold:,.0f}</div></div>
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">USD/PKR</div><div style="font-size: 1.4rem; font-weight: 800;">Rs {preview_rates['usd']:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="control-box">',
