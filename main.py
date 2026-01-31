import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# -------------------------------
# 1. CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="centered"
)

# -------------------------------
# 2. EUROPEAN CLEAN CSS (White & Gold)
# -------------------------------
st.markdown("""
<style>
/* Import Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

/* MAIN BACKGROUND - CLEAN WHITE */
.stApp {
    background-color: #ffffff;
    font-family: 'Outfit', sans-serif;
    color: #333333;
}

/* HIDE STREAMLIT ELEMENTS */
#MainMenu, footer, header {
    visibility: hidden;
}

/* HEADER STYLE */
.header-box {
    text-align: center;
    padding-bottom: 30px;
    border-bottom: 1px solid #f0f0f0;
    margin-bottom: 30px;
}

.brand-title {
    font-size: 3rem;
    font-weight: 800;
    color: #111;
    letter-spacing: -1px;
    margin-bottom: 5px;
    text-transform: uppercase;
}

.brand-subtitle {
    font-size: 0.9rem;
    color: #d4af37; /* Gold */
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* MAIN CARD STYLE (European Minimalist) */
.price-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 40px 20px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08); /* Soft Shadow */
    border: 1px solid #f5f5f5;
    margin-bottom: 30px;
}

.live-badge {
    background-color: #e6f4ea;
    color: #1e8e3e;
    padding: 8px 16px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 20px;
}

.closed-badge {
    background-color: #fce8e6;
    color: #c5221f;
    padding: 8px 16px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 1px;
    display: inline-block;
    margin-bottom: 20px;
}

.big-price {
    font-size: 4.5rem;
    font-weight: 800;
    color: #111;
    line-height: 1;
    margin: 10px 0;
    letter-spacing: -2px;
}

.price-label {
    font-size: 1rem;
    color: #666;
    font-weight: 400;
    margin-top: 10px;
}

/* STATS GRID */
.stats-container {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}

.stat-box {
    flex: 1;
    background: #fafafa;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    border: 1px solid #eeeeee;
}

.stat-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #d4af37; /* Gold */
}

.stat-label {
    font-size: 0.75rem;
    color: #999;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 5px;
}

/* CONTACT BUTTONS */
.btn-grid {
    display: flex;
    gap: 15px;
    margin-top: 30px;
}

.contact-btn {
    flex: 1;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}
.btn-call {
    background-color: #111;
    color: white !important;
}
.btn-whatsapp {
    background-color: #25D366;
    color: white !important;
}
.contact-btn:hover {
    transform: translateY(-2px);
    opacity: 0.9;
}

/* ADMIN SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #f9f9f9;
    border-right: 1px solid #eee;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. LOGIC (AUTO UPDATER)
# -------------------------------
def get_time():
    return datetime.now(pytz.timezone("Asia/Karachi"))

def load_data():
    # Load Market Data
    try:
        with open("prices.json", "r") as f:
            market = json.load(f)
    except:
        market = {"price_ounce_usd": 0, "usd_to_pkr": 0}

    # Load Manual Settings
    try:
        with open("manual.json", "r") as f:
            manual = json.load(f)
    except:
        manual = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}

    return market, manual

# Load Data
market, manual = load_data()

# Calculate Expiry
last_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_dt = pytz.timezone("Asia/Karachi").localize(
    datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
)
current_time = get_time()
is_expired = (current_time - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)

# Calculate Final Price
pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# 4. MAIN DISPLAY
# -------------------------------

# Header
st.markdown("""
<div class="header-box">
    <div class="brand-title">Islam Jewellery</div>
    <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

if is_expired:
    # CLOSED STATE
    st.markdown(f"""
    <div class="price-card">
        <div class="closed-badge">● MARKET CLOSED</div>
        <div class="big-price" style="color: #ccc;">PENDING</div>
        <div class="price-label">Waiting for Rate Update</div>
        <div style="font-size: 0.8rem; color: #aaa; margin-top: 15px;">Last: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # LIVE STATE
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge">● LIVE RATE</div>
        <div class="big-price">Rs {pk_price:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div style="font-size: 0.8rem; color: #aaa; margin-top: 15px;">Updated: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)

    # STATS GRID
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
    </div>
    """, unsafe_allow_html=True)

    # BUTTONS
    st.markdown("""
    <div class="btn-grid">
        <a href="tel:03001234567" class="contact-btn btn-call">📞 Call Now</a>
        <a href="https://wa.me/923001234567" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# 5. ADMIN PANEL (SIDEBAR)
# -------------------------------
st.sidebar.markdown("### ⚙️ Admin")
st.sidebar.markdown("---")

with st.sidebar.expander("Update Price"):
    pwd = st.text_input("Access Key", type="password")

    if pwd == "123123":
        st.success("Authorized")
        
        # Memory State for Calculator
        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = int(manual["premium"])

        def update_val(val):
            st.session_state.admin_premium += val

        # Calculator Buttons
        c1, c2 = st.columns(2)
        c1.button("- 500", on_click=update_val, args=(-500,))
        c2.button("+ 500", on_click=update_val, args=(500,))

        # Input Box
        st.number_input("Profit Margin (Rs)", key="admin_premium", step=100)
        
        # Save Button
        if st.button("🚀 Publish Rate"):
            try:
                # GitHub Connection
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                
                # Data Payload
                data = {
                    "premium": st.session_state.admin_premium,
                    "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": 4
                }
                
                # Push to GitHub
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Update", json.dumps(data), contents.sha)
                except:
                    repo.create_file("manual.json", "Init", json.dumps(data))
                
                st.success("Updated! Reloading...")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
