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
from streamlit_autorefresh import st_autorefresh

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery v51.0", page_icon="💎", layout="centered")

# 2. AUTO-REFRESH LOGIC (20 SECONDS AS REQUESTED)
st_autorefresh(interval=20000, limit=None, key="gold_sync")

# 3. SESSION STATE
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
if "selected_metal" not in st.session_state: st.session_state.selected_metal = "Gold"
if "publishing" not in st.session_state: st.session_state.publishing = False
if "confirm_reset_history" not in st.session_state: st.session_state.confirm_reset_history = False
if "confirm_reset_chart" not in st.session_state: st.session_state.confirm_reset_chart = False
if "last_api_call" not in st.session_state: st.session_state.last_api_call = 0
if "last_seen_update" not in st.session_state: st.session_state.last_seen_update = 0
if "new_gold" not in st.session_state: st.session_state.new_gold = 0
if "new_silver" not in st.session_state: st.session_state.new_silver = 0

# 4. HELPER FUNCTIONS
def clear_all_caches():
    st.cache_data.clear()
    get_live_rates.clear()
    load_settings.clear()

# 5. CSS STYLES
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}

.block-container {
    padding-top: 1rem !important; 
    padding-bottom: 1rem !important; 
    max-width: 700px;
}
header[data-testid="stHeader"] {background-color: transparent;}

