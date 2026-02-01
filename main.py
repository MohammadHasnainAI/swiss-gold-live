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
st.set_page_config(page_title="Islam Jewellery V10", page_icon="💎", layout="centered")
st_autorefresh(interval=240000, key="gold_refresh")

# 2. HELPER FUNCTIONS (The Fix for Buttons)
def adjust_val(key, amount):
    """Safely updates session state values without bugs."""
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] += amount

def clear_cache():
    """Forces a price refresh."""
    get_live_rates.clear()

# 3. DESIGN
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

.price-card {background:#ffffff; border-radius:20px; padding:30px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:20px; position: relative;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:6px 14px; border-radius:30px; font-weight:700; font-size:0.75rem; letter-spacing:1px; display:inline-block; margin-bottom:15px;}
.big-price {font-size:3.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:5px;}

.stats-container {display:flex; gap:8px; margin-top:15px; justify-content:center; flex-wrap: wrap;}
.stat-box {background:#fafafa; border-radius:10px; padding:10px; text-align:center; border:1px solid #eeeeee; flex: 1; min-width: 80px;}
.stat-value {font-size:1.0rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase;}

.btn-grid {display: flex; gap: 15px; margin-top: 30px; justify-content: center;}
.contact-btn {flex: 1; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 600; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}

.footer {background:#f9f9f9; padding:25px; text-align:center; font-size:0.85rem; color:#555; margin-top:50px; border-top:1px solid #eee; line-height: 1.6;}
.refresh-btn {margin-top: 10px;}
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

# 5. DATA ENGINE
@st.cache_data(ttl=3600, show_spinner=False) # Cache for 1 hour, manual refresh clears it
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR: Secret Keys Missing"
    
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    try:
        # A. Metals
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals).json()

        # B. Currency
        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr).json()
        
        # C. Process
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
            "usd_bank": curr_res['conversion_rates']['PKR'] if "conversion_rates" in curr_res else 278.0,
            "aed": curr_res['conversion_rates']['AED'] if "conversion_rates" in curr_res else 3.67,
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return f"UNKNOWN ERROR: {str(e)}"

# 6. LOAD DATA & SETTINGS
live_data = get_live_rates()

if isinstance(live_data, str):
    st.warning(f"⚠️ {live_data}")
    live_data = {"gold": 2750.0, "silver": 32.0, "usd_bank": 278.0, "aed": 3.67, "time": "Offline Mode", "full_date": "2024-01-01"}

settings = {"gold_premium": 0, "silver_premium": 0, "usd_adj": 0}
if repo:
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
    except:
        pass

# Initialize Session State for Inputs (This fixes the button bug)
if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)
if "new_usd" not in st.session_state: st.session_state.new_usd = settings.get("usd_adj", 0.0)

# Calculations
final_usd_rate = live_data['usd_bank'] + settings.get("usd_adj", 0)
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * final_usd_rate) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * final_usd_rate) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# 7. UI DISPLAY
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# --- GOLD CARD WITH REFRESH BUTTON ---
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
</div>
""", unsafe_allow_html=True)

# Refresh Button
if st.button("🔄 Update / Refresh Price", type="secondary", use_container_width=True):
    clear_cache()
    st.rerun()

# --- SILVER CARD ---
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

# 8. ADMIN DASHBOARD
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

    tabs = st.tabs(["Update Prices", "Stats", "History", "Gold Price Chart"])

    with tabs[0]:
        st.subheader("💵 Dollar Adjustment")
        c1, c2, c3 = st.columns([1,1,2])
        # Using on_click fixes the jumping bug
        c1.button("- 0.5", on_click=adjust_val, args=("new_usd", -0.5))
        c2.button("+ 0.5", on_click=adjust_val, args=("new_usd", 0.5))
        st.session_state.new_usd = c3.number_input("Dollar Adj (Rs)", value=float(st.session_state.new_usd), step=0.1)

        st.divider()

        metal_choice = st.radio("Select Metal:", ["Gold", "Silver"], horizontal=True)
        if metal_choice == "Gold":
            st.subheader("🟡 Gold Premium")
            c1, c2, c3 = st.columns([1,1,2])
            c1.button("- 500", key="g_sub", on_click=adjust_val, args=("new_gold", -500))
            c2.button("+ 500", key="g_add", on_click=adjust_val, args=("new_gold", 500))
            st.session_state.new_gold = c3.number_input("Gold Premium (Rs)", value=st.session_state.new_gold, step=100)
        else:
            st.subheader("⚪ Silver Premium")
            d1, d2, d3 = st.columns([1,1,2])
            d1.button("- 50", key="s_sub", on_click=adjust_val, args=("new_silver", -50))
            d2.button("+ 50", key="s_add", on_click=adjust_val, args=("new_silver", 50))
            st.session_state.new_silver = d3.number_input("Silver Premium (Rs)", value=st.session_state.new_silver, step=50)

        if st.button("🚀 Publish Changes", type="primary"):
            if repo:
                try:
                    new_settings = {
                        "gold_premium": st.session_state.new_gold, 
                        "silver_premium": st.session_state.new_silver,
                        "usd_adj": st.session_state.new_usd
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
        st.metric("Gold Premium", f"Rs {st.session_state.new_gold}")
        st.metric("Dollar Adjustment", f"+ Rs {st.session_state.new_usd}")
        st.metric("Final Dollar Rate", f"Rs {final_usd_rate:.2f}")

    with tabs[2]:
        try:
            if repo:
                contents = repo.get_contents("history.json")
                st.dataframe(pd.DataFrame(json.loads(contents.decoded_content.decode())))
        except:
            st.info("No history yet.")
    
    with tabs[3]:
        st.info("Chart will appear after history builds up.")

# 9. FOOTER
st.markdown("""
<div class="footer">
**Islam Jewellery** website shows approximate gold prices.<br>
Prices are updated based on market data and admin-set premium.<br><br>
⚠️ **Disclaimer:** Prices are indicative and may change anytime. Always verify with the shop before buying. Contact shop directly for confirmed gold rates.
</div>
""", unsafe_allow_html=True)
