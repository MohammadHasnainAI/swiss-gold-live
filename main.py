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
st.set_page_config(page_title="Islam Jewellery v38.0", page_icon="💎", layout="centered")

# 2. SESSION STATE INITIALIZATION (Moved to TOP to fix AttributeError)
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
if "selected_metal" not in st.session_state: st.session_state.selected_metal = "Gold"
if "publishing" not in st.session_state: st.session_state.publishing = False
if "confirm_reset_history" not in st.session_state: st.session_state.confirm_reset_history = False
if "confirm_reset_chart" not in st.session_state: st.session_state.confirm_reset_chart = False
if "last_api_call" not in st.session_state: st.session_state.last_api_call = 0
if "new_gold" not in st.session_state: st.session_state.new_gold = 0
if "new_silver" not in st.session_state: st.session_state.new_silver = 0
if "last_seen_update" not in st.session_state: st.session_state.last_seen_update = 0

# 3. HELPER FUNCTIONS
def clear_all_caches():
    """Clear all caches to ensure fresh data"""
    st.cache_data.clear()
    get_live_rates.clear()
    load_settings.clear()

# 4. CSS STYLES (Fixed Logo Clipping)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}

/* FIXED: Increased top padding to 4.5rem to stop logo cutting */
.block-container {padding-top: 4.5rem !important; padding-bottom: 1rem !important; max-width: 700px;}

