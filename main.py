import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# -------------------------------
# 1. CONFIG
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="centered"
)

# -------------------------------
# 2. FULL LUXURY CSS (FINAL)
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Outfit:wght@300;500;700&display=swap');

.stApp {
    background: linear-gradient(to bottom, #050505, #0d0d0d);
    font-family: 'Outfit', sans-serif;
    color: white;
}

#MainMenu, footer, header {
    visibility: hidden;
}

/* GOLD TITLE */
.gold-title {
    font-family: 'Playfair Display', serif;
    font-size: 52px;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #FFD700, #D4AF37, #FFF2B0);
    -webkit-background-clip: text;
    color: transparent;
    margin-top: 10px;
    text-shadow: 0px 0px 30px rgba(212, 175, 55, 0.3);
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    font-size: 14px;
    color: #888;
    letter-spacing: 3px;
    margin-bottom: 35px;
    text-transform: uppercase;
}

/* MAIN GLASS CARD */
.glass-panel {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 30px;
    padding: 50px;
    box-shadow: 0 0 40px rgba(212,175,55,0.15);
    text-align: center;
    margin-bottom: 25px;
    backdrop-filter: blur(10px);
}

/* PRICE TEXT */
.price-text {
    font-size: 85px;
    font-weight: 800;
    color: white;
    text-shadow: 0 0 25px rgba(212,175,55,0.6);
    margin: 15px 0;
    line-height: 1;
}

/* LIVE DOT */
.live-dot {
    color: #00ff99;
    font-weight: bold;
    letter-spacing: 2px;
    font-size: 14px;
}

/* STATS GRID */
.stat-grid {
    display: flex;
    gap: 15px;
    margin-top: 10px;
}

.stat-card {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 18px;
    text-align: center;
}

.stat-val {
    font-size: 22px;
    font-weight: 700;
    color: #FFD700;
}

.stat-lbl {
    font-size: 11px;
    color: #aaa;
    letter-spacing: 2px;
    margin-top: 5px;
    text-transform: uppercase;
}

/* PREMIUM BUTTONS */
.stButton button {
    background: linear-gradient(90deg, #D4AF37, #FFD700) !important;
    color: black !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 10px !important;
    border: none !important;
    transition: 0.3s !important;
}

.stButton button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 15px rgba(255,215,0,0.5);
}

/* SIDEBAR STYLE */
section[data-testid="stSidebar"] {
    background-color: #0c0c0c !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ADMIN INPUTS LUXURY */
input {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
    color: white !important;
}

.stNumberInput input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. FUNCTIONS
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

# -------------------------------
# 4. LOAD DATA
# -------------------------------
market, manual = load_data()

last_str = manual.get("last_updated")
last_dt = pytz.timezone("Asia/Karachi").localize(
    datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
)

is_expired = (get_time() - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)

pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# 5. HEADER
# -------------------------------
st.markdown("""
<div style="text-align:center; margin-top:15px;">
    <img src="https://cdn-icons-png.flaticon.com/512/263/263142.png" width="70">
</div>

<div class='gold-title'>Islam Jewellery</div>

<div class='subtitle'>
EST. 1990 • Sarafa Bazar • Premium Gold Rates
</div>

<hr style="border:0.5px solid rgba(212,175,55,0.2); margin-bottom:30px;">
""", unsafe_allow_html=True)

# -------------------------------
# 6. MAIN DISPLAY
# -------------------------------
if is_expired:
    st.markdown(f"""
    <div class='glass-panel' style='border-color:#ff4444;'>
        <div style='color:#ff4444; font-weight:bold;'>● MARKET CLOSED</div>
        <div class='price-text' style='color:#666; font-size:60px;'>PENDING</div>
        <div style="font-size:15px; color:#aaa;">Rates are being updated...</div>
        <div style="margin-top:20px; font-size:18px;">📞 0300-1234567</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class='glass-panel'>
        <div class='live-dot'>● LIVE GOLD RATE</div>
        <div class='price-text'>Rs {pk_price:,.0f}</div>
        <div style="font-size:15px; color:#bbb;">24K Gold Per Tola</div>
        <div style="font-size:12px; color:#666; margin-top:15px;">
            Updated: {last_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    st.markdown(f"""
    <div class='stat-grid'>
        <div class='stat-card'>
            <div class='stat-val'>${market['price_ounce_usd']:,.0f}</div>
            <div class='stat-lbl'>International Ounce</div>
        </div>

        <div class='stat-card'>
            <div class='stat-val'>Rs {market['usd_to_pkr']:.2f}</div>
            <div class='stat-lbl'>USD Exchange</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CALL + WHATSAPP BUTTONS
    st.markdown("""
    <div style="display:flex; gap:15px; margin-top:25px;">

        <a href="tel:03001234567" style="flex:1; text-decoration:none;">
            <div style="
                background:rgba(255,255,255,0.04);
                padding:15px;
                border-radius:15px;
                text-align:center;
                border:1px solid rgba(212,175,55,0.2);
                font-weight:600;
                color:white;">
                📞 Call Now
            </div>
        </a>

        <a href="https://wa.me/923001234567" target="_blank" style="flex:1; text-decoration:none;">
            <div style="
                background:rgba(255,255,255,0.04);
                padding:15px;
                border-radius:15px;
                text-align:center;
                border:1px solid rgba(212,175,55,0.2);
                font-weight:600;
                color:white;">
                💬 WhatsApp
            </div>
        </a>

    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# 7. FOOTER
# -------------------------------
st.markdown("""
<hr style="border:0.5px solid rgba(212,175,55,0.15); margin-top:50px;">

<div style="text-align:center; font-size:12px; color:#666; padding-bottom:20px;">
© 2026 Islam Jewellery • Live Gold Rates Updated Daily <br>
Designed for Professional Sarafa Business
</div>
""", unsafe_allow_html=True)

# -------------------------------
# 8. ADMIN PANEL
# -------------------------------
st.sidebar.markdown("---")

with st.sidebar.expander("🔒 Admin Panel"):
    pwd = st.text_input("Access Key", type="password")

    if pwd == "123123":
        st.success("Welcome, Owner 👑")

        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = int(manual["premium"])

        def change_val(amount):
            st.session_state.admin_premium += amount

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.button("-500", on_click=change_val, args=(-500,))
        with c2:
            st.button("-100", on_click=change_val, args=(-100,))
        with c3:
            st.button("+100", on_click=change_val, args=(100,))
        with c4:
            st.button("+500", on_click=change_val, args=(500,))

        st.number_input("Profit Margin", key="admin_premium", step=100)

        if st.button("🚀 UPDATE LIVE RATE"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")

                data = {
                    "premium": st.session_state.admin_premium,
                    "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": 4
                }

                try:
                    repo.update_file(
                        "manual.json",
                        "Update premium",
                        json.dumps(data),
                        repo.get_contents("manual.json").sha
                    )
                except:
                    repo.create_file("manual.json", "Init file", json.dumps(data))

                st.success("✅ Updated Successfully!")
                time.sleep(2)
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")
