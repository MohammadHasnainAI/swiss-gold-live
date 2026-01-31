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
# 2. PROFESSIONAL PREMIUM CSS
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

.stApp {
    background-color: #ffffff;
    font-family: 'Outfit', sans-serif;
    color: #111;
}

#MainMenu, footer, header {
    visibility: hidden;
}

/* HEADER */
.header-box {
    text-align: center;
    padding-bottom: 25px;
    border-bottom: 1px solid #eee;
    margin-bottom: 25px;
}

.brand-title {
    font-size: 2.8rem;
    font-weight: 800;
    text-transform: uppercase;
}

.brand-subtitle {
    font-size: 0.9rem;
    color: #d4af37;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* MAIN CARD */
.price-card {
    background: white;
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    border: 1px solid #f2f2f2;
    margin-bottom: 25px;
}

.big-price {
    font-size: 4.3rem;
    font-weight: 800;
    margin: 10px 0;
}

.live-badge {
    background: #e6f4ea;
    color: #1e8e3e;
    padding: 8px 18px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 0.8rem;
}

.closed-badge {
    background: #fce8e6;
    color: #c5221f;
    padding: 8px 18px;
    border-radius: 25px;
    font-weight: 700;
    font-size: 0.8rem;
}

/* TRUST BADGES */
.trust-box span {
    display: inline-block;
    margin: 6px;
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* STATS */
.stats-container {
    display: flex;
    gap: 15px;
    margin-top: 15px;
}

.stat-box {
    flex: 1;
    background: #fafafa;
    border-radius: 15px;
    padding: 20px;
    border: 1px solid #eee;
    text-align: center;
}

.stat-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #d4af37;
}

.stat-label {
    font-size: 0.75rem;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* BUTTONS */
.btn-grid {
    display: flex;
    gap: 15px;
    margin-top: 25px;
}

.contact-btn {
    flex: 1;
    padding: 14px;
    border-radius: 12px;
    font-weight: 700;
    text-decoration: none;
    text-align: center;
}

.btn-call {
    background: black;
    color: white !important;
}

.btn-whatsapp {
    background: #25D366;
    color: white !important;
}

/* ADMIN DASHBOARD */
.admin-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 25px;
    border: 1px solid #eee;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    margin-top: 20px;
}

.admin-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #d4af37;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# 3. TIME + DATA LOADER
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

# Expiry Check
last_str = manual.get("last_updated")
last_dt = pytz.timezone("Asia/Karachi").localize(
    datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
)

is_expired = (get_time() - last_dt).total_seconds() / 3600 > manual["valid_hours"]

# Final Price
pk_price = ((market["price_ounce_usd"] / 31.1035) * 11.66 * market["usd_to_pkr"]) + manual["premium"]

# -------------------------------
# 4. NAVIGATION MENU
# -------------------------------
page = st.sidebar.radio("📌 Navigation", ["🏠 Live Rate", "⚙️ Admin Dashboard"])

# -------------------------------
# PAGE 1: CUSTOMER VIEW
# -------------------------------
if page == "🏠 Live Rate":

    st.markdown("""
    <div class="header-box">
        <img src="https://cdn-icons-png.flaticon.com/512/263/263142.png" width="70">
        <div class="brand-title">Islam Jewellery</div>
        <div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
    </div>
    """, unsafe_allow_html=True)

    if is_expired:
        st.markdown(f"""
        <div class="price-card">
            <div class="closed-badge">● MARKET CLOSED</div>
            <div class="big-price" style="color:#ccc;">PENDING</div>
            <p>Waiting for Update</p>
            <small>Last: {last_str}</small>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="price-card">
            <div class="live-badge">● LIVE RATE</div>
            <div class="big-price">Rs {pk_price:,.0f}</div>
            <p>24K Gold Per Tola</p>

            <div class="trust-box">
                <span style="background:#fff8e1;color:#b8860b;">💎 Trusted Since 1990</span>
                <span style="background:#f1f8ff;color:#0b5394;">✅ Verified Rate</span>
                <span style="background:#f9f9f9;color:#333;">📍 Sarafa Market</span>
            </div>

            <small>Updated: {last_str}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">${market['price_ounce_usd']:,.0f}</div>
                <div class="stat-label">Ounce</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Rs {market['usd_to_pkr']:.2f}</div>
                <div class="stat-label">USD Rate</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="btn-grid">
            <a href="tel:03001234567" class="contact-btn btn-call">📞 Call Now</a>
            <a href="https://wa.me/923001234567" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------
# PAGE 2: FULL ADMIN DASHBOARD
# -------------------------------
if page == "⚙️ Admin Dashboard":

    st.markdown("<div class='admin-title'>⚙️ Admin Dashboard</div>", unsafe_allow_html=True)
    st.write("Manage your daily gold premium easily.")

    pwd = st.text_input("Enter Admin Key", type="password")

    if pwd != "123123":
        st.warning("Enter correct password to access admin panel.")

    else:
        st.success("Access Granted ✅")

        st.markdown("<div class='admin-card'>", unsafe_allow_html=True)

        st.subheader("💰 Premium Control")

        if "admin_premium" not in st.session_state:
            st.session_state.admin_premium = int(manual["premium"])

        col1, col2, col3 = st.columns(3)

        if col1.button("➖ -500"):
            st.session_state.admin_premium -= 500

        if col2.button("➕ +500"):
            st.session_state.admin_premium += 500

        st.number_input("Premium Amount (Rs)", key="admin_premium", step=100)

        st.divider()

        if st.button("🚀 Publish Rate Update"):

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
                    repo.update_file(contents.path, "Update Premium", json.dumps(data), contents.sha)
                except:
                    repo.create_file("manual.json", "Init Premium", json.dumps(data))

                st.success("Rate Updated Successfully ✅")
                time.sleep(2)
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<hr style="margin-top:50px;">
<div style="text-align:center;font-size:0.8rem;color:#888;padding:15px;">
© 2026 Islam Jewellery • Professional Gold Rate System
</div>
""", unsafe_allow_html=True)
