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

# Auto-refresh every 30 seconds
st_autorefresh(interval=30000, key="gold_refresh") 

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

# 4. GITHUB CONNECTION
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    print(f"GitHub Error: {e}")

# 5. DATA ENGINE
@st.cache_data(ttl=30, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR"
    
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

# 6. LOAD SETTINGS
@st.cache_data(ttl=30, show_spinner=False)
def load_settings():
    default_settings = {"gold_premium": 0, "silver_premium": 0}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
        except:
            pass
    return default_settings

live_data = get_live_rates()
settings = load_settings()

if isinstance(live_data, str):
    live_data = {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline Mode", "full_date": "2024-01-01"}

# Initialize Inputs
if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)

# 7. CALCULATIONS
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# 8. UI DISPLAY
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['gold']:,.0f}</div><div class="stat-label">Int'l Ounce</div></div>
        <div class="stat-box"><div class="stat-value">Rs {live_data['usd']:.2f}</div><div class="stat-label">Dollar Rate</div></div>
        <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai Tola</div></div>
    </div>
    <div style="font-size:0.75rem; color:#aaa; margin-top:15px; padding-top:10px; border-top:1px solid #eee;">
        Last Updated: <b>{live_data['time']}</b>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Check for New Gold Rate", use_container_width=True):
    manual_refresh()
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

# 9. PROFESSIONAL SIDEBAR ADMIN
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False

with st.sidebar:
    st.markdown("### 🛡️ Admin Access")
    if not st.session_state.admin_auth:
        admin_pass = st.text_input("Enter Key", type="password")
        if st.button("Login"):
            if admin_pass == "123123":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Invalid Key")
    
    if st.session_state.admin_auth:
        st.success("Verfied Admin")
        if st.button("Log Out"):
            st.session_state.admin_auth = False
            st.rerun()

# 10. MAIN ADMIN DASHBOARD (Only visible if logged in)
if st.session_state.admin_auth:
    st.divider()
    st.markdown("## 🎛️ Control Center")
    
    # Live Status Bar
    s1, s2, s3 = st.columns(3)
    s1.metric("Live Gold (Ounce)", f"${live_data['gold']:,.0f}")
    s2.metric("Current Premium", f"Rs {settings['gold_premium']}")
    s3.metric("Current Price", f"Rs {gold_tola:,.0f}")

    # Tabs for neat organization
    tab_update, tab_history = st.tabs(["✏️ Update Prices", "📜 History"])

    with tab_update:
        st.info("💡 Adjust the premium to match the local market rate.")
        
        col_gold, col_silver = st.columns(2)
        
        with col_gold:
            st.markdown("#### 🟡 Gold")
            g_btn1, g_btn2 = st.columns(2)
            g_btn1.button("➖ 500", key="g_dec", on_click=update_premium, args=("new_gold", -500))
            g_btn2.button("➕ 500", key="g_inc", on_click=update_premium, args=("new_gold", 500))
            st.number_input("Premium (Rs)", key="new_gold", step=100)
            
        with col_silver:
            st.markdown("#### ⚪ Silver")
            s_btn1, s_btn2 = st.columns(2)
            s_btn1.button("➖ 50", key="s_dec", on_click=update_premium, args=("new_silver", -50))
            s_btn2.button("➕ 50", key="s_inc", on_click=update_premium, args=("new_silver", 50))
            st.number_input("Premium (Rs)", key="new_silver", step=50)

        st.markdown("---")
        
        # PREVIEW CALCULATION
        preview_price = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
        st.caption(f"🚀 **Preview New Price:** Rs {preview_price:,.0f}")

        if st.button("✅ Publish New Rates", type="primary", use_container_width=True):
            if repo:
                try:
                    # Save Settings
                    new_settings = {"gold_premium": st.session_state.new_gold, "silver_premium": st.session_state.new_silver}
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, "Update", json.dumps(new_settings), contents.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
                    # Save History
                    try:
                        h_content = repo.get_contents("history.json")
                        history = json.loads(h_content.decoded_content.decode())
                    except:
                        history = []
                    
                    history.append({
                        "date": live_data['full_date'],
                        "gold": preview_price,
                        "premium": st.session_state.new_gold
                    })
                    if len(history) > 60: history = history[-60:]

                    try:
                        repo.update_file(h_content.path, "Hist Update", json.dumps(history), h_content.sha)
                    except:
                        repo.create_file("history.json", "Init Hist", json.dumps(history))

                    st.toast("✅ Rates Updated Successfully!")
                    manual_refresh()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("GitHub Connection Failed")

    with tab_history:
        try:
            if repo:
                contents = repo.get_contents("history.json")
                df = pd.DataFrame(json.loads(contents.decoded_content.decode()))
                st.dataframe(df, use_container_width=True)
        except:
            st.info("No history available yet.")

# 11. FOOTER
st.markdown("""
<div class="footer">
**Islam Jewellery** • Sarafa Bazar <br>
⚠️ Prices are indicative and subject to market changes. Verify before booking.
</div>
""", unsafe_allow_html=True)
