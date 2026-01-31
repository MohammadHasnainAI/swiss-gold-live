import streamlit as st
import json
import time
import requests
from github import Github
from datetime import datetime, timedelta
import pytz

# --- CONFIGURATION ---
st.set_page_config(page_title="Islam Jewellery", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        .stApp {background-color: #FFFFFF; font-family: 'Arial', sans-serif;}
        h1 {color: #000000; font-weight: 800; letter-spacing: -1px;}
        .status-box {
            padding: 30px; 
            border: 3px solid #000; 
            background-color: #f8d7da;
            color: #721c24;
            text-align: center; 
            margin-bottom: 20px;
            border-radius: 10px;
        }
        .live-box {
            padding: 10px;
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            text-align: center;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_time_pk():
    return datetime.now(pytz.timezone('Asia/Karachi'))

def load_data():
    # 1. Load Auto-Market Data
    try:
        with open("prices.json", "r") as f:
            market = json.load(f)
    except:
        market = {"price_ounce_usd": 0, "usd_to_pkr": 0}

    # 2. Load Manual Admin Settings
    try:
        with open("manual.json", "r") as f:
            manual = json.load(f)
    except:
        # Default settings if file doesn't exist
        manual = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}
        
    return market, manual

# --- ADMIN PANEL (SIDEBAR) ---
st.sidebar.header("🔒 Admin Login")
password = st.sidebar.text_input("Enter Password", type="password")

if password == "123123":
    st.sidebar.success("Logged In!")
    st.sidebar.markdown("---")
    
    # Load current settings
    _, current_manual = load_data()
    
    st.sidebar.subheader("💰 Update Price")
    # Allow negative numbers (step=100)
    new_premium = st.sidebar.number_input("Add/Sub Amount (PKR)", value=int(current_manual.get('premium', 0)), step=100)
    
    st.sidebar.subheader("⏳ Validity")
    valid_hours = st.sidebar.slider("Keep price live for (Hours)", 1, 24, 4)
    
    if st.sidebar.button("🔴 UPDATE NOW"):
        with st.spinner("Saving to Database..."):
            try:
                # Connect to GitHub
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                
                # Prepare Data
                save_data = {
                    "premium": new_premium,
                    "last_updated": get_time_pk().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": valid_hours
                }
                json_content = json.dumps(save_data, indent=4)
                
                # Save to 'manual.json'
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Admin Update", json_content, contents.sha)
                except:
                    repo.create_file("manual.json", "Init Admin", json_content)
                    
                st.sidebar.success("✅ Saved! Refreshing...")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# --- MAIN APP LOGIC ---
market, manual = load_data()

# Check Expiration
last_update_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_update_dt = datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S")
last_update_dt = pytz.timezone('Asia/Karachi').localize(last_update_dt)

current_time = get_time_pk()
hours_passed = (current_time - last_update_dt).total_seconds() / 3600
is_expired = hours_passed > manual.get("valid_hours", 4)

# Calculate Price
ounce = market['price_ounce_usd']
usd_pkr = market['usd_to_pkr']
premium = manual['premium']
pak_tola = ((ounce / 31.1035) * 11.66 * usd_pkr) + premium

# --- DISPLAY ---
st.title("ISLAM JEWELLERY")

if is_expired:
    # --- EXPIRED VIEW (Contact Us) ---
    st.markdown(f"""
        <div class="status-box">
            <h2>⚠️ RATES EXPIRED</h2>
            <p>The rates have not been updated recently.</p>
            <h3>📞 Please Contact: 0300-1234567</h3>
            <p style="font-size: 12px">Last Update: {last_update_str}</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # --- LIVE VIEW ---
    st.markdown(f"""
        <div class="live-box">
            ✅ <strong>Rates are LIVE</strong> (Valid for {manual.get('valid_hours')} hours)
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("🌍 Int'l Ounce", f"${ounce:,.2f}")
    col2.metric("💵 USD Rate", f"Rs {usd_pkr:.2f}")
    
    st.markdown("---")
    
    st.markdown("<h2 style='text-align: center;'>🇵🇰 PAKISTAN GOLD RATE</h2>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 60px;'>Rs {pak_tola:,.0f}</h1>", unsafe_allow_html=True)
    st.caption(f"Includes Market Premium: Rs {premium}")
    st.caption(f"Last Admin Update: {last_update_str}")
