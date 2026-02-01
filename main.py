import streamlit as st
import requests
import json
from datetime import datetime
import pytz
from github import Github
from streamlit_autorefresh import st_autorefresh

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery V11", page_icon="💎", layout="centered")

# ---------------------------------------------------------
# AUTO-REFRESH ENGINE (5 SECONDS)
# ---------------------------------------------------------
st_autorefresh(interval=5000, key="gold_refresh") 

# 2. HELPER FUNCTIONS
def update_premium(key, amount):
    if key not in st.session_state:
        st.session_state[key] = 0
    st.session_state[key] += amount

def manual_refresh():
    get_live_rates.clear()
    load_settings.clear()

# 3. DESIGN & CSS (COMPACT VERSION)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#ffffff; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* --- CRITICAL FIX: REMOVE TOP WHITESPACE --- */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 700px;
}

/* Header - More Compact */
.header-box {text-align:center; padding-bottom:10px; border-bottom:1px solid #f0f0f0; margin-bottom:15px;}
.brand-title {font-size:2.2rem; font-weight:800; color:#111; letter-spacing:-1px; margin-bottom:0px; text-transform:uppercase; line-height: 1.1;}
.brand-subtitle {font-size:0.75rem; color:#d4af37; font-weight:600; letter-spacing:2px; text-transform:uppercase;}

/* Cards - Less Padding */
.price-card {background:#ffffff; border-radius:15px; padding:15px 15px; text-align:center; box-shadow:0 5px 20px rgba(0,0,0,0.06); border:1px solid #f5f5f5; margin-bottom:12px;}
.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:4px 10px; border-radius:30px; font-weight:700; font-size:0.65rem; letter-spacing:1px; display:inline-block; margin-bottom:5px;}
.big-price {font-size:2.8rem; font-weight:800; color:#111; line-height:1; margin:5px 0; letter-spacing:-1px;}
.price-label {font-size:0.9rem; color:#666; font-weight:400; margin-top:2px;}

/* Stats Container */
.stats-container {display:flex; gap:5px; margin-top:10px; justify-content:center; flex-wrap: wrap;}
.stat-box {background:#fafafa; border-radius:8px; padding:8px; text-align:center; border:1px solid #eeeeee; flex: 1; min-width: 70px;}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.55rem; color:#999; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;}

/* Buttons */
.btn-grid {display: flex; gap: 10px; margin-top: 15px; justify-content: center;}
.contact-btn {flex: 1; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: white !important;}
.btn-call {background-color:#111;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {transform:translateY(-2px); opacity:0.9;}

/* Footer */
.footer {background:#f9f9f9; padding:15px; text-align:center; font-size:0.75rem; color:#666; margin-top:20px; border-top:1px solid #eee; line-height: 1.4;}
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

# 5. SETTINGS ENGINE (5 SECONDS)
@st.cache_data(ttl=5, show_spinner=False)
def load_settings():
    default_settings = {"gold_premium": 0, "silver_premium": 0}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            return json.loads(content.decoded_content.decode())
        except:
            pass
    return default_settings

# 6. DATA ENGINE (2 MINUTES)
@st.cache_data(ttl=120, show_spinner=False)
def get_live_rates():
    if "TWELVE_DATA_KEY" not in st.secrets:
        return "ERROR: Secret Keys Missing"
    
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

# 7. LOAD DATA
live_data = get_live_rates()
settings = load_settings()

if isinstance(live_data, str):
    st.warning(f"⚠️ {live_data}")
    live_data = {"gold": 2750.0, "silver": 32.0, "usd": 278.0, "aed": 3.67, "time": "Offline Mode", "full_date": "2024-01-01"}

if "new_gold" not in st.session_state: st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state: st.session_state.new_silver = settings.get("silver_premium", 0)

# 8. CALCULATIONS
gold_tola = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("gold_premium", 0)
silver_tola = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + settings.get("silver_premium", 0)
gold_dubai_tola = (live_data['gold'] / 31.1035) * 11.66 * live_data['aed']

# 9. COMPACT UI DISPLAY
st.markdown("""<div class="header-box"><div class="brand-title">Islam Jewellery</div><div class="brand-subtitle">Sarafa Bazar • Premium Gold</div></div>""", unsafe_allow_html=True)

# GOLD CARD
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
    <div style="font-size:0.65rem; color:#aaa; margin-top:8px; padding-top:8px; border-top:1px solid #eee;">
        Last Updated: <b>{live_data['time']}</b>
    </div>
</div>
""", unsafe_allow_html=True)

# REFRESH BUTTON
if st.button("🔄 Check for New Gold Rate", use_container_width=True):
    manual_refresh()
    st.rerun()

# SILVER CARD
st.markdown(f"""
<div class="price-card">
    <div class="live-badge" style="background-color:#f0f4f8; color:#4a5568;">● SILVER LIVE</div>
    <div class="big-price">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['silver']:,.2f}</div><div class="stat-label">Ounce</div></div>
        <div class="stat-box"><div class="stat-value">{live_data['time']}</div><div class="stat-label">Updated</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 10. ADMIN DASHBOARD
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

    tabs = st.tabs(["Update", "History", "Chart"])

    # TAB 1: Update
    with tabs[0]:
        metal_choice = st.radio("Select Metal:", ["Gold", "Silver"], horizontal=True)

        if metal_choice == "Gold":
            st.subheader("🟡 Gold Premium")
            c1, c2, c3 = st.columns([1,1,2])
            c1.button("- 500", key="g_sub", on_click=update_premium, args=("new_gold", -500))
            c2.button("+ 500", key="g_add", on_click=update_premium, args=("new_gold", 500))
            st.number_input("Gold Premium", key="new_gold", step=100)
        else:
            st.subheader("⚪ Silver Premium")
            d1, d2, d3 = st.columns([1,1,2])
            d1.button("- 50", key="s_sub", on_click=update_premium, args=("new_silver", -50))
            d2.button("+ 50", key="s_add", on_click=update_premium, args=("new_silver", 50))
            st.number_input("Silver Premium", key="new_silver", step=50)

        if st.button("🚀 Publish Rate", type="primary"):
            if repo:
                try:
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
                    except:
                        history = []
                    
                    history.append({
                        "date": live_data['full_date'],
                        "gold_pk": gold_tola,
                        "usd": live_data['usd']
                    })
                    if len(history) > 60: history = history[-60:]

                    try:
                        repo.update_file(h_content.path, "Update Hist", json.dumps(history), h_content.sha)
                    except:
                        repo.create_file("history.json", "Init Hist", json.dumps(history))

                    st.success("✅ Updated! Users see in ~5s.")
                    manual_refresh() 
                    st.rerun()
                except Exception as e:
                    st.error(f"GitHub Error: {e}")
            else:
                st.error("❌ GitHub Connection Failed")

    # TAB 2: History
    with tabs[1]:
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                st.dataframe(pd.DataFrame(history_data))
        except:
            st.info("No history yet.")

    # TAB 3: Chart
    with tabs[2]:
        try:
            if repo and 'df' in locals() and not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                chart = alt.Chart(df).mark_line().encode(x='date:T', y='gold_pk:Q')
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Update price once to see chart.")
        except:
            st.info("Chart unavailable.")

# 11. FOOTER
st.markdown("""
<div class="footer">
**Islam Jewellery** website shows approximate gold prices.<br>
⚠️ **Disclaimer:** Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
