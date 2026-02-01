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
# 1. PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Islam Jewellery Pro", page_icon="💎", layout="wide")

# -----------------------------
# 2. HELPER FUNCTIONS
# -----------------------------
def update_premium(key, amount):
    if key not in st.session_state: st.session_state[key] = 0
    st.session_state[key] += amount

def manual_refresh():
    get_live_rates.clear()
    load_settings.clear()

# -----------------------------
# 3. CSS DESIGN (Professional Theme)
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* CUSTOMER VIEW CARDS */
.header-box {text-align:center; padding-bottom:20px; margin-bottom:30px;}
.brand-title {font-size:3rem; font-weight:800; color:#111; letter-spacing:-1px; text-transform:uppercase;}
.brand-subtitle {font-size:0.9rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

.price-card {background:#ffffff; border-radius:20px; padding:30px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.05); border:1px solid #fff; margin-bottom:20px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:6px 14px; border-radius:30px; font-weight:700; font-size:0.75rem; letter-spacing:1px; display:inline-block; margin-bottom:15px;}
.big-price {font-size:3.5rem; font-weight:800; color:#111; line-height:1; margin:10px 0; letter-spacing:-2px;}
.stats-container {display:flex; gap:10px; margin-top:15px; justify-content:center; flex-wrap: wrap;}
.stat-box {background:#f8f9fa; border-radius:10px; padding:10px; text-align:center; border:1px solid #eee; flex: 1; min-width: 90px;}
.stat-value {font-size:1.0rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.65rem; color:#999; font-weight:600; letter-spacing:1px; text-transform:uppercase;}

/* ADMIN DASHBOARD STYLES */
.admin-card {background:#fff; padding:20px; border-radius:15px; border-left: 5px solid #d4af37; box-shadow:0 4px 15px rgba(0,0,0,0.05);}
.status-dot {height: 10px; width: 10px; background-color: #2ecc71; border-radius: 50%; display: inline-block; margin-right: 5px;}
.metric-label {font-size:0.8rem; color:#888; text-transform:uppercase; letter-spacing:1px;}
.metric-value {font-size:1.8rem; font-weight:700; color:#333;}

.btn-grid {display: flex; gap: 15px; margin-top: 30px; justify-content: center;}
.contact-btn {flex: 1; padding: 15px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: 600; color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}

.footer {text-align:center; font-size:0.8rem; color:#aaa; margin-top:50px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 4. DATA ENGINE
# -----------------------------
repo = None 
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except:
    pass

@st.cache_data(ttl=30, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets: return "ERROR"
    TD_KEY = st.secrets["TWELVE_DATA_KEY"]
    CURR_KEY = st.secrets["CURR_KEY"]
    try:
        metal_res = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={TD_KEY}").json()
        curr_res = requests.get(f"https://v6.exchangerate-api.com/v6/{CURR_KEY}/latest/USD").json()
        
        gold = float(metal_res['XAU/USD']['price']) if "price" in metal_res.get('XAU/USD', {}) else 2750.0
        silver = float(metal_res['XAG/USD']['price']) if "price" in metal_res.get('XAG/USD', {}) else 32.0
        
        return {
            "gold": gold, "silver": silver,
            "usd_bank": curr_res.get('conversion_rates', {}).get('PKR', 278.0),
            "aed": curr_res.get('conversion_rates', {}).get('AED', 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except: return "ERROR"

@st.cache_data(ttl=30, show_spinner=False)
def load_settings():
    try:
        if repo:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
    except: pass
    return {"gold_premium": 0, "silver_premium": 0}

# Load Data
live_data = get_live_rates()
if live_data == "ERROR": live_data = {"gold": 2750.0, "silver": 32.0, "usd_bank": 278.0, "aed": 3.67, "time": "Offline", "full_date": "2024-01-01"}
settings = load_settings()

# Initialize Inputs
if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)

# Calculations
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd_bank']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd_bank']) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# -----------------------------
# 5. SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("💎 Islam Jewellery")
page = st.sidebar.radio("Navigation", ["🏠 Home Screen", "⚙️ Admin Dashboard"])

if page == "🏠 Home Screen":
    # Only Auto-Refresh on the Customer View (Prevents Admin Typing bugs)
    st_autorefresh(interval=30000, key="home_refresh")

    # HOME PAGE UI
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)
        
        # Gold Card
        st.markdown(f"""
        <div class="price-card">
            <div class="live-badge">● GOLD LIVE</div>
            <div class="big-price">Rs {gold_tola:,.0f}</div>
            <div class="stats-container">
                <div class="stat-box"><div class="stat-value">${live_data['gold']:,.0f}</div><div class="stat-label">Ounce</div></div>
                <div class="stat-box"><div class="stat-value">Rs {live_data['usd_bank']:.2f}</div><div class="stat-label">Dollar</div></div>
                <div class="stat-box"><div class="stat-value">AED {gold_dubai_tola:,.0f}</div><div class="stat-label">Dubai Tola</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Refresh Rates", use_container_width=True):
            manual_refresh()
            st.rerun()

        # Silver Card
        st.markdown(f"""
        <div class="price-card" style="margin-top:20px;">
            <div class="live-badge" style="background:#f0f4f8; color:#555;">● SILVER LIVE</div>
            <div class="big-price" style="font-size:2.5rem;">Rs {silver_tola:,.0f}</div>
            <div class="stats-container">
                <div class="stat-box"><div class="stat-value">${live_data['silver']:,.2f}</div><div class="stat-label">Ounce</div></div>
                <div class="stat-box"><div class="stat-value">{live_data['time']}</div><div class="stat-label">Update</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class="footer">⚠️ <b>Disclaimer:</b> Prices are indicative. Confirm with shop.</div>""", unsafe_allow_html=True)

elif page == "⚙️ Admin Dashboard":
    # ADMIN PAGE UI
    if "admin_auth" not in st.session_state: st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        st.sidebar.markdown("---")
        with st.sidebar.expander("🔒 Login Required", expanded=True):
            pwd = st.text_input("Password", type="password")
            if st.button("Login"):
                if pwd == "123123":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong Password")
        st.info("👈 Please login from the Sidebar to access the Control Panel.")
    else:
        # LOGGED IN VIEW
        st.sidebar.success("✅ Logged In")
        if st.sidebar.button("Logout"):
            st.session_state.admin_auth = False
            st.rerun()

        st.title("⚙️ Control Room")
        st.markdown(f"**System Status:** <span class='status-dot'></span> Online | **Last Sync:** {live_data['time']}", unsafe_allow_html=True)
        st.markdown("---")

        # Top Metrics
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"<div class='admin-card'><div class='metric-label'>Current Gold Price</div><div class='metric-value'>Rs {gold_tola:,.0f}</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='admin-card' style='border-left-color:#3498db;'><div class='metric-label'>Current Premium</div><div class='metric-value'>Rs {settings.get('gold_premium', 0)}</div></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='admin-card' style='border-left-color:#2ecc71;'><div class='metric-label'>Dollar Rate</div><div class='metric-value'>Rs {live_data['usd_bank']:.2f}</div></div>", unsafe_allow_html=True)

        st.markdown("### 🛠️ Adjust Prices")
        
        tab_ctrl, tab_hist, tab_chart = st.tabs(["🎛️ Adjustments", "📜 History", "📈 Charts"])

        with tab_ctrl:
            col_gold, col_silver = st.columns(2)
            
            with col_gold:
                st.info("🟡 **Gold Premium**")
                c1, c2 = st.columns(2)
                c1.button("➖ 500", key="g_sub", on_click=update_premium, args=("new_gold", -500), use_container_width=True)
                c2.button("➕ 500", key="g_add", on_click=update_premium, args=("new_gold", 500), use_container_width=True)
                st.number_input("Value (Rs)", key="new_gold", step=100)

            with col_silver:
                st.info("⚪ **Silver Premium**")
                d1, d2 = st.columns(2)
                d1.button("➖ 50", key="s_sub", on_click=update_premium, args=("new_silver", -50), use_container_width=True)
                d2.button("➕ 50", key="s_add", on_click=update_premium, args=("new_silver", 50), use_container_width=True)
                st.number_input("Value (Rs)", key="new_silver", step=50)

            st.markdown("---")
            if st.button("🚀 PUBLISH CHANGES TO LIVE WEBSITE", type="primary", use_container_width=True):
                if repo:
                    try:
                        # Update Settings
                        new_settings = {"gold_premium": st.session_state.new_gold, "silver_premium": st.session_state.new_silver}
                        try:
                            contents = repo.get_contents("manual.json")
                            repo.update_file(contents.path, "Update", json.dumps(new_settings), contents.sha)
                        except:
                            repo.create_file("manual.json", "Init", json.dumps(new_settings))
                        
                        # Update History
                        try:
                            h_content = repo.get_contents("history.json")
                            history = json.loads(h_content.decoded_content.decode())
                        except: history = []
                        
                        history.append({"date": live_data['full_date'], "gold_pk": gold_tola, "premium": st.session_state.new_gold})
                        if len(history) > 60: history = history[-60:]

                        try:
                            repo.update_file(h_content.path, "Update Hist", json.dumps(history), h_content.sha)
                        except:
                            repo.create_file("history.json", "Init Hist", json.dumps(history))

                        st.toast("✅ Changes Published Successfully!", icon="🎉")
                        manual_refresh()
                    except Exception as e:
                        st.error(f"GitHub Error: {e}")
                else:
                    st.error("❌ GitHub Not Connected")

        with tab_hist:
            try:
                if repo:
                    contents = repo.get_contents("history.json")
                    df = pd.DataFrame(json.loads(contents.decoded_content.decode()))
                    st.dataframe(df, use_container_width=True)
            except: st.warning("No history found.")

        with tab_chart:
            try:
                if repo and 'df' in locals() and not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    chart = alt.Chart(df).mark_line().encode(x='date:T', y='gold_pk:Q', tooltip=['date', 'gold_pk'])
                    st.altair_chart(chart, use_container_width=True)
            except: st.warning("No chart data yet.")
