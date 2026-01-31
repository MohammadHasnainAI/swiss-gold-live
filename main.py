import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Islam Jewellery - Gold Rate",
    page_icon="💎",
    layout="wide"
)

# -----------------------------
# Luxury Website CSS
# -----------------------------
st.markdown("""
<style>

body {
    background-color: #0b0b0b;
    color: white;
    font-family: 'Poppins', sans-serif;
}

.main {
    background: linear-gradient(to bottom, #050505, #0d0d0d);
}

/* Title */
.gold-title {
    font-size: 55px;
    font-weight: 800;
    text-align: center;
    color: #d4af37;
    margin-top: 10px;
    letter-spacing: 2px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 16px;
    color: #aaa;
    margin-bottom: 25px;
}

/* Card */
.gold-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(212,175,55,0.25);
    padding: 30px;
    border-radius: 25px;
    box-shadow: 0px 0px 25px rgba(212,175,55,0.12);
    text-align: center;
}

/* Rate Text */
.rate {
    font-size: 42px;
    font-weight: bold;
    color: #d4af37;
}

/* Badge Feature */
.badge {
    display: inline-block;
    background: rgba(212,175,55,0.12);
    border: 1px solid rgba(212,175,55,0.3);
    padding: 8px 18px;
    border-radius: 20px;
    margin: 8px;
    font-size: 14px;
    color: #f5e6a1;
}

/* Buttons */
.action-btn {
    background: rgba(255,255,255,0.05);
    padding: 14px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid rgba(212,175,55,0.25);
    font-weight: 600;
    color: white;
    transition: 0.3s;
}

.action-btn:hover {
    background: rgba(212,175,55,0.15);
    cursor: pointer;
}

/* Sidebar Admin */
section[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid rgba(212,175,55,0.2);
}

input {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(212,175,55,0.25) !important;
    color: white !important;
}

/* Footer */
.footer {
    text-align: center;
    font-size: 12px;
    color: #666;
    padding: 25px;
    margin-top: 50px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Default Data
# -----------------------------
if "gold_rate" not in st.session_state:
    st.session_state.gold_rate = 245000

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Website Header
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-top:15px;">
    <img src="https://cdn-icons-png.flaticon.com/512/263/263142.png" width="75">
</div>

<div class="gold-title">Islam Jewellery</div>

<div class="subtitle">
EST. 1990 • Sarafa Bazar • Premium Gold Rate Display
</div>

<hr style="border:0.5px solid rgba(212,175,55,0.15); margin-bottom:35px;">
""", unsafe_allow_html=True)

# -----------------------------
# Main Gold Rate Card
# -----------------------------
st.markdown(f"""
<div class="gold-card">

    <div style="font-size:18px; color:#bbb;">
        Today's Gold Rate (24K per Tola)
    </div>

    <div class="rate">
        Rs. {st.session_state.gold_rate:,}
    </div>

    <div style="margin-top:20px;">
        <span class="badge">💎 Trusted Since 1990</span>
        <span class="badge">📍 Sarafa Market Live Display</span>
        <span class="badge">✅ Verified Daily Update</span>
    </div>

</div>
""", unsafe_allow_html=True)

# -----------------------------
# Feature 1: Call + WhatsApp Buttons
# -----------------------------
st.markdown("""
<div style="display:flex; gap:18px; margin-top:30px; justify-content:center;">

    <a href="tel:03001234567" style="flex:1; text-decoration:none;">
        <div class="action-btn">📞 Call Now</div>
    </a>

    <a href="https://wa.me/923001234567" target="_blank" style="flex:1; text-decoration:none;">
        <div class="action-btn">💬 WhatsApp Order</div>
    </a>

</div>
""", unsafe_allow_html=True)

# -----------------------------
# Feature 2: Gold Rate History Table
# -----------------------------
st.markdown("<br><h3 style='color:#d4af37;'>📌 Rate Update History</h3>", unsafe_allow_html=True)

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No updates yet. Admin will update rate from dashboard.")

# -----------------------------
# Sidebar Admin Dashboard
# -----------------------------
st.sidebar.markdown("""
<h2 style="color:#d4af37; text-align:center;">
🔐 Admin Dashboard
</h2>
<hr style="border:0.5px solid rgba(212,175,55,0.2);">
""", unsafe_allow_html=True)

password = st.sidebar.text_input("Enter Admin Password", type="password")

if password == "admin123":

    st.sidebar.success("Access Granted ✅")

    new_rate = st.sidebar.number_input(
        "Update Gold Rate (Rs.)",
        min_value=1000,
        step=500,
        value=st.session_state.gold_rate
    )

    if st.sidebar.button("💾 Save New Rate"):

        st.session_state.gold_rate = new_rate

        st.session_state.history.insert(0, {
            "Date": datetime.now().strftime("%d-%b-%Y"),
            "Time": datetime.now().strftime("%I:%M %p"),
            "New Rate": f"Rs. {new_rate:,}"
        })

        st.sidebar.success("Gold Rate Updated Successfully!")

else:
    st.sidebar.warning("Enter correct password to manage rates.")

# -----------------------------
# Feature 3: Professional Footer
# -----------------------------
st.markdown("""
<div class="footer">
<hr style="border:0.5px solid rgba(212,175,55,0.12);">
© 2026 Islam Jewellery • Premium Gold Rate Display System <br>
Designed for Sarafa Market Professional Shops
</div>
""", unsafe_allow_html=True)
