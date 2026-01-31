import streamlit as st
import json

# --- SWISS CONFIGURATION ---
st.set_page_config(page_title="Gold Market", layout="centered")

# Minimalist Black & White Design
st.markdown("""
    <style>
        .stApp {background-color: #FFFFFF; font-family: 'Arial', sans-serif;}
        h1, h2, h3 {color: #000000; font-weight: 700; letter-spacing: -0.5px;}
        div[data-testid="stMetricValue"] {color: #000000; font-size: 36px !important; font-weight: 700;}
        div[data-testid="stMetricLabel"] {color: #666666; font-size: 14px !important; text-transform: uppercase;}
        hr {border-color: #000000;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
try:
    with open("prices.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    st.warning("System Initializing. Please wait.")
    st.stop()

# --- ADMIN PREMIUM ---
premium = st.secrets.get("PREMIUM", 0)

# --- CALCULATIONS ---
ounce = data['price_ounce_usd']
usd_pkr = data['usd_to_pkr']
usd_aed = data['usd_to_aed']

dubai_gram = (ounce / 31.1035) * usd_aed
pak_tola = ((ounce / 31.1035) * 11.66 * usd_pkr) + premium

# --- DISPLAY ---
st.title("MARKET DATA")
st.caption(f"UPDATED: {data['timestamp']}")
st.markdown("---")

# Global
c1, c2 = st.columns(2)
c1.metric("Gold Ounce (USD)", f"${ounce:,.2f}")
c2.metric("USD / PKR", f"{usd_pkr:.2f}")

st.markdown("---")

# Local
c3, c4 = st.columns(2)
c3.metric("Dubai (Gram)", f"AED {dubai_gram:,.2f}")
c4.metric("Pakistan (Tola)", f"Rs {pak_tola:,.0f}")
