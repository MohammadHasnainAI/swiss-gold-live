import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz
import pandas as pd
import altair as alt

# -------------------------------
# 1. CONFIG
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# 2. CSS STYLING
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* CENTER CONTENT */
.centered {display:flex; justify-content:center; flex-direction:column; align-items:center;}

/* HEADER */
.header-box {text-align:center; padding:20px 0; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; margin-bottom:5px;}
.brand-subtitle {font-size:1rem; color:#d4af37; font-weight:600;}

/* PRICE CARD */
.price-card {background:#ffffff; border-radius:20px; padding:50px 40px; text-align:center; box-shadow:0 15px 40px rgba(0,0,0,0.1); margin-bottom:30px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:8px 18px; border-radius:30px; font-weight:700; font-size:0.85rem; display:inline-block; margin-bottom:20px;}
.closed-badge {background-color:#fce8e6; color:#c5221f; padding:8px 18px; border-radius:30px; font-weight:700; font-size:0.85rem; display:inline-block; margin-bottom:20px;}
.big-price {font-size:4rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-1px;}
.price-label {font-size:1rem; color:#666; font-weight:500; margin-top:10px;}

/* STATS */
.stats-container {display:flex; gap:20px; justify-content:center; margin-bottom:30px;}
.stat-box {flex:1; background:#ffffff; border-radius:15px; padding:20px; text-align:center; box-shadow:0 5px 20px rgba(0,0,0,0.05);}
.stat-value {font-size:1.5rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.85rem; color:#777; font-weight:600; margin-top:5px;}

/* CONTACT BUTTONS */
.btn-grid {display:flex; gap:15px; margin-bottom:40px;}
.contact-btn {flex:1; padding:15px; border-radius:12px; text-align:center; text-decoration:none; font-weight:600; transition:0.2s; box-shadow:0 5px 15px rgba(0,0,0,0.05);}
.btn-call {background-color:#111; color:white !important;}
.btn-whatsapp {background-color:#25D366; color:white !important;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}

/* DISCLAIMER */
.disclaimer {background:#ffffff; border-radius:20px; padding:25px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.05); margin-top:40px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. DATA LOGIC
# -------------------------------
def get_time():
    return datetime.now(pytz.timezone("Asia/Karachi"))

def load_data():
    try:
        with open("prices.json", "r") as f:
            market = json.load(f)
    except:
        market = {"price_ounce_usd": 0, "usd_to_pkr": 0}
    try:
        with open("manual.json", "r") as f:
            manual = json.load(f)
    except:
        manual = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}
    return market, manual

market, manual = load_data()
last_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_dt = pytz.timezone("Asia/Karachi").localize(datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S"))
current_time = get_time()
is_expired = (current_time - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)
pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# 4. AUTO-REFRESH EVERY 10 SECONDS
# -------------------------------
st_autorefresh = st.experimental_rerun
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# -------------------------------
# 5. MAIN WEBSITE DISPLAY (CENTERED)
# -------------------------------
st.markdown('<div class="centered">', unsafe_allow_html=True)
st.markdown(f"""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

# Price Card
if is_expired:
    st.markdown(f"""
    <div class="price-card">
        <div class="closed-badge">● MARKET CLOSED</div>
        <div class="big-price" style="color:#ccc;">PENDING</div>
        <div class="price-label">Waiting for Rate Update</div>
        <div style="font-size:0.85rem; color:#aaa; margin-top:10px;">Last: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge">● LIVE RATE</div>
        <div class="big-price">Rs {pk_price:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div style="font-size:0.85rem; color:#aaa; margin-top:10px;">Updated: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)

# Stats
st.markdown(f"""
<div class="stats-container">
    <div class="stat-box">
        <div class="stat-value">${market['price_ounce_usd']:,.0f}</div>
        <div class="stat-label">Int'l Ounce</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">Rs {market['usd_to_pkr']:.2f}</div>
        <div class="stat-label">USD Rate</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">Rs {manual['premium']}</div>
        <div class="stat-label">Admin Premium</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Contact Buttons
st.markdown("""
<div class="btn-grid">
    <a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a>
    <a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# 6. ADMIN LOGIN / DASHBOARD
# -------------------------------
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

with st.sidebar:
    if not st.session_state.admin_authenticated:
        st.header("Admin Login")
        key_input = st.text_input("Enter Admin Access Key", type="password")
        if st.button("Login"):
            if key_input == "123123":
                st.session_state.admin_authenticated = True
                st.success("Admin Access Granted ✅")
            else:
                st.error("Incorrect Key ❌")
    else:
        st.header("Admin Panel")
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.success("Logged out successfully ✅")

# -------------------------------
# 7. FULL-WIDTH ADMIN DASHBOARD
# -------------------------------
if st.session_state.admin_authenticated:
    st.title("⚙️ Admin Dashboard")
    tabs = st.tabs(["Update Prices", "Stats", "History", "Gold Price Chart"])

    # --- TAB 1: Update Prices ---
    with tabs[0]:
        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = manual["premium"]

        col1, col2 = st.columns(2)
        col1.button("- 500", on_click=lambda: st.session_state.update({"admin_premium": st.session_state.admin_premium-500}))
        col2.button("+ 500", on_click=lambda: st.session_state.update({"admin_premium": st.session_state.admin_premium+500}))
        st.number_input("Profit Margin (Rs)", key="admin_premium", step=100)

        if st.button("🚀 Publish Rate"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                data = {
                    "premium": st.session_state.admin_premium,
                    "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": 4
                }
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Update", json.dumps(data), contents.sha)
                except:
                    repo.create_file("manual.json", "Init", json.dumps(data))

                # History
                try:
                    contents = repo.get_contents("history.json")
                    history = json.loads(contents.decoded_content.decode())
                except:
                    history = []

                history.append({
                    "premium": st.session_state.admin_premium,
                    "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "usd_to_pkr": market["usd_to_pkr"],
                    "price_ounce_usd": market["price_ounce_usd"]
                })

                try:
                    contents = repo.get_contents("history.json")
                    repo.update_file(contents.path, "Append History", json.dumps(history, indent=2), contents.sha)
                except:
                    repo.create_file("history.json", "Init History", json.dumps(history, indent=2))

                st.success("✅ Updated & Logged History!")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- TAB 2: Stats ---
    with tabs[1]:
        st.subheader("Current Stats")
        st.metric("Current Premium", f"Rs {manual['premium']}")
        st.metric("USD to PKR", f"Rs {market['usd_to_pkr']}")
        st.metric("Gold Price/Ounce", f"${market['price_ounce_usd']}")

    # --- TAB 3: History ---
    with tabs[2]:
        st.subheader("Price Update History")
        try:
            g = Github(st.secrets["GIT_TOKEN"])
            repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
            contents = repo.get_contents("history.json")
            history = json.loads(contents.decoded_content.decode())
        except:
            history = []

        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No history yet.")

    # --- TAB 4: Gold Price Chart ---
    with tabs[3]:
        st.subheader("Gold Price Trend")
        if history:
            df = pd.DataFrame(history)
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            chart = alt.Chart(df).mark_line(point=True).encode(
                x='last_updated:T',
                y='price_ounce_usd:Q',
                tooltip=['last_updated:T','price_ounce_usd:Q','usd_to_pkr:Q','premium:Q']
            ).properties(width=1000, height=400)
            st.altair_chart(chart)
        else:
            st.info("No data to show.")

# -------------------------------
# 8. WEBSITE INFO / DISCLAIMER (BOTTOM)
# -------------------------------
st.markdown('<div class="disclaimer">', unsafe_allow_html=True)
st.subheader("Website Info & Disclaimer")
st.markdown("""
**Islam Jewellery** shows approximate gold prices.  
Prices are updated using market data and admin premium.  

⚠️ **Disclaimer:**  
- Prices are indicative and may change anytime.  
- Verify with the shop before buying.  
- Contact shop for confirmed gold rates.
""")
st.markdown('</div>', unsafe_allow_html=True)
