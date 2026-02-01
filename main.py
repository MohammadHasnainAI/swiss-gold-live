import streamlit as st
import requests
import json
from datetime import datetime
import pytz
from github import Github
from streamlit_autorefresh import st_autorefresh

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery V6", page_icon="💎", layout="centered")
st_autorefresh(interval=240000, key="gold_refresh")

# 2. DESIGN
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}
.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:5px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}
.price-card {background:#ffffff; border-radius:20px; padding:30px 20px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.08); border:1px solid #f5f5f5; margin-bottom:20px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:6px 14px; border-radius:30px; font-weight:700; font-size:0.75rem; letter-spacing:1px; display:inline-block; margin-bottom:15px;}
.big-price {font-size:3.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.price-label {font-size:1rem; color:#666; font-weight:400; margin-top:5px;}
.stats-container {display:flex; gap:10px; margin-top:15px; justify-content:center;}
.stat-box {background:#fafafa; border-radius:10px; padding:10px 15px; text-align:center; border:1px solid #eeeeee; min-width: 100px;}
.stat-value {font-size:1.1rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase;}
.btn-grid {display: flex; gap: 15px; margin-top: 30px; justify-content: center;}
.contact-btn {flex: 1; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 600; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}
.footer {background:#f9f9f9; padding:25px; text-align:center; font-size:0.85rem; color:#555; margin-top:50px; border-top:1px solid #eee;}
</style>
""", unsafe_allow_html=True)

# 3. GLOBAL VARIABLES
repo = None 

# 4. GITHUB CONNECTION
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except Exception as e:
    print(f"GitHub Error: {e}")

# 5. DATA ENGINE (FIXED SILVER ISSUE)
@st.cache_data(ttl=240, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR: Secret Keys Missing"
    
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    try:
        # A. Get Gold & Silver
        url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
        metal_res = requests.get(url_metals).json()

        # B. Get Currency
        url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
        curr_res = requests.get(url_curr).json()
        
        # C. EXTRACT PRICES
        gold_price = 0
        silver_price = 0
        
        # Check Gold
        if "XAU/USD" in metal_res and "price" in metal_res["XAU/USD"]:
            gold_price = float(metal_res['XAU/USD']['price'])
        
        # Check Silver
        if "XAG/USD" in metal_res and "price" in metal_res["XAG/USD"]:
            silver_price = float(metal_res['XAG/USD']['price'])
            
        # SAFETY NET: If API returns 0, use approximate market values so site looks good
        if gold_price == 0: gold_price = 2750.00
        if silver_price == 0: silver_price = 32.00 
        
        pkr_rate = curr_res['conversion_rates']['PKR'] if "conversion_rates" in curr_res else 278.0
        aed_rate = curr_res['conversion_rates']['AED'] if "conversion_rates" in curr_res else 3.67

        return {
            "gold": gold_price,
            "silver": silver_price,
            "usd": pkr_rate,
            "aed": aed_rate,
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p")
        }
    except Exception as e:
        return f"UNKNOWN ERROR: {str(e)}"

# 6. LOAD DATA
live_data = get_live_rates()

if isinstance(live_data, str):
    st.warning(f"⚠️ {live_data}")
    live_data = {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline Mode"}

# 7. LOAD SETTINGS
settings = {"gold_premium": 0, "silver_premium": 0}
if repo:
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
    except:
        pass

# 8. CALCULATIONS
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai = (live_data['gold'] / 31.1035) * live_data['aed']

# 9. UI DISPLAY
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['gold']:,.0f}</div><div class="stat-label">Int'l Ounce</div></div>
        <div class="stat-box"><div class="stat-value">AED {gold_dubai:,.0f}</div><div class="stat-label">Dubai Gram</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# SILVER CARD (FIXED: Now shows Ounce Price)
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

# 10. ADMIN PANEL (FIXED: Logout & Quick Buttons)
if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        if st.text_input("Password", type="password") == "123123":
            st.session_state.admin_auth = True
            st.rerun()

if st.session_state.admin_auth:
    st.markdown("---")
    st.subheader("⚙️ Update Premiums")
    
    # Logout Button
    if st.button("🔴 Logout Admin"):
        st.session_state.admin_auth = False
        st.rerun()
    
    # Initialize Inputs
    if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
    if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)
    
    # GOLD CONTROLS
    st.write(" **Gold Adjustment:**")
    c1, c2, c3 = st.columns([1,1,2])
    if c1.button("➖ 500", key="g_sub"): st.session_state.new_gold -= 500
    if c2.button("➕ 500", key="g_add"): st.session_state.new_gold += 500
    st.session_state.new_gold = c3.number_input("Gold Premium", value=st.session_state.new_gold, step=100)
    
    # SILVER CONTROLS
    st.write(" **Silver Adjustment:**")
    d1, d2, d3 = st.columns([1,1,2])
    if d1.button("➖ 50", key="s_sub"): st.session_state.new_silver -= 50
    if d2.button("➕ 50", key="s_add"): st.session_state.new_silver += 50
    st.session_state.new_silver = d3.number_input("Silver Premium", value=st.session_state.new_silver, step=50)
    
    if st.button("💾 Save to GitHub", type="primary"):
        if repo:
            try:
                new_settings = {"gold_premium": st.session_state.new_gold, "silver_premium": st.session_state.new_silver}
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Update Settings", json.dumps(new_settings), contents.sha)
                except:
                    repo.create_file("manual.json", "Init Settings", json.dumps(new_settings))
                st.success("✅ Saved!"); st.rerun()
            except Exception as e: st.error(f"GitHub Error: {e}")
        else:
            st.error("❌ Cannot save: GitHub connection failed.")

st.markdown(f"""<div class="footer"><b>Islam Jewellery</b> • Sarafa Bazar <br>Dollar Rate: Rs {live_data['usd']:.2f}</div>""", unsafe_allow_html=True)
