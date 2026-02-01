import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery V13", page_icon="💎", layout="centered")

# ---------------------------------------------------------
# AUTO-REFRESH ENGINE (5 SECONDS)
# ---------------------------------------------------------
st_autorefresh(interval=5000, key="gold_refresh") 

# 2. HELPER FUNCTIONS
def update_premium(key, amount):
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] += amount

def manual_refresh():
    get_live_rates.clear()
    load_settings.clear()

# 3. DESIGN & CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding-top: 0rem !important; padding-bottom: 1rem !important; margin-top: -40px !important; max-width: 700px;}
.header-box {text-align:center; padding-bottom:5px; margin-bottom:10px; margin-top: 15px;}
.brand-title {font-size:1.8rem; font-weight:800; color:#111; letter-spacing:-0.5px; text-transform:uppercase; line-height: 1; margin-bottom: 2px;}
.brand-subtitle {font-size:0.65rem; color:#d4af37; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;}
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
.contact-btn:hover {opacity:0.9;}
.footer {background:#f1f3f5; padding:10px; border-radius: 10px; text-align:center; font-size:0.7rem; color:#666; margin-top:15px;}

/* Admin Dashboard Styles */
.login-card {background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); max-width: 400px; margin: 2rem auto; text-align: center; border-top: 4px solid #d4af37;}
.admin-title {font-size: 1.8rem; font-weight: 800; color: #d4af37; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 2px;}
.metric-card-pro {background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-bottom: 3px solid #d4af37; text-align: center;}
.metric-value-pro {font-size: 1.8rem; font-weight: 800; color: #1a1a1a; margin: 0.5rem 0;}
.metric-label-pro {color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;}
.control-box {background: #fafafa; border-radius: 16px; padding: 2rem; border: 1px solid #e0e0e0; margin-top: 1rem;}
.success-msg {background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;}
.error-msg {background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; margin: 1rem 0;}
.warning-banner {background: #fff3cd; color: #856404; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #ffc107; margin: 1rem 0; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

# 4. GITHUB CONNECTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    print(f"GitHub Error: {e}")

# 5. SETTINGS ENGINE
@st.cache_data(ttl=5, show_spinner=False)
def load_settings():
    default_settings = {"gold_premium": 0, "silver_premium": 0}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
        except:
            pass
    return default_settings

# 6. DATA ENGINE
@st.cache_data(ttl=120, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR: Secret Keys Missing"
    
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    try:
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals).json()
        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr).json()
        
        gold_price = 0
        silver_price = 0
        
        if "XAU/USD" in metal_res and "price" in metal_res["XAU/USD"]:
            gold_price = float(metal_res['XAU/USD']['price'])
        if "XAG/USD" in metal_res and "price" in metal_res["XAG/USD"]:
            silver_price = float(metal_res['XAG/USD']['price'])
            
        if gold_price == 0: gold_price = 2750.00
        if silver_price == 0: silver_price = 32.00 
        
        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return f"UNKNOWN ERROR: {str(e)}"

# 7. LOAD DATA
live_data = get_live_rates()
settings = load_settings()

if isinstance(live_data, str):
    st.warning(f"⚠️ {live_data}")
    live_data = {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline Mode", "full_date": "2024-01-01"}

if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)

# 8. CALCULATIONS
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# 9. COMPACT UI DISPLAY
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['gold']:,.0f}</div><div class="stat-label">Ounce</div></div>
        <div class="stat-box"><div class="stat-value">Rs {live_data['usd']:.2f}</div><div class="stat-label">Dollar</div></div>
        <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai</div></div>
    </div>
    <div style="font-size:0.6rem; color:#aaa; margin-top:8px; padding-top:5px; border-top:1px solid #eee;">
        Last Updated: <b>{live_data['time']}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# REFRESH BUTTON
if st.button("🔄 Check for New Gold Rate", use_container_width=True):
    manual_refresh()
    st.rerun()

# SILVER CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
    <div class="big-price">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['silver']:,.2f}</div><div class="stat-label">Ounce</div></div>
        <div class="stat-box"><div class="stat-value">{live_data['time']}</div><div class="stat-label">Updated</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 10. ADMIN DASHBOARD (COMPLETE WITH IMPORTS WORKING)
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "selected_metal" not in st.session_state:
    st.session_state.selected_metal = "Gold"
if "confirm_reset_history" not in st.session_state:
    st.session_state.confirm_reset_history = False
if "confirm_reset_chart" not in st.session_state:
    st.session_state.confirm_reset_chart = False

# Login Screen
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""
        <div class="login-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔐</div>
            <div class="admin-title">Admin Portal</div>
            <p style="color: #666; margin-bottom: 2rem;">Authorized Personnel Only</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password...")
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if password == "123123":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">⚠️ Invalid password</div>', unsafe_allow_html=True)

# Dashboard Screen
if st.session_state.admin_auth:
    st.markdown("---")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="admin-title" style="margin-bottom: 0;">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666; margin-top: 0;">Manage premium rates & analytics</p>', unsafe_allow_html=True)
    with col2:
        if st.button("🔴 Logout", type="secondary"):
            st.session_state.admin_auth = False
            st.rerun()
    
    tabs = st.tabs(["💰 Update Rates", "📊 Statistics", "📜 History", "📈 Charts"])
    
    # TAB 1: Update Rates
    with tabs[0]:
        st.markdown("### Select Metal")
        
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("🟡 GOLD", use_container_width=True, 
                        type="primary" if st.session_state.selected_metal == "Gold" else "secondary"):
                st.session_state.selected_metal = "Gold"
                st.rerun()
        
        with btn_cols[1]:
            if st.button("⚪ SILVER", use_container_width=True,
                        type="primary" if st.session_state.selected_metal == "Silver" else "secondary"):
                st.session_state.selected_metal = "Silver"
                st.rerun()
        
        if st.session_state.selected_metal == "Gold":
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### 🟡 Gold Premium Control")
            
            step = 500
            current = int(st.session_state.new_gold)
            
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 500", use_container_width=True):
                    st.session_state.new_gold = max(0, current - 500)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 500", use_container_width=True):
                    st.session_state.new_gold = current + 500
                    st.rerun()
            
            val = st.number_input("Gold Premium", value=current, step=step)
            st.session_state.new_gold = val
            
            calculated = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro"><div class="metric-label-pro">Premium</div><div class="metric-value-pro" style="color: #d4af37;">Rs {int(st.session_state.new_gold):,}</div></div>
                <div class="metric-card-pro"><div class="metric-label-pro">Final Rate</div><div class="metric-value-pro">Rs {calculated:,.0f}</div></div>
                <div class="metric-card-pro"><div class="metric-label-pro">USD</div><div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div></div>
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
                if st.button("➖ 50", use_container_width=True, key="s1"):
                    st.session_state.new_silver = max(0, current - 50)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 50", use_container_width=True, key="s2"):
                    st.session_state.new_silver = current + 50
                    st.rerun()
            
            val = st.number_input("Silver Premium", value=current, step=step, key="sil_in")
            st.session_state.new_silver = val
            
            calculated = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_silver
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;"><div class="metric-label-pro">Premium</div><div class="metric-value-pro" style="color: #666;">Rs {int(st.session_state.new_silver):,}</div></div>
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;"><div class="metric-label-pro">Final Rate</div><div class="metric-value-pro">Rs {calculated:,.0f}</div></div>
                <div class="metric-card-pro"><div class="metric-label-pro">USD</div><div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 PUBLISH RATE", type="primary", use_container_width=True):
            if repo:
                try:
                    new_settings = {"gold_premium": int(st.session_state.new_gold), "silver_premium": int(st.session_state.new_silver)}
                    
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, f"Update - {datetime.now().strftime('%H:%M')}", json.dumps(new_settings), contents.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
                    try:
                        h_content = repo.get_contents("history.json")
                        history = json.loads(h_content.decoded_content.decode())
                    except:
                        history = []
                    
                    history.append({
                        "date": live_data['full_date'],
                        "gold_pk": float(gold_tola),
                        "silver_pk": float(silver_tola),
                        "usd": float(live_data['usd'])
                    })
                    if len(history) > 60: history = history[-60:]
                    
                    try:
                        repo.update_file(h_content.path, f"Hist - {datetime.now().strftime('%H:%M')}", json.dumps(history), h_content.sha)
                    except:
                        repo.create_file("history.json", "Init", json.dumps(history))
                    
                    st.markdown('<div class="success-msg">✅ Published! Live in 5 seconds.</div>', unsafe_allow_html=True)
                    manual_refresh()
                except Exception as e:
                    st.markdown(f'<div class="error-msg">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ GitHub not connected</div>', unsafe_allow_html=True)
    
    # TAB 2: Statistics
    with tabs[1]:
        st.markdown("### Market Overview")
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.markdown(f'<div style="background: #1a1a1a; color: #d4af37; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #d4af37;"><div style="font-size: 2rem; margin-bottom: 0.5rem;">🟡</div><div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">Gold Premium</div><div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {int(st.session_state.new_gold):,}</div></div>', unsafe_allow_html=True)
        with stats_cols[1]:
            st.markdown(f'<div style="background: white; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #C0C0C0;"><div style="font-size: 2rem; margin-bottom: 0.5rem;">⚪</div><div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px;">Silver Premium</div><div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0; color: #666;">Rs {int(st.session_state.new_silver):,}</div></div>', unsafe_allow_html=True)
        with stats_cols[2]:
            st.markdown(f'<div style="background: linear-gradient(135deg, #d4af37 0%, #f4e5c2 100%); color: #1a1a1a; border-radius: 12px; padding: 1.5rem; text-align: center;"><div style="font-size: 2rem; margin-bottom: 0.5rem;">💵</div><div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">USD/PKR</div><div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {live_data["usd"]:.2f}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown(f'<div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #d4af37;"><h4 style="margin-top: 0; color: #1a1a1a;">🟡 Gold Details</h4><p style="margin: 0.5rem 0; color: #555;"><strong>Int\'l:</strong> ${live_data["gold"]:,.2f}/oz</p><p style="margin: 0.5rem 0; color: #555;"><strong>Tola:</strong> Rs {gold_tola:,.0f}</p><p style="margin: 0.5rem 0; color: #555;"><strong>Dubai:</strong> AED {gold_dubai_tola:,.0f}</p></div>', unsafe_allow_html=True)
        with detail_cols[1]:
            st.markdown(f'<div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #C0C0C0;"><h4 style="margin-top: 0; color: #1a1a1a;">⚪ Silver Details</h4><p style="margin: 0.5rem 0; color: #555;"><strong>Int\'l:</strong> ${live_data["silver"]:,.2f}/oz</p><p style="margin: 0.5rem 0; color: #555;"><strong>Tola:</strong> Rs {silver_tola:,.0f}</p><p style="margin: 0.5rem 0; color: #555;"><strong>Premium:</strong> Rs {int(st.session_state.new_silver)}</p></div>', unsafe_allow_html=True)
    
    # TAB 3: History WITH RESET
    with tabs[2]:
        st.markdown("### Rate History")
        
        reset_col1, reset_col2 = st.columns([3, 1])
        with reset_col1:
            st.caption("Last 60 records")
        with reset_col2:
            if st.button("🗑️ Reset All", type="secondary", key="reset_hist_btn"):
                st.session_state.confirm_reset_history = True
        
        if st.session_state.confirm_reset_history:
            st.markdown('<div class="warning-banner">⚠️ This will delete all history permanently!</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes, Delete", type="primary", key="confirm_yes_hist"):
                    if repo:
                        try:
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset history", json.dumps([]), h_content.sha)
                            st.session_state.confirm_reset_history = False
                            st.success("✅ History cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            with c2:
                if st.button("❌ Cancel", key="cancel_hist"):
                    st.session_state.confirm_reset_history = False
                    st.rerun()
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 0:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
                    df = df.rename(columns={'date': 'Date/Time', 'gold_pk': 'Gold (PKR)', 'silver_pk': 'Silver (PKR)', 'usd': 'USD Rate'})
                    st.dataframe(df.sort_values('Date/Time', ascending=False), use_container_width=True, hide_index=True)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export CSV", csv, f"rates_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                else:
                    st.info("📭 History is empty.")
        except:
            st.info("No history available yet.")
    
    # TAB 4: Charts WITH RESET & GOLD/SILVER SELECTOR
    with tabs[3]:
        st.markdown("### Price Trends")
        
        ctrl_col1, ctrl_col2 = st.columns([3, 1])
        with ctrl_col1:
            chart_metal = st.selectbox("Select Metal:", ["Gold", "Silver"], key="chart_selector")
        with ctrl_col2:
            if st.button("🗑️ Reset", type="secondary", key="reset_chart_btn"):
                st.session_state.confirm_reset_chart = True
        
        if st.session_state.confirm_reset_chart:
            st.markdown('<div class="warning-banner">⚠️ Delete all chart data?</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Delete", type="primary", key="confirm_yes_chart"):
                    if repo:
                        try:
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset chart data", json.dumps([]), h_content.sha)
                            st.session_state.confirm_reset_chart = False
                            st.success("✅ Data cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            with c2:
                if st.button("❌ Cancel", key="cancel_chart"):
                    st.session_state.confirm_reset_chart = False
                    st.rerun()
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 1:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df['gold_pk'] = pd.to_numeric(df['gold_pk'], errors='coerce')
                    df['silver_pk'] = pd.to_numeric(df['silver_pk'], errors='coerce')
                    
                    if chart_metal == "Gold":
                        y_col = 'gold_pk'
                        color = '#d4af37'
                        title = "Gold Rate Trend"
                    else:
                        y_col = 'silver_pk'
                        color = '#C0C0C0'
                        title = "Silver Rate Trend"
                    
                    chart = alt.Chart(df).mark_line(point=True, color=color, strokeWidth=3).encode(
                        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%d %b')),
                        y=alt.Y(f'{y_col}:Q', title='Rate (PKR)', scale=alt.Scale(zero=False)),
                        tooltip=[alt.Tooltip('date:T', title='Date', format='%Y-%m-%d %H:%M'), alt.Tooltip(f'{y_col}:Q', title=chart_metal, format='Rs ,.0f')]
                    ).properties(title=title, height=400)
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    stats_cols = st.columns(3)
                    stats_cols[0].metric("Highest", f"Rs {df[y_col].max():,.0f}")
                    stats_cols[1].metric("Lowest", f"Rs {df[y_col].min():,.0f}")
                    stats_cols[2].metric("Average", f"Rs {df[y_col].mean():,.0f}")
                else:
                    st.info("📊 Need at least 2 records.")
        except Exception as e:
            st.error(f"Chart error: {str(e)}")

# 11. FOOTER
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
