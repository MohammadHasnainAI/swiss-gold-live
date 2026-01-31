import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Islam Jewellery",
    page_icon="💎",
    layout="centered"
)

# -------------------------------
# PREMIUM EUROPEAN UI CSS
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

.stApp {
    background: #f6f7fb;
    font-family: 'Inter', sans-serif;
    color: #111;
}

#MainMenu, header, footer {
    visibility: hidden;
}

/* HEADER */
.brand-header {
    text-align: center;
    margin-top: 15px;
    margin-bottom: 35px;
}

.brand-logo {
    font-size: 45px;
    margin-bottom: 8px;
}

.brand-name {
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -1px;
}

.brand-sub {
    font-size: 0.85rem;
    color: #6c757d;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* MAIN CARD */
.euro-card {
    background: white;
    border-radius: 18px;
    padding: 45px;
    border: 1px solid #eaeaea;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.06);
    text-align: center;
}

/* LIVE BADGE */
.status-badge {
    display: inline-block;
    padding: 7px 18px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 20px;
}

.live {
    background: #e6fcf5;
    color: #087f5b;
}

.closed {
    background: #fff5f5;
    color: #c92a2a;
}

/* PRICE */
.main-price {
    font-size: 4.8rem;
    font-weight: 800;
    letter-spacing: -2px;
    margin: 10px 0;
    color: #111;
}

.price-label {
    font-size: 1rem;
    color: #868e96;
    font-weight: 600;
}

.update-time {
    font-size: 0.8rem;
    color: #adb5bd;
    margin-top: 18px;
}

/* STATS */
.stats-container {
    display: flex;
    gap: 15px;
    margin-top: 18px;
}

.stat-box {
    flex: 1;
    background: white;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #eee;
    box-shadow: 0px 5px 12px rgba(0,0,0,0.03);
}

.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
}

.stat-title {
    font-size: 0.75rem;
    margin-top: 6px;
    color: #868e96;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* BUTTONS */
.action-btn {
    flex: 1;
    padding: 14px;
    border-radius: 12px;
    text-align: center;
    font-weight: 700;
    text-decoration: none;
    transition: 0.2s;
}

.call-btn {
    background: #111;
    color: white;
}

.call-btn:hover {
    background: #333;
}

.wa-btn {
    background: #25D366;
    color: white;
}

.wa-btn:hover {
    background: #1da851;
}

/* FOOTER */
.footer {
    text-align: center;
    font-size: 0.75rem;
    color: #adb5bd;
    margin-top: 45px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FUNCTIONS
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
# LOAD DATA
# -------------------------------
market, manual = load_data()

last_str = manual.get("last_updated")
last_dt = pytz.timezone("Asia/Karachi").localize(
    datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
)

is_expired = (get_time() - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)

pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div class="brand-header">
    <div class="brand-logo">💎</div>
    <h1 class="brand-name">Islam Jewellery</h1>
    <div class="brand-sub">Sarafa Bazar • Est. 1990</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------
# MAIN DISPLAY
# -------------------------------
if is_expired:
    st.markdown("""
    <div class="euro-card">
        <div class="status-badge closed">● Market Closed</div>
        <div class="main-price" style="color:#dee2e6;">Pending</div>
        <div class="price-label">Waiting for Update</div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="euro-card">
        <div class="status-badge live">● Live Gold Rate</div>
        <div class="main-price">Rs {pk_price:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div class="update-time">Last Updated: {last_str}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">${market['price_ounce_usd']:,.0f}</div>
            <div class="stat-title">International Ounce</div>
        </div>

        <div class="stat-box">
            <div class="stat-value">Rs {market['usd_to_pkr']:.2f}</div>
            <div class="stat-title">USD Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; gap:12px; margin-top:20px;">
        <a href="tel:03001234567" class="action-btn call-btn">📞 Call Now</a>
        <a href="https://wa.me/923001234567" target="_blank" class="action-btn wa-btn">💬 WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<div class="footer">
© 2026 Islam Jewellery • Professional Live Gold Rate System
</div>
""", unsafe_allow_html=True)

# -------------------------------
# ADMIN PANEL
# -------------------------------
st.sidebar.title("⚙️ Admin Panel")

with st.sidebar.expander("Update Premium"):
    pwd = st.text_input("Access Key", type="password")

    if pwd == "123123":

        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = int(manual["premium"])

        st.number_input("Premium Amount", key="admin_premium", step=100)

        if st.button("Save & Publish"):
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

                st.success("✅ Updated Successfully!")
                time.sleep(2)
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")
