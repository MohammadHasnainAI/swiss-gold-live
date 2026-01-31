import streamlit as st
import json
import time
from github import Github
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Islam Jewellery", page_icon="💎", layout="centered")

# --- 2. EUROPEAN CLEAN CSS ---
st.markdown("""
    <style>
        /* Import Clean Sans-Serif Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* MAIN BACKGROUND */
        .stApp {
            background-color: #f8f9fa; /* Very Light Grey */
            font-family: 'Inter', sans-serif;
            color: #212529;
        }

        /* HIDE DEFAULT ELEMENTS */
        #MainMenu, header, footer {visibility: hidden;}

        /* HEADER STYLES */
        .brand-header {
            text-align: center;
            margin-bottom: 40px;
            padding-top: 20px;
        }
        .brand-name {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1a1a1a;
            letter-spacing: -1px;
            text-transform: uppercase;
            margin: 0;
        }
        .brand-sub {
            font-size: 0.9rem;
            color: #6c757d;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 5px;
        }

        /* CARD DESIGN (Clean White Box) */
        .euro-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Soft Shadow */
            border: 1px solid #e9ecef;
            text-align: center;
            margin-bottom: 24px;
        }

        /* LIVE BADGE */
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            background-color: #d1e7dd;
            color: #0f5132;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 20px;
        }
        
        .status-badge-closed {
            display: inline-block;
            padding: 6px 16px;
            background-color: #f8d7da;
            color: #842029;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 20px;
        }

        /* PRICE TYPOGRAPHY */
        .main-price {
            font-size: 4.5rem;
            font-weight: 800;
            color: #212529;
            letter-spacing: -2px;
            line-height: 1;
            margin: 10px 0;
        }
        .price-label {
            font-size: 1rem;
            color: #adb5bd;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .update-time {
            font-size: 0.8rem;
            color: #ced4da;
            margin-top: 20px;
        }

        /* STATS GRID */
        .stats-container {
            display: flex;
            gap: 15px;
        }
        .stat-box {
            flex: 1;
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #495057;
        }
        .stat-title {
            font-size: 0.75rem;
            color: #adb5bd;
            letter-spacing: 1px;
            text-transform: uppercase;
            font-weight: 600;
            margin-top: 5px;
        }

        /* BUTTONS (Clean Blue) */
        .action-btn {
            display: block;
            width: 100%;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            color: #495057;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            margin-top: 10px;
            transition: all 0.2s;
        }
        .action-btn:hover {
            background-color: #f8f9fa;
            border-color: #adb5bd;
            color: #212529;
        }
        
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---
def get_time(): return datetime.now(pytz.timezone('Asia/Karachi'))

def load_data():
    try:
        with open("prices.json", "r") as f: m = json.load(f)
    except: m = {"price_ounce_usd": 0, "usd_to_pkr": 0}
    try:
        with open("manual.json", "r") as f: a = json.load(f)
    except: a = {"premium": 0, "last_updated": "2000-01-01 00:00:00", "valid_hours": 4}
    return m, a

market, manual = load_data()
last_str = manual.get("last_updated", "2000-01-01 00:00:00")
last_dt = pytz.timezone('Asia/Karachi').localize(datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S"))
is_expired = (get_time() - last_dt).total_seconds() / 3600 > manual.get("valid_hours", 4)
pk_price = ((market['price_ounce_usd'] / 31.1035) * 11.66 * market['usd_to_pkr']) + manual['premium']

# --- 4. DISPLAY (HTML) ---

# Header
st.markdown("""
    <div class='brand-header'>
        <h1 class='brand-name'>Islam Jewellery</h1>
        <div class='brand-sub'>Sarafa Bazar • Est. 1990</div>
    </div>
""", unsafe_allow_html=True)

if is_expired:
    # CLOSED CARD
    st.markdown(f"""
        <div class='euro-card'>
            <div class='status-badge-closed'>● Market Closed</div>
            <div class='main-price' style='color: #dee2e6;'>Pending</div>
            <div class='price-label'>Waiting for Daily Update</div>
            <div style='margin-top: 20px;'>
                <a href='tel:03001234567' class='action-btn'>📞 Call for Rates</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

else:
    # LIVE CARD
    st.markdown(f"""
        <div class='euro-card'>
            <div class='status-badge'>● Live Market Rate</div>
            <div class='main-price'>Rs {pk_price:,.0f}</div>
            <div class='price-label'>24K Gold Per Tola</div>
            <div class='update-time'>Last Update: {last_str}</div>
        </div>
    """, unsafe_allow_html=True)

    # STATS ROW
    st.markdown(f"""
        <div class='stats-container'>
            <div class='stat-box'>
                <div class='stat-value'>${market['price_ounce_usd']:,.0f}</div>
                <div class='stat-title'>Int'l Ounce</div>
            </div>
            <div class='stat-box'>
                <div class='stat-value'>Rs {market['usd_to_pkr']:.2f}</div>
                <div class='stat-title'>USD Rate</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # CONTACT BUTTONS
    st.markdown("""
        <div style='display: flex; gap: 10px; margin-top: 20px;'>
            <a href='tel:03001234567' class='action-btn'>📞 Call Now</a>
            <a href='https://wa.me/923001234567' class='action-btn' style='color: #25D366; border-color: #25D366;'>💬 WhatsApp</a>
        </div>
    """, unsafe_allow_html=True)

# --- 5. ADMIN PANEL (SIDEBAR) ---
st.sidebar.title("⚙️ Admin")

# Token Checker (Debug)
if "GIT_TOKEN" in st.secrets:
    st.sidebar.caption("✅ System Connected")
else:
    st.sidebar.error("❌ Token Missing in Secrets!")

with st.sidebar.expander("Update Prices"):
    pwd = st.text_input("Access Key", type="password")
    
    if pwd == "123123":
        st.sidebar.success("Unlocked")
        
        # Initialize Memory
        if 'admin_premium' not in st.session_state:
            st.session_state.admin_premium = int(manual['premium'])

        def change_val(amount):
            st.session_state.admin_premium += amount

        # Buttons
        c1, c2 = st.sidebar.columns(2)
        c1.button("-100", on_click=change_val, args=(-100,))
        c2.button("+100", on_click=change_val, args=(100,))
        
        # Input
        st.sidebar.number_input("Premium Amount", key="admin_premium", step=100)
        
        if st.sidebar.button("Save & Publish"):
            try:
                g = Github(st.secrets["GIT_TOKEN"])
                repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
                data = {
                    "premium": st.session_state.admin_premium,
                    "last_updated": get_time().strftime("%Y-%m-%d %H:%M:%S"),
                    "valid_hours": 4
                }
                
                # Update File
                try:
                    contents = repo.get_contents("manual.json")
                    repo.update_file(contents.path, "Update", json.dumps(data), contents.sha)
                except:
                    repo.create_file("manual.json", "Init", json.dumps(data))
                
                st.sidebar.success("Done! Reloading...")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
