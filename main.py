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

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Islam Jewellery Pro", page_icon="💎", layout="centered")

# ---------------------------------------------------------
# AUTO-REFRESH ENGINE (Runs first to guarantee updates)
# ---------------------------------------------------------
# Refreshes every 5 seconds for everyone
st_autorefresh(interval=5000, key="global_refresh")

# 2. CSS STYLING
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

.control-box {background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 15px; margin-bottom: 15px;}
.closed-card {background:#ffffff; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(220,38,38,0.05); border:2px solid #fee2e2; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

# 3. GITHUB CONNECTION & HELPER FUNCTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    st.error(f"GitHub Error: {e}")

# --- THE FIX: ROBUST SAVE FUNCTION ---
def save_to_github(filename, data, message="Update"):
    """Safely saves data to GitHub handling the SHA error automatically."""
    if not repo: return False
    try:
        # Try to get existing file to get its SHA
        contents = repo.get_contents(filename)
        repo.update_file(contents.path, message, json.dumps(data), contents.sha)
    except:
        # If file doesn't exist, create it
        repo.create_file(filename, "Init", json.dumps(data))
    return True

# 4. DATA ENGINE
@st.cache_data(ttl=120, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return {"gold": 2750, "silver": 32, "usd": 278, "aed": 3.67, "time": "Demo"}
    try:
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={st.secrets['TWELVE_DATA_KEY']}"
        metal_res = requests.get(url_metals, timeout=5).json()
        
        url_curr = f"https://v6.exchangerate-api.com/v6/{st.secrets['CURR_KEY']}/latest/USD"
        curr_res = requests.get(url_curr, timeout=5).json()
        
        gold_price = float(metal_res.get('XAU/USD', {}).get('price', 2750.0))
        silver_price = float(metal_res.get('XAG/USD', {}).get('price', 32.0))
        
        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline"}

# 5. SETTINGS ENGINE
@st.cache_data(ttl=1, show_spinner=False)
def get_settings():
    default = {"gold_premium": 0, "silver_premium": 0, "gold_market": "OPEN", "silver_market": "OPEN"}
    try:
        if repo:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
    except:
        pass
    return default

# 6. INITIALIZE STATE
live_data = get_live_rates()
settings = get_settings()

if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)
if "gold_market_status" not in st.session_state: st.session_state.gold_market_status = settings.get("gold_market", "OPEN")
if "silver_market_status" not in st.session_state: st.session_state.silver_market_status = settings.get("silver_market", "OPEN")
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
if "selected_metal" not in st.session_state: st.session_state.selected_metal = "Gold"

# 7. CALCULATIONS
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# 8. DISPLAY HEADER
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# 9. GOLD CARD
if settings.get("gold_market", "OPEN") == "OPEN":
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
else:
    st.markdown("""
    <div class="closed-card">
        <div style="background:#fee2e2; color:#dc2626; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; display:inline-block;">● GOLD CLOSED</div>
        <div style="font-size:1.5rem; font-weight:800; color:#dc2626; margin:5px 0;">⏸️ MARKET PAUSED</div>
    </div>
    """, unsafe_allow_html=True)

# 10. SILVER CARD
if settings.get("silver_market", "OPEN") == "OPEN":
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
else:
    st.markdown("""
    <div class="closed-card">
        <div style="background:#f3f4f6; color:#666; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; display:inline-block;">● SILVER CLOSED</div>
        <div style="font-size:1.5rem; font-weight:800; color:#666; margin:5px 0;">⏸️ MARKET PAUSED</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 11. ADMIN DASHBOARD
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Wrong Password")

if st.session_state.admin_auth:
    st.markdown("---")
    c1, c2 = st.columns([3,1])
    c1.subheader("⚙️ Admin Dashboard")
    if c2.button("🔴 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    tabs = st.tabs(["Update", "History", "Chart"])
    
    with tabs[0]:
        st.markdown("### 🌐 Market Status")
        col1, col2 = st.columns(2)
        
        current_g = settings.get("gold_market", "OPEN")
        current_s = settings.get("silver_market", "OPEN")
        
        if col1.button(f"Gold is {current_g} (Toggle)"):
            st.session_state.gold_market_status = "CLOSED" if current_g == "OPEN" else "OPEN"
            
        if col2.button(f"Silver is {current_s} (Toggle)"):
            st.session_state.silver_market_status = "CLOSED" if current_s == "OPEN" else "OPEN"

        st.divider()
        st.markdown("### 💰 Premiums")
        
        m1, m2 = st.columns(2)
        if m1.button("🟡 Gold"): st.session_state.selected_metal = "Gold"
        if m2.button("⚪ Silver"): st.session_state.selected_metal = "Silver"
        
        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        if st.session_state.selected_metal == "Gold":
            st.write(f"**Editing Gold Premium**")
            c1, c2 = st.columns(2)
            if c1.button("- 500", key="g_sub"): st.session_state.new_gold -= 500
            if c2.button("+ 500", key="g_add"): st.session_state.new_gold += 500
            st.session_state.new_gold = st.number_input("Value", value=st.session_state.new_gold, step=500)
        else:
            st.write(f"**Editing Silver Premium**")
            c1, c2 = st.columns(2)
            if c1.button("- 50", key="s_sub"): st.session_state.new_silver -= 50
            if c2.button("+ 50", key="s_add"): st.session_state.new_silver += 50
            st.session_state.new_silver = st.number_input("Value", value=st.session_state.new_silver, step=50)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- THE FIX FOR SAVE ERROR ---
        if st.button("🚀 SAVE CHANGES", type="primary", use_container_width=True):
            if repo:
                # 1. Update Settings
                new_data = {
                    "gold_premium": st.session_state.new_gold,
                    "silver_premium": st.session_state.new_silver,
                    "gold_market": st.session_state.gold_market_status,
                    "silver_market": st.session_state.silver_market_status
                }
                save_to_github("manual.json", new_data, "Update Settings")
                
                # 2. Update History
                try:
                    # Fetch existing history to append
                    contents = repo.get_contents("history.json")
                    history_data = json.loads(contents.decoded_content.decode())
                except:
                    history_data = [] # Start fresh if fails
                
                history_data.append({
                    "date": live_data['full_date'],
                    "gold_pk": gold_tola,
                    "silver_pk": silver_tola,
                    "gold_ounce": live_data['gold'],
                    "silver_ounce": live_data['silver'],
                    "usd": live_data['usd']
                })
                if len(history_data) > 60: history_data = history_data[-60:]
                
                save_to_github("history.json", history_data, "Log History")
                
                get_settings.clear()
                st.success("✅ Saved! Updates visible in ~5 seconds.")
                time.sleep(1)
                st.rerun()

    with tabs[1]:
        if st.button("Clear History"):
            save_to_github("history.json", [], "Reset History")
            st.rerun()
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                data = json.loads(contents.decoded_content.decode())
                if data:
                    df = pd.DataFrame(data)
                    display_df = pd.DataFrame({
                        'Date': df.get('date', 'N/A'),
                        'Gold Rate': df.get('gold_pk', 0).apply(lambda x: f"Rs {x:,.0f}"),
                        'Silver Rate': df.get('silver_pk', 0).apply(lambda x: f"Rs {x:,.0f}"),
                        'Gold Oz': df.get('gold_ounce', 0).apply(lambda x: f"${x:,.2f}"),
                        'Silver Oz': df.get('silver_ounce', 0).apply(lambda x: f"${x:,.2f}")
                    })
                    st.dataframe(display_df.iloc[::-1], use_container_width=True)
        except Exception as e:
            st.info(f"History Empty or Error: {e}")

    with tabs[2]:
        try:
            if repo:
                contents = repo.get_contents("history.json")
                data = json.loads(contents.decoded_content.decode())
                if len(data) > 1:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    c_type = st.radio("Chart:", ["Gold", "Silver"], horizontal=True)
                    y_val = 'gold_pk' if c_type == "Gold" else 'silver_pk'
                    color = '#d4af37' if c_type == "Gold" else '#71797E'
                    
                    c = alt.Chart(df).mark_line(color=color).encode(x='date:T', y=f'{y_val}:Q')
                    st.altair_chart(c, use_container_width=True)
        except:
            st.info("No Data")