/* HEADER */
.header-box {
    text-align:center; 
    padding: 25px 0; 
    margin-bottom:15px; 
    margin-top: -20px;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
    border-radius: 12px; 
    color: white; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.brand-title {font-size:2.2rem; font-weight:800; color:#d4af37; letter-spacing:1px; text-transform:uppercase; line-height: 1.1; margin-bottom: 5px;}
.brand-subtitle {font-size:0.8rem; color:#fff; font-weight:500; letter-spacing:3px; text-transform:uppercase; opacity: 0.8;}

/* STATS BOX */
.price-card {background:#ffffff; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.04); border:1px solid #eef0f2; margin-bottom:8px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.sleep-badge {background-color:#eef2f6; color:#555; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.error-badge {background-color:#f8d7da; color:#721c24; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; line-height:1; margin:4px 0; letter-spacing:-1px;}
.price-label {font-size:0.85rem; color:#666; font-weight:500; margin-bottom: 10px;}

.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {background:#f1f3f5; border-radius:8px; padding:8px; text-align:center; border:1px solid #ebebeb; flex: 1; display: flex; flex-direction: column; justify-content: center;}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37; line-height: 1.2;}
.stat-label {font-size:0.55rem; color:#444; font-weight:700; text-transform:uppercase; margin-top: 2px;}
.stat-time {font-size:0.5rem; color:#999; font-weight:500; margin-top: 2px;}

.btn-grid {display: flex; gap: 8px; margin-top: 12px; justify-content: center;}
.contact-btn {flex: 1; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#222;}
.btn-whatsapp {background-color:#25D366;}
.footer {background:#f1f3f5; padding:10px; border-radius: 10px; text-align:center; font-size:0.7rem; color:#666; margin-top:15px;}

/* Admin Styles */
.login-card {background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 400px; margin: 2rem auto; text-align: center; border-top: 4px solid #d4af37;}
.admin-title {font-size: 1.8rem; font-weight: 800; color: #d4af37; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 2px;}
.metric-card-pro {background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-bottom: 3px solid #d4af37; text-align: center;}
.control-box {background: #fafafa; border-radius: 16px; padding: 2rem; border: 1px solid #e0e0e0; margin-top: 1rem;}
.success-msg {background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;}
.error-msg {background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0;}
.reset-container {background: #fff5f5; border: 2px solid #feb2b2; border-radius: 12px; padding: 1rem; margin: 1rem 0; text-align: center;}
</style>
""", unsafe_allow_html=True)

# 6. GITHUB CONNECTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    st.error(f"GitHub Connection Failed: {e}")

# 7. SETTINGS ENGINE
@st.cache_data(ttl=10, show_spinner=False)
def load_settings():
    default_settings = {"gold_premium": 0, "silver_premium": 0, "last_update": 0}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            data = json.loads(content.decoded_content.decode())
            for key in default_settings:
                data.setdefault(key, default_settings[key])
            return data
        except Exception:
            return default_settings
    return default_settings

# 8. DATA ENGINE (HIGH SPEED 15s Cache)
@st.cache_data(ttl=15, show_spinner=False)
def get_live_rates():
    tz_khi = pytz.timezone("Asia/Karachi")
    now_khi = datetime.now(tz_khi)
    current_hour = now_khi.hour
    is_active_hours = 7 <= current_hour <= 23
    debug_logs = []
    
    # Fake Browser Header to prevent 429 Errors
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Initialize Variables
    gold_price = 0.0
    silver_price = 0.0
    usd_rate = 0.0
    aed_rate = 0.0
    
    # Source Trackers
    src_gold = "OFFLINE"
    src_silver = "OFFLINE"
    src_usd = "OFFLINE"
    
    # --- 1. GOLD STRATEGY (Priority: TwelveData -> Yahoo) ---
    try:
        if "TWELVE_DATA_KEY" in st.secrets:
            TD_KEY = st.secrets["TWELVE_DATA_KEY"]
            url_gold = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TD_KEY}"
            gold_res = requests.get(url_gold, headers=headers, timeout=5) # Added headers
            if gold_res.status_code == 200:
                data = gold_res.json()
                if 'price' in data:
                    gold_price = float(data['price'])
                    src_gold = "TwelveData"
                else:
                    debug_logs.append(f"TD Gold Limit: {data.get('message')}")
    except Exception as e:
        debug_logs.append(f"TD Gold Error: {str(e)}")

    if gold_price == 0:
        try:
            g_tick = yf.Ticker("XAUUSD=X")
            g_hist = g_tick.history(period="1d")
            if not g_hist.empty:
                gold_price = float(g_hist['Close'].iloc[-1])
                src_gold = "Yahoo Finance"
        except Exception as e:
            debug_logs.append(f"Yahoo Gold Error: {str(e)}")

    # --- 2. SILVER STRATEGY (Priority: Yahoo -> TwelveData) ---
    try:
        s_tick = yf.Ticker("XAGUSD=X")
        s_hist = s_tick.history(period="1d")
        if not s_hist.empty:
            silver_price = float(s_hist['Close'].iloc[-1])
            src_silver = "Yahoo Finance"
    except Exception as e:
        debug_logs.append(f"Yahoo Silver Error: {str(e)}")

    if silver_price == 0:
        try:
            if "TWELVE_DATA_KEY" in st.secrets:
                TD_KEY = st.secrets["TWELVE_DATA_KEY"]
                url_slv = f"https://api.twelvedata.com/price?symbol=XAG/USD&apikey={TD_KEY}"
                slv_res = requests.get(url_slv, headers=headers, timeout=5) # Added headers
                if slv_res.status_code == 200:
                    s_data = slv_res.json()
                    if 'price' in s_data:
                        silver_price = float(s_data['price'])
                        src_silver = "TwelveData"
        except Exception as e:
            debug_logs.append(f"TD Silver Error: {str(e)}")

    # --- 3. CURRENCY STRATEGY (Priority: Yahoo -> ExchangeRateAPI) ---
    try:
        c_tick = yf.Ticker("PKR=X")
        c_hist = c_tick.history(period="1d")
        if not c_hist.empty:
            usd_rate = float(c_hist['Close'].iloc[-1])
            aed_rate = 3.67 
            src_usd = "Yahoo Finance"
    except Exception as e:
        debug_logs.append(f"Yahoo USD Error: {str(e)}")

    if usd_rate == 0:
        try:
            if "CURR_KEY" in st.secrets:
                CURR_KEY = st.secrets["CURR_KEY"]
                url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
                curr_res = requests.get(url_curr, headers=headers, timeout=5) # Added headers
                if curr_res.status_code == 200:
                    c_data = curr_res.json()
                    usd_rate = float(c_data.get('conversion_rates', {}).get('PKR', 0))
                    aed_rate = float(c_data.get('conversion_rates', {}).get('AED', 0))
                    src_usd = "ExchangeRate-API"
        except Exception as e:
            debug_logs.append(f"Currency Backup Error: {str(e)}")

    return {
        "gold": gold_price, "silver": silver_price, "usd": usd_rate, "aed": aed_rate,
        "src_gold": src_gold, "src_silver": src_silver, "src_usd": src_usd,
        "debug": debug_logs,
        "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M:%S %p"),
        "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S"),
        "active_mode": is_active_hours
    }

# 9. LOAD DATA
try:
    current_ts = time.time()
    tz_khi = pytz.timezone("Asia/Karachi")
    cur_hour = datetime.now(tz_khi).hour
    wait_time = 90 if (7 <= cur_hour <= 23) else 1800
    
    # In High Speed mode, we just check the cache timestamp
    live_data = get_live_rates()
except:
    live_data = {"gold": 0, "silver": 0, "usd": 0, "aed": 0, "src_gold": "ERR", "src_silver": "ERR", "src_usd": "ERR", "debug": ["Crash"], "full_date": "Error", "active_mode": True}

try:
    settings = load_settings()
except:
    settings = {"gold_premium": 0, "silver_premium": 0, "last_update": 0}

# 10. SYNC AND AUTO-UPDATE CHECK
st.session_state.new_gold = int(settings.get("gold_premium", 0))
st.session_state.new_silver = int(settings.get("silver_premium", 0))

if settings.get("last_update", 0) > st.session_state.last_seen_update:
    if not st.session_state.get("is_admin_publishing", False):
        st.session_state.last_seen_update = settings.get("last_update", 0)
        clear_all_caches()
        st.rerun()

# 11. CALCULATIONS
gold_ounce = float(live_data.get('gold', 0))
silver_ounce = float(live_data.get('silver', 0))
usd_rate = float(live_data.get('usd', 0))
aed_rate = float(live_data.get('aed', 0))
gold_premium = float(settings.get("gold_premium", 0))
silver_premium = float(settings.get("silver_premium", 0))

if gold_ounce > 0 and usd_rate > 0:
    gold_tola = ((gold_ounce / 31.1035) * 11.66 * usd_rate) + gold_premium
    gold_dubai_tola = (gold_ounce / 31.1035) * 11.66 * aed_rate
else:
    gold_tola = 0
    gold_dubai_tola = 0

if silver_ounce > 0 and usd_rate > 0:
    silver_tola = ((silver_ounce / 31.1035) * 11.66 * usd_rate) + silver_premium
else:
    silver_tola = 0

# 12. DISPLAY
st.markdown("""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

is_active = live_data.get('active_mode', True)
status_badge = '<div class="live-badge">● GOLD LIVE</div>' if is_active else '<div class="sleep-badge">☾ NIGHT MODE</div>'
update_time = live_data.get('time')

# Gold Card
if gold_tola > 0:
    st.markdown(f"""
    <div class="price-card">
        {status_badge}
        <div class="big-price">Rs {gold_tola:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">${gold_ounce:,.2f}</div>
                <div class="stat-label">Ounce USD</div>
                <div class="stat-time">🕒 {update_time}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Rs {usd_rate:.2f}</div>
                <div class="stat-label">USD Rate</div>
                <div class="stat-time">🕒 {update_time}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">AED {gold_dubai_tola:,.0f}</div>
                <div class="stat-label">Dubai/Tola</div>
                <div class="stat-time">🕒 {update_time}</div>
            </div>
        </div>
        <div style="font-size:0.6rem; color:#aaa; margin-top:8px;">Data as of: <b>{live_data.get('full_date')}</b></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card" style="border-left: 5px solid #dc3545;">
        <div class="error-badge">● DISCONNECTED</div>
        <div class="big-price" style="color:#dc3545; font-size: 1.8rem;">MARKET OFFLINE</div>
        <div class="price-label">Live data unavailable. Do not trade.</div>
        <div style="font-size:0.6rem; color:#aaa; margin-top:8px;">Last check: <b>{live_data.get('full_date')}</b></div>
    </div>
    """, unsafe_allow_html=True)

# Silver Card
if silver_tola > 0:
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
        <div class="big-price">Rs {silver_tola:,.0f}</div>
        <div class="price-label">24K Silver Per Tola</div>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">${silver_ounce:.2f}</div>
                <div class="stat-label">Ounce USD</div>
                <div class="stat-time">🕒 {update_time}</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{live_data.get('time')}</div>
                <div class="stat-label">Time</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card" style="border-left: 5px solid #dc3545;">
        <div class="error-badge">● DISCONNECTED</div>
        <div class="big-price" style="color:#dc3545; font-size: 1.5rem;">SILVER OFFLINE</div>
    </div>
    """, unsafe_allow_html=True)

# REFRESH BUTTON
if st.button("🔄 Refresh Rates", use_container_width=True):
    clear_all_caches()
    st.rerun()

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 13. ADMIN SECTION
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""<div class="login-card"><div style="font-size: 2.5rem; margin-bottom: 1rem;">🔐</div><div class="admin-title">Admin Portal</div><p style="color: #666; margin-bottom: 2rem;">Authorized Personnel Only</p></div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password...", key="admin_pass")
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                admin_pass = st.secrets.get("ADMIN_PASSWORD", "123123")
                if password == admin_pass:
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
            clear_all_caches()
            st.rerun()
    
    # NEW: SOURCE MONITOR
    with st.expander("📡 Live Source Monitor", expanded=True):
        sc1, sc2, sc3 = st.columns(3)
        
        def get_color(src):
            if "TwelveData" in src: return "#e3f2fd" # Blue
            if "Yahoo" in src: return "#e8f5e9" # Green
            return "#ffebee" # Red/Error
            
        with sc1:
            st.markdown(f'<div style="text-align:center; padding:10px; border-radius:8px; background:{get_color(live_data["src_gold"])};"><b>🟡 Gold</b><br>{live_data["src_gold"]}</div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div style="text-align:center; padding:10px; border-radius:8px; background:{get_color(live_data["src_silver"])};"><b>⚪ Silver</b><br>{live_data["src_silver"]}</div>', unsafe_allow_html=True)
        with sc3:
            st.markdown(f'<div style="text-align:center; padding:10px; border-radius:8px; background:{get_color(live_data["src_usd"])};"><b>💵 USD</b><br>{live_data["src_usd"]}</div>', unsafe_allow_html=True)

    # DEBUGGER
    with st.expander("🛠️ Debug Logs", expanded=False):
        if live_data.get("debug"):
            for log in live_data["debug"]:
                if "TD Gold Limit" in log:
                    st.warning(f"⚠️ {log}")
                elif "Success" in log:
                    st.success(f"✅ {log}")
                elif "Trying" in log:
                    st.info(f"ℹ️ {log}")
                elif "Used Backup" in log:
                    st.warning(f"🔄 {log}")
                else:
                    st.error(f"❌ {log}")
        else:
            st.success("✅ Clean run (No errors)")

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
            
            val = st.number_input("Gold Premium", value=current, step=step, key="gold_input")
            st.session_state.new_gold = int(val)
            
            # Preview
            preview_gold = ((gold_ounce / 31.1035) * 11.66 * usd_rate) + st.session_state.new_gold
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Premium</div><div style="font-size: 1.8rem; font-weight: 800; color: #d4af37;">Rs {int(st.session_state.new_gold):,}</div></div>
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Final Rate</div><div style="font-size: 1.8rem; font-weight: 800;">Rs {preview_gold:,.0f}</div></div>
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">USD</div><div style="font-size: 1.4rem; font-weight: 800;">Rs {usd_rate:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### ⚪ Silver Premium Control")
            step = 50
            current = int(st.session_state.new_silver)
            
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 50", use_container_width=True, key="s_minus"):
                    st.session_state.new_silver = max(0, current - 50)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 50", use_container_width=True, key="s_plus"):
                    st.session_state.new_silver = current + 50
                    st.rerun()
            
            val = st.number_input("Silver Premium", value=current, step=step, key="silver_input")
            st.session_state.new_silver = int(val)
            
            # Preview
            preview_silver = ((silver_ounce / 31.1035) * 11.66 * usd_rate) + st.session_state.new_silver
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Premium</div><div style="font-size: 1.8rem; font-weight: 800; color: #666;">Rs {int(st.session_state.new_silver):,}</div></div>
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">Final Rate</div><div style="font-size: 1.8rem; font-weight: 800;">Rs {preview_silver:,.0f}</div></div>
                <div class="metric-card-pro"><div style="color: #666; font-size: 0.75rem; text-transform: uppercase;">USD</div><div style="font-size: 1.4rem; font-weight: 800;">Rs {usd_rate:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # PUBLISH BUTTON
        publish_disabled = st.session_state.get("publishing", False)
        if publish_disabled:
            st.warning("⏳ Publishing... Please wait")
        
        if st.button("🚀 PUBLISH RATE", type="primary", use_container_width=True, disabled=publish_disabled):
            if repo and not publish_disabled:
                st.session_state.publishing = True
                st.session_state.is_admin_publishing = True
                try:
                    # CRITICAL: Get FRESH live rates
                    get_live_rates.clear()
                    fresh = get_live_rates()
                    
                    if fresh['gold'] == 0 or fresh['usd'] == 0:
                        st.error("❌ Cannot publish: APIs are offline.")
                        st.session_state.publishing = False
                    else:
                        c_gold = ((fresh['gold'] / 31.1035) * 11.66 * fresh['usd']) + int(st.session_state.new_gold)
                        c_silver = ((fresh['silver'] / 31.1035) * 11.66 * fresh['usd']) + int(st.session_state.new_silver)
                        
                        new_settings = {
                            "gold_premium": int(st.session_state.new_gold), 
                            "silver_premium": int(st.session_state.new_silver),
                            "last_update": int(time.time())
                        }
                        
                        try:
                            c = repo.get_contents("manual.json")
                            repo.update_file(c.path, "Update", json.dumps(new_settings), c.sha)
                        except:
                            repo.create_file("manual.json", "Init", json.dumps(new_settings))
                            
                        # Update History
                        try:
                            hc = repo.get_contents("history.json")
                            hist_data = json.loads(hc.decoded_content.decode())
                            hist = hist_data if isinstance(hist_data, list) else []
                        except:
                            hist = []
                        
                        hist.append({
                            "date": fresh['full_date'],
                            "gold_pk": c_gold,
                            "silver_pk": c_silver,
                            "gold_ounce": fresh['gold'],
                            "silver_ounce": fresh['silver'],
                            "usd": fresh['usd']
                        })
                        if len(hist) > 60: hist = hist[-60:]
                        
                        try:
                            repo.update_file(hc.path, "Hist", json.dumps(hist), hc.sha)
                        except:
                            repo.create_file("history.json", "Init", json.dumps(hist))
                            
                        st.success("✅ Updated! Syncing all users...")
                        time.sleep(1)
                        st.session_state.publishing = False
                        st.session_state.last_seen_update = new_settings["last_update"]
                        clear_all_caches()
                        st.rerun()
                        
                except Exception as e:
                    st.session_state.publishing = False
                    st.markdown(f'<div class="error-msg">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ GitHub not connected</div>', unsafe_allow_html=True)
    
    # TAB 2: Statistics
    with tabs[1]:
        st.markdown("### Market Overview")
        st.info(f"Gold Ounce: ${gold_ounce:,.2f} | USD/PKR: {usd_rate:.2f} | Premium Gold: Rs {int(gold_premium):,}")
        
        stats_cols = st.columns(3)
        with stats_cols[0]:
            st.markdown(f'<div style="background: #1a1a1a; color: #d4af37; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #d4af37;"><div style="font-size: 2rem;">🟡</div><div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; margin-top: 0.5rem;">Gold Premium</div><div style="font-size: 1.8rem; font-weight: 800;">Rs {int(gold_premium):,}</div></div>', unsafe_allow_html=True)
        with stats_cols[1]:
            st.markdown(f'<div style="background: white; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #C0C0C0;"><div style="font-size: 2rem;">⚪</div><div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;">Silver Premium</div><div style="font-size: 1.8rem; font-weight: 800; color: #666;">Rs {int(silver_premium):,}</div></div>', unsafe_allow_html=True)
        with stats_cols[2]:
            st.markdown(f'<div style="background: linear-gradient(135deg, #d4af37 0%, #f4e5c2 100%); color: #1a1a1a; border-radius: 12px; padding: 1.5rem; text-align: center;"><div style="font-size: 2rem;">💵</div><div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; margin-top: 0.5rem;">USD/PKR</div><div style="font-size: 1.8rem; font-weight: 800;">Rs {usd_rate:.2f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Price Breakdown
        st.markdown("### Price Calculation")
        calc_cols = st.columns(2)
        
        with calc_cols[0]:
            base_gold = ((gold_ounce/31.1035)*11.66*usd_rate)
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #d4af37; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h4 style="margin-top: 0; color: #1a1a1a; margin-bottom: 1rem;">🟡 Gold</h4>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Ounce:</strong> ${gold_ounce:,.2f}</p>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Base:</strong> Rs {base_gold:,.0f}</p>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Premium:</strong> Rs {int(gold_premium):,}</p>
                <hr style="border: 1px solid #eee;">
                <p style="margin: 0.3rem 0; color: #d4af37; font-size: 1.1rem; font-weight: bold;">FINAL: Rs {gold_tola:,.0f}</p>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Dubai:</strong> AED {gold_dubai_tola:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with calc_cols[1]:
            base_silver = ((silver_ounce/31.1035)*11.66*usd_rate)
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #C0C0C0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h4 style="margin-top: 0; color: #1a1a1a; margin-bottom: 1rem;">⚪ Silver</h4>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Ounce:</strong> ${silver_ounce:.2f}</p>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Base:</strong> Rs {base_silver:,.0f}</p>
                <p style="margin: 0.3rem 0; color: #555; font-size: 0.9rem;"><strong>Premium:</strong> Rs {int(silver_premium):,}</p>
                <hr style="border: 1px solid #eee;">
                <p style="margin: 0.3rem 0; color: #666; font-size: 1.1rem; font-weight: bold;">FINAL: Rs {silver_tola:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 3: HISTORY
    with tabs[2]:
        st.markdown("### 📜 Rate History Log")
        
        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.caption(f"Last 60 records")
        with header_cols[1]:
            if st.button("🗑️ Reset History", type="secondary", key="reset_hist_btn"):
                st.session_state.confirm_reset_history = True
        
        if st.session_state.confirm_reset_history:
            st.markdown('<div class="reset-container">', unsafe_allow_html=True)
            st.markdown("⚠️ **Warning:** This will permanently delete all history records!")
            conf_cols = st.columns(2)
            with conf_cols[0]:
                if st.button("✅ Yes, Delete All", type="primary", key="confirm_hist_yes", use_container_width=True):
                    if repo:
                        try:
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset history", json.dumps([]), h_content.sha)
                            st.session_state.confirm_reset_history = False
                            st.success("✅ History cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("GitHub not connected")
            with conf_cols[1]:
                if st.button("❌ Cancel", key="cancel_hist", use_container_width=True):
                    st.session_state.confirm_reset_history = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 0:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    column_mapping = {
                        'date': 'Date/Time',
                        'gold_pk': 'Gold PKR',
                        'silver_pk': 'Silver PKR',
                        'gold_ounce': 'Gold Oz ($)',
                        'silver_ounce': 'Silver Oz ($)',
                        'usd': 'USD Rate'
                    }
                    
                    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
                    expected_cols = ['Date/Time', 'Gold Oz ($)', 'Gold PKR', 'Silver Oz ($)', 'Silver PKR', 'USD Rate']
                    for col in expected_cols:
                        if col not in df.columns:
                            df[col] = 0
                    
                    df = df[expected_cols]
                    
                    st.dataframe(df.sort_values('Date/Time', ascending=False), use_container_width=True, hide_index=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export CSV", csv, f"history_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                else:
                    st.info("📭 No history records found.")
            else:
                st.error("❌ GitHub not connected")
        except Exception as e:
            st.info(f"📭 History empty or error: {str(e)}")
    
    # TAB 4: CHARTS
    with tabs[3]:
        st.markdown("### 📈 Price Trends")
        
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
        
        with ctrl_col1:
            chart_metal = st.selectbox("Select Metal:", ["Gold", "Silver"], key="chart_sel")
        
        with ctrl_col2:
            chart_type = st.selectbox("Chart Type:", ["Line", "Area"], key="type_sel")
        
        with ctrl_col3:
            if st.button("🗑️ Reset", type="secondary", key="reset_chart"):
                st.session_state.confirm_reset_chart = True
        
        if st.session_state.confirm_reset_chart:
            st.markdown('<div class="reset-container">', unsafe_allow_html=True)
            st.markdown("⚠️ **Warning:** Delete all chart data?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Delete", type="primary", key="confirm_chart_yes", use_container_width=True):
                    if repo:
                        try:
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset", json.dumps([]), h_content.sha)
                            st.session_state.confirm_reset_chart = False
                            st.success("✅ Cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Not connected")
            with c2:
                if st.button("❌ Cancel", key="cancel_chart", use_container_width=True):
                    st.session_state.confirm_reset_chart = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 1:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df['gold_pk'] = pd.to_numeric(df.get('gold_pk', 0), errors='coerce')
                    df['silver_pk'] = pd.to_numeric(df.get('silver_pk', 0), errors='coerce')
                    df = df.dropna(subset=['date'])
                    
                    if chart_metal == "Gold":
                        df_chart = df.dropna(subset=['gold_pk'])
                        y_col = 'gold_pk'
                        color = '#d4af37'
                        title = "Gold Price History"
                    else:
                        df_chart = df.dropna(subset=['silver_pk'])
                        y_col = 'silver_pk'
                        color = '#71797E'
                        title = "Silver Price History"
                    
                    if len(df_chart) < 2:
                        st.info("📊 Not enough data points.")
                    else:
                        base = alt.Chart(df_chart).encode(
                            x=alt.X('date:T', title='Date', axis=alt.Axis(format='%d %b %H:%M')),
                            y=alt.Y(f'{y_col}:Q', title='Price (PKR)', scale=alt.Scale(zero=False)),
                            tooltip=[
                                alt.Tooltip('date:T', title='Date', format='%Y-%m-%d %H:%M'),
                                alt.Tooltip(f'{y_col}:Q', title='Rate', format='Rs ,.0f')
                            ]
                        )
                        
                        if chart_type == "Area":
                            chart = (base.mark_area(color=color, opacity=0.3) + 
                                    base.mark_line(color=color, strokeWidth=3) + 
                                    base.mark_point(filled=True, color=color, size=60, stroke='white', strokeWidth=2))
                        else:
                            chart = (base.mark_line(color=color, strokeWidth=3) + 
                                    base.mark_point(filled=True, color=color, size=60, stroke='white', strokeWidth=2))
                        
                        final_chart = chart.properties(
                            title=title,
                            height=450
                        ).configure_view(
                            strokeWidth=0,
                            fill='white'
                        ).configure_axis(
                            gridColor='#f0f0f0',
                            labelFontSize=12,
                            titleFontSize=14
                        ).configure_title(
                            fontSize=16,
                            fontWeight=800,
                            anchor='middle'
                        )
                        
                        st.altair_chart(final_chart, use_container_width=True)
                        
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("📈 High", f"Rs {df_chart[y_col].max():,.0f}")
                        c2.metric("📉 Low", f"Rs {df_chart[y_col].min():,.0f}")
                        c3.metric("📊 Avg", f"Rs {df_chart[y_col].mean():,.0f}")
                        c4.metric("📝 Count", len(df_chart))
                else:
                    st.info("📊 Need 2+ records.")
        except Exception as e:
            st.error(f"Chart error: {str(e)}")

# 14. FOOTER
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
