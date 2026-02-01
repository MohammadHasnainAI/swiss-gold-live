import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Islam Jewellery Pro", page_icon="💎", layout="centered")

# ---------------------------------------------------------
# 2. INITIALIZE SESSION STATE (The Brains)
# ---------------------------------------------------------
# This ensures buttons and inputs remember their value
defaults = {
    "admin_auth": False,
    "new_gold": 0,
    "new_silver": 0,
    "gold_market_status": "OPEN",
    "silver_market_status": "OPEN",
    "settings_loaded": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Auto-Refresh: Only runs for customers (Public), not Admin (to prevent input resetting)
if not st.session_state.admin_auth:
    st_autorefresh(interval=5000, key="public_refresh") 

# ---------------------------------------------------------
# 3. CSS STYLING (Ultra Compact + Gray Theme)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

/* Main Background */
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* --- SPACE REMOVER --- */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
    margin-top: -40px !important;
    max-width: 700px;
}

/* Header */
.header-box {text-align:center; padding-bottom:5px; margin-bottom:10px; margin-top: 15px;}
.brand-title {font-size:1.8rem; font-weight:800; color:#111; letter-spacing:-0.5px; text-transform:uppercase; line-height: 1; margin-bottom: 2px;}
.brand-subtitle {font-size:0.65rem; color:#d4af37; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;}

/* Price Cards (Live) */
.price-card {
    background:#ffffff; 
    border-radius:16px; 
    padding:15px; 
    text-align:center; 
    box-shadow:0 4px 6px rgba(0,0,0,0.04); 
    border:1px solid #eef0f2; 
    margin-bottom:8px; 
}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; line-height:1; margin:4px 0; letter-spacing:-1px;}
.price-label {font-size:0.85rem; color:#666; font-weight:500;}

/* Closed Cards */
.closed-card {
    background:#ffffff; 
    border-radius:16px; 
    padding:20px; 
    text-align:center; 
    box-shadow:0 4px 6px rgba(220,38,38,0.05); 
    border:2px solid #fee2e2; 
    margin-bottom:8px; 
}
.closed-badge {background-color:#fee2e2; color:#dc2626; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; display:inline-block; margin-bottom:4px;}
.closed-text {font-size:1.5rem; font-weight:800; color:#dc2626; margin:5px 0;}

/* Stats Boxes */
.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {
    background:#f1f3f5; 
    border-radius:8px; 
    padding:8px; 
    text-align:center; 
    border:1px solid #ebebeb; 
    flex: 1; 
}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.55rem; color:#888; font-weight:600; text-transform:uppercase;}

/* Buttons */
.btn-grid {display: flex; gap: 8px; margin-top: 12px; justify-content: center;}
.contact-btn {
    flex: 1; 
    padding: 12px; 
    border-radius: 10px; 
    text-align: center; 
    text-decoration: none; 
    font-weight: 600; 
    font-size: 0.85rem; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    color: white !important;
}
.btn-call {background-color:#222;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {opacity:0.9;}

/* Admin Controls */
.control-box {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
}
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
# 5. DATA ENGINE
# ---------------------------------------------------------
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return {"gold": 2750, "silver": 32, "usd": 278, "aed": 3.67, "time": "Demo"}
    
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    try:
        # Timeout added to prevent hanging
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals, timeout=5).json()

        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr, timeout=5).json()
        
        gold_price = float(metal_res['XAU/USD']['price']) if "XAU/USD" in metal_res else 2750.0
        silver_price = float(metal_res['XAG/USD']['price']) if "XAG/USD" in metal_res else 32.0
        
        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline", "full_date": "2024-01-01"}

# ---------------------------------------------------------
# 6. INITIALIZE & LOAD SETTINGS
# ---------------------------------------------------------
live_data = get_live_rates()

# Load Settings ONLY ONCE per session to allow Admin editing without reset
if not st.session_state.settings_loaded and repo:
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
        
        st.session_state.new_gold = settings.get("gold_premium", 0)
        st.session_state.new_silver = settings.get("silver_premium", 0)
        st.session_state.gold_market_status = settings.get("gold_market", "OPEN")
        st.session_state.silver_market_status = settings.get("silver_market", "OPEN")
        st.session_state.settings_loaded = True
    except:
        # If file doesn't exist, just mark loaded
        st.session_state.settings_loaded = True

# ---------------------------------------------------------
# 7. CALCULATIONS
# ---------------------------------------------------------
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_silver
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# ---------------------------------------------------------
# 8. PUBLIC UI DISPLAY
# ---------------------------------------------------------
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# --- GOLD SECTION ---
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
        <div class="closed-badge">● GOLD CLOSED</div>
        <div class="closed-text">⏸️ MARKET CLOSED</div>
        <div style="font-size:0.75rem; color:#999;">Rates are temporarily paused by Admin</div>
    </div>
    """, unsafe_allow_html=True)

# REFRESH BUTTON
if st.button("🔄 Check for New Prices", use_container_width=True):
    get_live_rates.clear()
    st.rerun()

# --- SILVER SECTION ---
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
        <div class="closed-badge" style="background:#f3f4f6; color:#666;">● SILVER CLOSED</div>
        <div class="closed-text" style="color:#666;">⏸️ MARKET CLOSED</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 9. ADMIN DASHBOARD
# ---------------------------------------------------------
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

    tabs = st.tabs(["💰 Update Rates", "📜 History", "📈 Chart"])

    # --- TAB 1: UPDATE ---
    with tabs[0]:
        st.markdown("### 🌐 Market Status")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Gold:** {st.session_state.gold_market_status}")
            if st.button("Toggle Gold"):
                st.session_state.gold_market_status = "CLOSED" if st.session_state.gold_market_status == "OPEN" else "OPEN"
                st.rerun()
        with col2:
            st.write(f"**Silver:** {st.session_state.silver_market_status}")
            if st.button("Toggle Silver"):
                st.session_state.silver_market_status = "CLOSED" if st.session_state.silver_market_status == "OPEN" else "OPEN"
                st.rerun()

        st.divider()
        st.markdown("### 💰 Update Premiums")
        
        metal_choice = st.radio("Select Metal:", ["Gold", "Silver"], horizontal=True)
        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        
        if metal_choice == "Gold":
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

        # BIG SAVE BUTTON
        st.info("⚠️ Click Save below to apply Premium & Market Status changes.")
        if st.button("🚀 SAVE & PUBLISH ALL SETTINGS", type="primary", use_container_width=True):
            if repo:
                try:
                    # 1. Save Settings
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
                    
                    # 2. Save History (With Ounce Logic)
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

                    st.success("✅ Published! Users will see updates shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"GitHub Error: {e}")
            else:
                st.error("❌ GitHub Connection Failed")

    # --- TAB 2: HISTORY ---
    with tabs[1]:
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
                    # Safe Display Table (Handles missing columns)
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

    # --- TAB 3: CHART ---
    with tabs[2]:
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

# 10. FOOTER
st.markdown("""
<div style="text-align:center; margin-top:20px; color:#aaa; font-size:0.7rem;">
Islam Jewellery • Live Market Rates
</div>
""", unsafe_allow_html=True)