.header-box {text-align:center; padding: 20px 0; margin-bottom:15px; margin-top: 0px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 12px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
.brand-title {font-size:2.2rem; font-weight:800; color:#d4af37; letter-spacing:1px; text-transform:uppercase; line-height: 1.2; margin-bottom: 8px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
.brand-subtitle {font-size:0.8rem; color:#fff; font-weight:500; letter-spacing:3px; text-transform:uppercase; opacity: 0.9;}
.price-card {background:#ffffff; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.04); border:1px solid #eef0f2; margin-bottom:8px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.sleep-badge {background-color:#eef2f6; color:#555; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.error-badge {background-color:#f8d7da; color:#721c24; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
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
</style>
""", unsafe_allow_html=True)

# 5. GITHUB CONNECTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    st.error(f"GitHub Connection Failed: {e}")

# 6. SETTINGS ENGINE
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

# 7. DATA ENGINE - HYBRID (TwelveData -> Yahoo)
@st.cache_data(ttl=60, show_spinner=False)
def get_live_rates():
    """
    1. TwelveData (Primary - Best Accuracy)
    2. Yahoo Finance (Backup - Unlimited)
    """
    
    # 1. Determine "Smart Cache" Duration
    tz_khi = pytz.timezone("Asia/Karachi")
    now_khi = datetime.now(tz_khi)
    current_hour = now_khi.hour
    
    # Smart Logic: Active hours 07:00 to 23:59
    is_active_hours = 7 <= current_hour <= 23
    
    debug_logs = []
    gold_price = 0.0
    silver_price = 0.0
    usd_rate = 0.0
    aed_rate = 0.0
    
    # --- PHASE 1: GOLD & SILVER ---
    
    # Attempt 1: TwelveData
    td_success = False
    try:
        if "TWELVE_DATA_KEY" in st.secrets:
            TD_KEY = st.secrets["TWELVE_DATA_KEY"]
            url_gold = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TD_KEY}"
            gold_res = requests.get(url_gold, timeout=5)
            
            if gold_res.status_code == 200:
                data = gold_res.json()
                if 'price' in data:
                    gold_price = float(data['price'])
                    td_success = True
                else:
                    debug_logs.append(f"TD Gold Limit: {data.get('message', 'Limit reached')}")
            else:
                debug_logs.append(f"TD Gold HTTP: {gold_res.status_code}")
                
            if td_success:
                url_slv = f"https://api.twelvedata.com/price?symbol=XAG/USD&apikey={TD_KEY}"
                slv_res = requests.get(url_slv, timeout=5)
                if slv_res.status_code == 200:
                    s_data = slv_res.json()
                    silver_price = float(s_data.get('price', 0))
    except Exception as e:
        debug_logs.append(f"TD Error: {str(e)}")
        td_success = False

    # Attempt 2: Yahoo Finance (Safe Backup)
    if not td_success:
        try:
            debug_logs.append("Trying Yahoo Backup...")
            g_tick = yf.Ticker("GC=F") 
            g_hist = g_tick.history(period="1d")
            if not g_hist.empty:
                gold_price = float(g_hist['Close'].iloc[-1])
            
            s_tick = yf.Ticker("SI=F")
            s_hist = s_tick.history(period="1d")
            if not s_hist.empty:
                silver_price = float(s_hist['Close'].iloc[-1])
            
            if gold_price > 0:
                debug_logs.append("Success: Used Yahoo Finance")
                
        except Exception as e:
            debug_logs.append(f"Yahoo Error: {str(e)}")

    # --- PHASE 2: CURRENCY ---
    try:
        if "CURR_KEY" in st.secrets:
            CURR_KEY = st.secrets["CURR_KEY"]
            url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
            curr_res = requests.get(url_curr, timeout=5)
            
            if curr_res.status_code == 200:
                c_data = curr_res.json()
                usd_rate = float(c_data.get('conversion_rates', {}).get('PKR', 0))
                aed_rate = float(c_data.get('conversion_rates', {}).get('AED', 0))
            else:
                debug_logs.append(f"Currency API Status: {curr_res.status_code}")
        else:
            debug_logs.append("Missing CURR_KEY")
    except Exception as e:
        debug_logs.append(f"Currency Exception: {str(e)}")

    return {
        "gold": gold_price,
        "silver": silver_price,
        "usd": usd_rate,
        "aed": aed_rate,
        "debug": debug_logs,
        "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
        "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S"),
        "active_mode": is_active_hours
    }

# 8. LOAD DATA
try:
    # DYNAMIC THROTTLE LOGIC (PAKISTAN TIME)
    current_ts = time.time()
    tz_khi = pytz.timezone("Asia/Karachi")
    cur_hour = datetime.now(tz_khi).hour
    
    # 7am - 11:59pm = Fast (90s), 12am - 6:59am = Slow (30m)
    wait_time = 90 if (7 <= cur_hour <= 23) else 1800
    
    if (current_ts - st.session_state.last_api_call) > wait_time:
        clear_all_caches()
        live_data = get_live_rates()
        st.session_state.last_api_call = current_ts
    else:
        live_data = get_live_rates()
except:
    live_data = {"gold": 0, "silver": 0, "usd": 0, "aed": 0, "debug": ["Crash"], "full_date": "Error", "active_mode": True}

try:
    settings = load_settings()
except:
    settings = {"gold_premium": 0, "silver_premium": 0, "last_update": 0}

# 9. SYNC SETTINGS TO STATE
st.session_state.new_gold = int(settings.get("gold_premium", 0))
st.session_state.new_silver = int(settings.get("silver_premium", 0))

# 10. AUTO-REFRESH CHECK
current_update_time = settings.get("last_update", 0)
if current_update_time > st.session_state.last_seen_update:
    if not st.session_state.get("is_admin_publishing", False):
        st.session_state.last_seen_update = current_update_time
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

# GOLD CARD
if gold_tola > 0:
    st.markdown(f"""
    <div class="price-card">
        {status_badge}
        <div class="big-price">Rs {gold_tola:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div class="stats-container">
            <div class="stat-box"><div class="stat-value">${gold_ounce:,.2f}</div><div class="stat-label">Ounce USD</div></div>
            <div class="stat-box"><div class="stat-value">Rs {usd_rate:.2f}</div><div class="stat-label">USD Rate</div></div>
            <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai/Tola</div></div>
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

if st.button("🔄 Refresh Rates", use_container_width=True):
    clear_all_caches()
    st.rerun()

# SILVER CARD
if silver_tola > 0:
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
        <div class="big-price">Rs {silver_tola:,.0f}</div>
        <div class="price-label">24K Silver Per Tola</div>
        <div class="stats-container">
            <div class="stat-box"><div class="stat-value">${silver_ounce:.2f}</div><div class="stat-label">Ounce USD</div></div>
            <div class="stat-box"><div class="stat-value">{live_data.get('time')}</div><div class="stat-label">Time</div></div>
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

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 13. ADMIN SECTION
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        password = st.text_input("Password", type="password", key="admin_pass")
        if st.button("🔓 Login", use_container_width=True, type="primary"):
            admin_pass = st.secrets.get("ADMIN_PASSWORD", "123123")
            if password == admin_pass:
                st.session_state.admin_auth = True
                clear_all_caches()
                st.rerun()
            else:
                st.error("Invalid password")

if st.session_state.admin_auth:
    st.markdown("---")
    st.subheader("⚙️ Admin Dashboard")
    
    # DEBUGGER
    with st.expander("🛠️ Connection Status (Debug)", expanded=True):
        if live_data.get("debug"):
            for log in live_data["debug"]:
                if "TD Gold Limit" in log:
                    st.warning(f"⚠️ {log}")
                elif "Success" in log:
                    st.success(f"✅ {log}")
                elif "Trying" in log:
                    st.info(f"ℹ️ {log}")
                else:
                    st.error(f"❌ {log}")
        else:
            st.success("✅ All APIs Connected Successfully")
    
    if st.button("🔴 Logout", key="logout"):
        st.session_state.admin_auth = False
        st.rerun()

    tabs = st.tabs(["Update Rates", "Stats", "History", "Charts"])
    
    # TAB 1: UPDATE
    with tabs[0]:
        st.info(f"Current Gold Premium: {int(st.session_state.new_gold)}")
        val_g = st.number_input("New Gold Premium", value=int(st.session_state.new_gold), step=500, key="g_in")
        st.session_state.new_gold = val_g
        
        st.info(f"Current Silver Premium: {int(st.session_state.new_silver)}")
        val_s = st.number_input("New Silver Premium", value=int(st.session_state.new_silver), step=50, key="s_in")
        st.session_state.new_silver = val_s

        if st.button("🚀 PUBLISH CHANGES", type="primary", use_container_width=True):
            if repo:
                st.session_state.publishing = True
                st.session_state.is_admin_publishing = True
                try:
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
                        
                        # Update manual.json
                        try:
                            c = repo.get_contents("manual.json")
                            repo.update_file(c.path, "Update", json.dumps(new_settings), c.sha)
                        except:
                            repo.create_file("manual.json", "Init", json.dumps(new_settings))
                            
                        # Update History (Safely)
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
                            "usd": fresh['usd']
                        })
                        if len(hist) > 60: hist = hist[-60:]
                        
                        try:
                            repo.update_file(hc.path, "Hist", json.dumps(hist), hc.sha)
                        except:
                            repo.create_file("history.json", "Init", json.dumps(hist))
                            
                        st.success("✅ Updated!")
                        time.sleep(1)
                        st.session_state.publishing = False
                        st.session_state.last_seen_update = new_settings["last_update"]
                        clear_all_caches()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.publishing = False
            else:
                st.error("GitHub Disconnected")

    # TAB 2: HISTORY (Fixed Crash)
    with tabs[2]:
        if st.button("🗑️ Reset History"):
            st.session_state.confirm_reset_history = True
            
        if st.session_state.confirm_reset_history:
            if st.button("✅ Confirm Delete"):
                if repo:
                    try:
                        hc = repo.get_contents("history.json")
                        repo.update_file(hc.path, "Reset", json.dumps([]), hc.sha)
                        st.success("Reset!")
                        st.session_state.confirm_reset_history = False
                    except:
                        st.error("Error resetting")
            if st.button("❌ Cancel"):
                st.session_state.confirm_reset_history = False

        try:
            if repo:
                hc = repo.get_contents("history.json")
                data = json.loads(hc.decoded_content.decode())
                if isinstance(data, list) and len(data) > 0:
                    st.dataframe(data)
                else:
                    st.info("No history found")
        except:
            st.info("History empty")

# 14. FOOTER
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
