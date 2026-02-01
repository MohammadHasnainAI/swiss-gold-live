import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Islam Jewellery V7", page_icon="💎", layout="centered")
st_autorefresh(interval=240000, key="gold_refresh")


# -----------------------------
# CSS DESIGN
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

.header-box {text-align:center; padding-bottom:20px; border-bottom:1px solid #f0f0f0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600;}

.price-card {background:#fff; border-radius:20px; padding:30px 20px;
text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.08);
border:1px solid #f5f5f5; margin-bottom:20px;}

.live-badge {background:#e6f4ea; color:#1e8e3e;
padding:6px 14px; border-radius:30px;
font-weight:700; font-size:0.75rem; display:inline-block;}

.big-price {font-size:3.3rem; font-weight:800; margin:10px 0;}

.stats-container {display:flex; gap:10px; justify-content:center; flex-wrap:wrap;}
.stat-box {background:#fafafa; border-radius:10px; padding:10px;
text-align:center; border:1px solid #eee; min-width:90px;}
.stat-value {font-size:1rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600;}

.btn-grid {display:flex; gap:15px; margin-top:30px; justify-content:center;}
.contact-btn {flex:1; padding:15px; border-radius:12px;
text-align:center; font-weight:600; text-decoration:none;
color:white !important;}
.btn-call {background:#111;}
.btn-whatsapp {background:#25D366;}

.footer {background:#f9f9f9; padding:25px; text-align:center;
font-size:0.85rem; color:#555; margin-top:50px;
border-top:1px solid #eee; line-height:1.6;}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# CONNECT GITHUB
# -----------------------------
repo = None
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except:
    pass


# -----------------------------
# LIVE API DATA
# -----------------------------
@st.cache_data(ttl=240)
def get_live_rates():
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]

    url_metals = f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}"
    metal_res = requests.get(url_metals).json()

    url_curr = f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD"
    curr_res = requests.get(url_curr).json()

    gold_price = float(metal_res["XAU/USD"]["price"])
    silver_price = float(metal_res["XAG/USD"]["price"])

    return {
        "gold": gold_price,
        "silver": silver_price,
        "usd": curr_res["conversion_rates"]["PKR"],
        "aed": curr_res["conversion_rates"]["AED"],
        "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
        "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
    }


live_data = get_live_rates()


# -----------------------------
# LOAD SETTINGS
# -----------------------------
settings = {"gold_premium": 0, "silver_premium": 0}

if repo:
    try:
        content = repo.get_contents("manual.json")
        settings = json.loads(content.decoded_content.decode())
    except:
        pass


# -----------------------------
# CALCULATIONS
# -----------------------------
gold_tola = ((live_data["gold"] / 31.1035) * 11.66 * live_data["usd"]) + settings["gold_premium"]
silver_tola = ((live_data["silver"] / 31.1035) * 11.66 * live_data["usd"]) + settings["silver_premium"]

gold_dubai_tola = (live_data["gold"] / 31.1035) * 11.66 * live_data["aed"]


# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="header-box">
  <div class="brand-title">Islam Jewellery</div>
  <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# GOLD CARD + BUTTON + LAST UPDATE
# -----------------------------
st.markdown(f"""
<div class="price-card">
    <div class="live-badge">● GOLD LIVE</div>
    <div class="big-price">Rs {gold_tola:,.0f}</div>
    <div class="price-label">24K Gold Per Tola</div>

    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">${live_data['gold']:,.0f}</div>
            <div class="stat-label">Ounce</div>
        </div>

        <div class="stat-box">
            <div class="stat-value">Rs {live_data['usd']:.2f}</div>
            <div class="stat-label">Dollar</div>
        </div>

        <div class="stat-box">
            <div class="stat-value">{live_data['time']}</div>
            <div class="stat-label">Last Update</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Manual Refresh Button
if st.button("🔄 Update Gold Price Now"):
    st.cache_data.clear()
    st.rerun()


# -----------------------------
# SILVER CARD
# -----------------------------
st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background:#f0f4f8; color:#4a5568;">● SILVER LIVE</div>
    <div class="big-price" style="font-size:2.5rem;">Rs {silver_tola:,.0f}</div>
    <div class="price-label">Silver Per Tola</div>

    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">${live_data['silver']:,.2f}</div>
            <div class="stat-label">Ounce</div>
        </div>

        <div class="stat-box">
            <div class="stat-value">{live_data['time']}</div>
            <div class="stat-label">Last Update</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# CONTACT BUTTONS
# -----------------------------
st.markdown("""
<div class="btn-grid">
  <a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a>
  <a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# ADMIN LOGIN
# -----------------------------
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if password == "123123":
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Wrong Password ❌")


# -----------------------------
# ADMIN DASHBOARD FIXED BUTTON BUG
# -----------------------------
if st.session_state.admin_auth:
    st.title("⚙️ Admin Dashboard")

    if st.button("🔴 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

    tabs = st.tabs(["Update Prices", "Stats"])

    with tabs[0]:

        if "new_gold" not in st.session_state:
            st.session_state.new_gold = settings["gold_premium"]

        st.subheader("🟡 Gold Premium Update")

        col1, col2, col3 = st.columns([1, 1, 2])

        if col1.button("-500"):
            st.session_state.new_gold -= 500

        if col2.button("+500"):
            st.session_state.new_gold += 500

        st.session_state.new_gold = col3.number_input(
            "Gold Premium",
            value=st.session_state.new_gold,
            step=100
        )

        if st.button("🚀 Publish Premium"):
            new_settings = {
                "gold_premium": st.session_state.new_gold,
                "silver_premium": settings["silver_premium"]
            }

            contents = repo.get_contents("manual.json")
            repo.update_file(contents.path, "Update Premium", json.dumps(new_settings), contents.sha)

            st.success("✅ Premium Updated Successfully!")
            st.rerun()

    with tabs[1]:
        st.metric("Gold Premium", st.session_state.new_gold)
        st.metric("Gold Price Per Tola", f"Rs {gold_tola:,.0f}")


# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<div class="footer">
<b>Islam Jewellery</b> website shows approximate gold prices.<br>
Rates are based on international market data and admin-set premium.<br><br>
⚠️ <b>Disclaimer:</b> Prices may change anytime. Always confirm final rate from the shop before buying.
</div>
""", unsafe_allow_html=True)
