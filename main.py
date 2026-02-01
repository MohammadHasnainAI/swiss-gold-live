import streamlit as st
import requests
import json
import time
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Islam Jewellery Pro", page_icon="💎", layout="centered")

# ---------------------------------------------------------
# 2. INITIALIZE SESSION STATE
# ---------------------------------------------------------
defaults = {
    "admin_auth": False,
    "new_gold": 0,
    "new_silver": 0,
    "gold_market_status": "OPEN",
    "silver_market_status": "OPEN",
    "selected_metal": "Gold",
    "settings_loaded": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# 3. CSS STYLING (Ultra Compact)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}
.block-container {padding-top: 0rem !important; padding-bottom: 1rem !important; margin-top: -40px !important; max-width: 700px;}

/* Header */
.header-box {text-align:center; padding-bottom:5px; margin-bottom:10px; margin-top: 15px;}
.brand-title {font-size:1.8rem; font-weight:800; color:#111; letter-spacing:-0.5px; text-transform:uppercase; line-height: 1; margin-bottom: 2px;}
.brand-subtitle {font-size:0.65rem; color:#d4af37; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;}

/* Cards */
.price-card {background:#ffffff; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.04); border:1px solid #eef0f2; margin-bottom:8px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; line-height:1; margin:4px 0; letter-spacing:-1px;}
.price-label {font-size:0.85rem; color:#666; font-weight:500;}

/* Stats */
.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {background:#f1f3f5; border-radius:8px; padding:8px; text-align:center; border:1px solid #ebebeb; flex: 1;}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.55rem; color:#888; font-weight:600; text-transform:uppercase;}

/* Buttons */
.btn-grid {display: flex; gap: 8px; margin-top: 12px; justify-content: center;}
.contact-btn {flex: 1; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.85rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#222;}
.btn-whatsapp {background-color:#25D366;}

/* Admin */
.control-box {background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 15px; margin-bottom: 15px;}
.closed-card {background:#ffffff; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(220,38,38,0.05); border:2px solid #fee2e2; margin-bottom:8px;}
.metric-card-pro {background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-bottom: 3px solid #d4af37; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. GITHUB CONNECTION
# ---------------------------------------------------------
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    st.error(f"GitHub Error: {e}")

# ---------------------------------------------------------
# 5. DATA ENGINE (PROTECTED WITH CACHE)
# ---------------------------------------------------------
# ⚠️ SAFETY: Caches API for 2 mins so 5s refresh doesn't drain credits
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

# ⚠️ SETTINGS: Caches for 5s so users see Admin updates quickly
@st.cache_data(ttl=5, show_spinner=False)
def load_settings_from_github():
    if repo:
        try:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
        except:
            pass
    return {"gold_premium": 0, "silver_premium": 0, "gold_market": "OPEN", "silver_market": "OPEN"}

# Initialize Data
live_data = get_live_rates()
settings = load_settings_from_github()

# State Management
if not st.session_state.settings_loaded:
    st.session_state.new_gold = settings.get("gold_premium", 0)
    st.session_state.new_silver = settings.get("silver_premium", 0)
    st.session_state.gold_market_status = settings.get("gold_market", "OPEN")
    st.session_state.silver_market_status = settings.get("silver_market", "OPEN")
    st.session_state.settings_loaded = True

# ---------------------------------------------------------
# 6. CALCULATIONS
# ---------------------------------------------------------
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_silver
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# ---------------------------------------------------------
# 7. PUBLIC UI DISPLAY
# ---------------------------------------------------------
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
if st.session_state.gold_market_status == "OPEN":
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
        <div style="font-size:0.75rem; color:#999;">Check back later</div>
    </div>
    """, unsafe_allow_html=True)

# SILVER CARD
if st.session_state.silver_market_status == "OPEN":
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

# ---------------------------------------------------------
# 8. ADMIN DASHBOARD
# ---------------------------------------------------------
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        password = st.text_input("Password", type="password")
        if st.button("🔓 Login", use_container_width=True, type="primary"):
            if password == st.secrets["ADMIN_PASSWORD"]: 
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ Invalid Password")

if st.session_state.admin_auth:
    st.markdown("---")
    c1, c2 = st.columns([3,1])
    c1.subheader("⚙️ Admin Dashboard")
    if c2.button("🔴 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    tabs = st.tabs(["💰 Update Rates", "📊 Statistics", "📜 History", "📈 Charts"])

    with tabs[0]:
        st.markdown("### 🌐 Market Status")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Gold:** {st.session_state.gold_market_status}")
            if st.button("Toggle Gold", key="tg_gold"):
                st.session_state.gold_market_status = "CLOSED" if st.session_state.gold_market_status == "OPEN" else "OPEN"
                st.rerun()
        with col2:
            st.write(f"**Silver:** {st.session_state.silver_market_status}")
            if st.button("Toggle Silver", key="tg_silver"):
                st.session_state.silver_market_status = "CLOSED" if st.session_state.silver_market_status == "OPEN" else "OPEN"
                st.rerun()

        st.divider()
        st.markdown("### 💰 Update Premiums")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if st.button("🟡 GOLD", use_container_width=True, type="primary" if st.session_state.selected_metal == "Gold" else "secondary"):
                st.session_state.selected_metal = "Gold"
                st.rerun()
        with m_col2:
            if st.button("⚪ SILVER", use_container_width=True, type="primary" if st.session_state.selected_metal == "Silver" else "secondary"):
                st.session_state.selected_metal = "Silver"
                st.rerun()

        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        
        if st.session_state.selected_metal == "Gold":
            c1, c2 = st.columns(2)
            if c1.button("➖ 500", use_container_width=True): 
                st.session_state.new_gold -= 500
                st.rerun()
            if c2.button("➕ 500", use_container_width=True): 
                st.session_state.new_gold += 500
                st.rerun()
            st.session_state.new_gold = st.number_input("Gold Premium (Rs)", value=st.session_state.new_gold, step=500)
        else:
            c1, c2 = st.columns(2)
            if c1.button("➖ 50", use_container_width=True): 
                st.session_state.new_silver -= 50
                st.rerun()
            if c2.button("➕ 50", use_container_width=True): 
                st.session_state.new_silver += 50
                st.rerun()
            st.session_state.new_silver = st.number_input("Silver Premium (Rs)", value=st.session_state.new_silver, step=50)
        
        st.markdown('</div>', unsafe_allow_html=True)

        st.info("⚠️ Click Save below to apply Premium & Market Status changes.")
        if st.button("🚀 SAVE & PUBLISH ALL SETTINGS", type="primary", use_container_width=True):
            if repo:
                try:
                    new_settings = {
                        "gold_premium": st.session_state.new_gold,
                        "silver_premium": st.session_state.new_silver,
                        "gold_market": st.session_state.gold_market_status,
                        "silver_market": st.session_state.silver_market_status
                    }
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, "Update", json.dumps(new_settings), contents.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
                    try:
                        h_content = repo.get_contents("history.json")
                        history = json.loads(h_content.decoded_content.decode())
                    except:
                        history = []
                    
                    history.append({
                        "date": live_data['full_date'],
                        "gold_pk": gold_tola,
                        "silver_pk": silver_tola,
                        "gold_ounce": live_data['gold'],
                        "silver_ounce": live_data['silver'],
                        "usd": live_data['usd']
                    })
                    if len(history) > 60: history = history[-60:]

                    try:
                        repo.update_file(h_content.path, "Log", json.dumps(history), h_content.sha)
                    except:
                        repo.create_file("history.json", "Log Init", json.dumps(history))

                    # 3. FORCE CACHE CLEARING
                    load_settings_from_github.clear()
                    
                    st.success("✅ Published! Users will see updates shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"GitHub Error: {e}")
            else:
                st.error("❌ GitHub Connection Failed")

    # --- TAB 2: STATISTICS ---
    with tabs[1]:
        st.markdown("### Market Overview")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f'<div class="metric-card-pro"><div style="font-size:0.7rem;">GOLD PREMIUM</div><div style="font-size:1.5rem; color:#d4af37;">Rs {st.session_state.new_gold}</div></div>', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'<div class="metric-card-pro"><div style="font-size:0.7rem;">SILVER PREMIUM</div><div style="font-size:1.5rem; color:#666;">Rs {st.session_state.new_silver}</div></div>', unsafe_allow_html=True)
        with sc3:
            st.markdown(f'<div class="metric-card-pro"><div style="font-size:0.7rem;">USD RATE</div><div style="font-size:1.5rem; color:#333;">Rs {live_data["usd"]:.2f}</div></div>', unsafe_allow_html=True)

    # --- TAB 3: HISTORY ---
    with tabs[2]:
        if st.button("🗑️ Clear History (Fixes Errors)", type="secondary"):
            if repo:
                h = repo.get_contents("history.json")
                repo.update_file(h.path, "Reset", json.dumps([]), h.sha)
                st.success("History Reset.")
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
                        'Gold Oz ($)': df.get('gold_ounce', 0).apply(lambda x: f"${x:,.2f}"),
                        'USD Rate': df.get('usd', 0).apply(lambda x: f"Rs {x:.2f}")
                    })
                    st.dataframe(display_df.iloc[::-1], use_container_width=True, hide_index=True)
                else:
                    st.info("No history records.")
        except:
            st.info("History unavailable.")

    # --- TAB 4: CHART ---
    with tabs[3]:
        try:
            if repo and 'data' in locals() and len(data) > 1:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                c = alt.Chart(df).mark_line(point=True).encode(
                    x='date:T',
                    y=alt.Y('gold_pk:Q', scale=alt.Scale(zero=False)),
                    tooltip=['date', 'gold_pk', 'gold_ounce']
                ).properties(height=300)
                st.altair_chart(c, use_container_width=True)
            else:
                st.info("Chart needs at least 2 saved records.")
        except:
            st.info("Chart data unavailable.")

# ---------------------------------------------------------
# 10. REFRESH LOGIC (Native - No External Library)
# ---------------------------------------------------------
# This forces the page to reload every 5 seconds for Public Users
if not st.session_state.admin_auth:
    time.sleep(5)
    st.rerun()

# 11. FOOTER
st.markdown("""
<div class="footer">
Islam Jewellery • Live Market Rates<br>
Updated: {}
</div>
""".format(datetime.now(pytz.timezone("Asia/Karachi")).strftime("%H:%M:%S")), unsafe_allow_html=True)
