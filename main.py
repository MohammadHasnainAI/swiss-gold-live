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
# 2. CSS STYLING
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
.closed-card {background:#ffffff; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 6px rgba(220,38,38,0.05); border:2px solid #fee2e2; margin-bottom:8px;}
.metric-card-pro {background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-bottom: 3px solid #d4af37; text-align: center;}
.control-box {background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 15px; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. GLOBAL VARIABLES & FUNCTIONS
# ---------------------------------------------------------
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# API Data Engine (Cached 2 Mins)
@st.cache_data(ttl=120, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return {"gold": 2750, "silver": 32, "usd": 278, "aed": 3.67, "time": "Demo"}
    try:
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={st.secrets['TWELVE_DATA_KEY']}"
        metal_res = requests.get(url_metals, timeout=5).json()
        url_curr = f"https://v6.exchangerate-api.com/v6/{st.secrets['CURR_KEY']}/latest/USD"
        curr_res = requests.get(url_curr, timeout=5).json()
        
        return {
            "gold": float(metal_res.get('XAU/USD', {}).get('price', 2750.0)),
            "silver": float(metal_res.get('XAG/USD', {}).get('price', 32.0)),
            "usd": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline"}

# Settings Engine
@st.cache_data(ttl=2, show_spinner=False)
def get_settings():
    default = {"gold_premium": 0, "silver_premium": 0, "gold_market": "OPEN", "silver_market": "OPEN"}
    try:
        if "GIT_TOKEN" in st.secrets:
            g = Github(st.secrets["GIT_TOKEN"])
            repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode()), repo
    except:
        pass
    return default, None

# ---------------------------------------------------------
# 4. PUBLIC INTERFACE (AUTO-REFRESHING FRAGMENT)
# ---------------------------------------------------------
@st.fragment(run_every=5) 
def show_public_dashboard():
    # 1. Get Fresh Data
    live = get_live_rates()
    settings, _ = get_settings()
    
    # 2. Calculate
    gold_tola = ((live['gold'] / 31.1035) * 11.66 * live['usd']) + settings.get("gold_premium", 0)
    silver_tola = ((live['silver'] / 31.1035) * 11.66 * live['usd']) + settings.get("silver_premium", 0)
    gold_dubai = (live['gold'] / 31.1035) * 11.66 * live['aed']

    # 3. Header
    st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

    # 4. Gold Card
    if settings.get("gold_market", "OPEN") == "OPEN":
        st.markdown(f"""
        <div class="price-card">
            <div class="live-badge">● GOLD LIVE</div>
            <div class="big-price">Rs {gold_tola:,.0f}</div>
            <div class="price-label">24K Gold Per Tola</div>
            <div class="stats-container">
                <div class="stat-box"><div class="stat-value">${live['gold']:,.0f}</div><div class="stat-label">Ounce</div></div>
                <div class="stat-box"><div class="stat-value">Rs {live['usd']:.2f}</div><div class="stat-label">Dollar</div></div>
                <div class="stat-box"><div class="stat-value">AED {gold_dubai:,.0f}</div><div class="stat-label">Dubai</div></div>
            </div>
            <div style="font-size:0.6rem; color:#aaa; margin-top:8px; padding-top:5px; border-top:1px solid #eee;">
                Last Updated: <b>{live['time']}</b>
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

    # 5. Silver Card
    if settings.get("silver_market", "OPEN") == "OPEN":
        st.markdown(f"""
        <div class="price-card">
            <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
            <div class="big-price">Rs {silver_tola:,.0f}</div>
            <div class="price-label">24K Silver Per Tola</div>
            <div class="stats-container">
                <div class="stat-box"><div class="stat-value">${live['silver']:,.2f}</div><div class="stat-label">Ounce</div></div>
                <div class="stat-box"><div class="stat-value">{live['time']}</div><div class="stat-label">Updated</div></div>
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

    # 6. Buttons
    st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div style="text-align:center; margin-top:20px; color:#aaa; font-size:0.6rem;">Auto-Sync Active • {datetime.now(pytz.timezone("Asia/Karachi")).strftime("%H:%M:%S")}</div>""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 5. MAIN LOGIC ROUTER
# ---------------------------------------------------------
if not st.session_state.admin_auth:
    show_public_dashboard()
    
    with st.expander("🔒 Admin Login"):
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Wrong Password")

else:
    # ADMIN VIEW
    st.markdown("---")
    c1, c2 = st.columns([3,1])
    c1.subheader("⚙️ Admin Dashboard")
    if c2.button("🔴 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    settings, repo = get_settings()
    
    # Init Session Vars for Editing
    if "edit_gold" not in st.session_state: st.session_state.edit_gold = settings.get("gold_premium", 0)
    if "edit_silver" not in st.session_state: st.session_state.edit_silver = settings.get("silver_premium", 0)
    
    tabs = st.tabs(["Update", "History", "Chart"])
    
    with tabs[0]:
        st.markdown("### 🌐 Market Status")
        col1, col2 = st.columns(2)
        
        new_gold_status = "OPEN" if settings.get("gold_market") == "OPEN" else "CLOSED"
        new_silver_status = "OPEN" if settings.get("silver_market") == "OPEN" else "CLOSED"
        
        if col1.button(f"Gold is {new_gold_status} (Toggle)"):
            new_gold_status = "CLOSED" if new_gold_status == "OPEN" else "OPEN"
            
        if col2.button(f"Silver is {new_silver_status} (Toggle)"):
            new_silver_status = "CLOSED" if new_silver_status == "OPEN" else "OPEN"

        st.divider()
        st.markdown("### 💰 Premiums")
        
        st.write("🟡 **Gold Premium**")
        gc1, gc2 = st.columns(2)
        if gc1.button("- 500", key="g_sub"): st.session_state.edit_gold -= 500
        if gc2.button("+ 500", key="g_add"): st.session_state.edit_gold += 500
        st.session_state.edit_gold = st.number_input("Gold Value", value=st.session_state.edit_gold, step=500)

        st.write("⚪ **Silver Premium**")
        sc1, sc2 = st.columns(2)
        if sc1.button("- 50", key="s_sub"): st.session_state.edit_silver -= 50
        if sc2.button("+ 50", key="s_add"): st.session_state.edit_silver += 50
        st.session_state.edit_silver = st.number_input("Silver Value", value=st.session_state.edit_silver, step=50)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- FIXED SAVE BUTTON LOGIC (Solves the SHA Error) ---
        if st.button("🚀 SAVE & PUBLISH CHANGES", type="primary", use_container_width=True):
            if repo:
                new_data = {
                    "gold_premium": st.session_state.edit_gold,
                    "silver_premium": st.session_state.edit_silver,
                    "gold_market": new_gold_status,
                    "silver_market": new_silver_status
                }
                
                # 1. Update Settings with Fresh SHA
                try:
                    # FETCH FRESH FILE CONTENT & SHA IMMEDIATELY BEFORE UPDATING
                    file = repo.get_contents("manual.json")
                    repo.update_file(file.path, "Update", json.dumps(new_data), file.sha)
                except:
                    repo.create_file("manual.json", "Init", json.dumps(new_data))
                
                # 2. Update History with Fresh SHA
                live = get_live_rates()
                try:
                    h_file = repo.get_contents("history.json")
                    hist_data = json.loads(h_file.decoded_content.decode())
                    
                    hist_data.append({
                        "date": live['full_date'],
                        "gold_pk": ((live['gold']/31.1035)*11.66*live['usd']) + st.session_state.edit_gold,
                        "gold_ounce": live['gold'],
                        "usd": live['usd']
                    })
                    if len(hist_data) > 60: hist_data = hist_data[-60:]
                    
                    # Update with the FRESH sha we just got
                    repo.update_file(h_file.path, "Log", json.dumps(hist_data), h_file.sha)
                except:
                    hist_data = [{
                        "date": live['full_date'],
                        "gold_pk": ((live['gold']/31.1035)*11.66*live['usd']) + st.session_state.edit_gold,
                        "gold_ounce": live['gold'],
                        "usd": live['usd']
                    }]
                    repo.create_file("history.json", "Init", json.dumps(hist_data))
                
                # Clear Cache
                get_settings.clear()
                st.success("✅ Published! Auto-Refresh will show changes in ~5s.")
                time.sleep(1)
                st.rerun()

    # History Tab
    with tabs[1]:
        if st.button("Clear History"):
            if repo:
                try:
                    h = repo.get_contents("history.json")
                    repo.update_file(h.path, "Reset", json.dumps([]), h.sha)
                    st.rerun()
                except:
                    pass
        
        try:
            if repo:
                h = repo.get_contents("history.json")
                data = json.loads(h.decoded_content.decode())
                st.dataframe(pd.DataFrame(data).iloc[::-1], use_container_width=True)
        except:
            st.info("No Data")

    # Chart Tab
    with tabs[2]:
        try:
            if repo:
                h = repo.get_contents("history.json")
                data = json.loads(h.decoded_content.decode())
                if len(data) > 1:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    c = alt.Chart(df).mark_line().encode(x='date:T', y='gold_pk:Q')
                    st.altair_chart(c, use_container_width=True)
        except:
            st.info("No Data")
