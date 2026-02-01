import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# MUST BE FIRST - Page Config
st.set_page_config(page_title="Islam Jewellery V13", page_icon="💎", layout="centered")

# Initialize session states FIRST (before any other code)
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "new_gold" not in st.session_state:
    st.session_state.new_gold = 0
if "new_silver" not in st.session_state:
    st.session_state.new_silver = 0
if "gold_market_status" not in st.session_state:
    st.session_state.gold_market_status = "OPEN"
if "silver_market_status" not in st.session_state:
    st.session_state.silver_market_status = "OPEN"

# Auto-refresh only when not in admin
if not st.session_state.admin_auth:
    st_autorefresh(interval=5000, key="gold_refresh")

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif;}
.block-container {padding-top: 0rem !important; margin-top: -40px !important; max-width: 700px;}
.brand-title {font-size:1.8rem; font-weight:800; color:#111; text-transform:uppercase;}
.brand-subtitle {font-size:0.65rem; color:#d4af37; font-weight:700; letter-spacing:1.5px;}
.price-card {background:#ffffff; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 6px rgba(0,0,0,0.04); border:1px solid #eef0f2; margin-bottom:8px;}
.live-badge {padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; margin:4px 0;}
.price-label {font-size:0.85rem; color:#666;}
.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {background:#f1f3f5; border-radius:8px; padding:8px; text-align:center; flex:1;}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.btn-grid {display:flex; gap:8px; margin-top:12px;}
.contact-btn {flex:1; padding:12px; border-radius:10px; text-align:center; text-decoration:none; font-weight:600; color:white !important;}
.btn-call {background:#222;}
.btn-whatsapp {background:#25D366;}
.footer {background:#f1f3f5; padding:10px; border-radius:10px; text-align:center; font-size:0.7rem; margin-top:15px;}

/* Admin */
.login-card {background:white; border-radius:16px; padding:2rem; box-shadow:0 4px 20px rgba(0,0,0,0.1); max-width:400px; margin:2rem auto; border-top:4px solid #d4af37; text-align:center;}
.admin-title {font-size:1.8rem; font-weight:800; color:#d4af37; text-transform:uppercase;}
.metric-card {background:white; border-radius:12px; padding:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.08); border-bottom:3px solid #d4af37; text-align:center;}
.control-box {background:#fafafa; border-radius:16px; padding:2rem; border:1px solid #e0e0e0; margin-top:1rem;}
.success-msg {background:#d4edda; color:#155724; padding:1rem; border-radius:8px; border-left:4px solid #28a745; margin:1rem 0;}
.error-msg {background:#f8d7da; color:#721c24; padding:1rem; border-radius:8px; border-left:4px solid #dc3545; margin:1rem 0;}
</style>
""", unsafe_allow_html=True)

# GitHub Connection
repo = None
try:
    if "GIT_TOKEN" in st.secrets:
        g = Github(st.secrets["GIT_TOKEN"])
        repo = g.get_repo("MohammadHasnainAI/swiss-gold-live")
except:
    pass

# Load Settings
def load_settings():
    defaults = {"gold_premium": 0, "silver_premium": 0, "gold_market": "OPEN", "silver_market": "OPEN"}
    if repo:
        try:
            content = repo.get_contents("manual.json")
            data = json.loads(content.decoded_content.decode())
            # Merge with defaults to ensure all keys exist
            return {**defaults, **data}
        except:
            return defaults
    return defaults

settings = load_settings()

# Update session state from settings
if st.session_state.new_gold == 0:
    st.session_state.new_gold = settings.get("gold_premium", 0)
if st.session_state.new_silver == 0:
    st.session_state.new_silver = settings.get("silver_premium", 0)
if "gold_market" in settings:
    st.session_state.gold_market_status = settings["gold_market"]
if "silver_market" in settings:
    st.session_state.silver_market_status = settings["silver_market"]

# Get Live Rates
def get_rates():
    try:
        if "TWELVE_DATA_KEY" not in st.secrets:
            return {"gold": 2750, "silver": 32, "usd": 278, "aed": 3.67, "time": "Demo", "full_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        td_key = st.secrets["TWELVE_DATA_KEY"]
        curr_key = st.secrets["CURR_KEY"]
        
        metals = requests.get(f"https://api.twelvedata.com/price?symbol=XAU/USD,XAG/USD&apikey={td_key}", timeout=5).json()
        curr = requests.get(f"https://v6.exchangerate-api.com/v6/{curr_key}/latest/USD", timeout=5).json()
        
        return {
            "gold": float(metals.get("XAU/USD", {}).get("price", 2750)),
            "silver": float(metals.get("XAG/USD", {}).get("price", 32)),
            "usd": curr.get("conversion_rates", {}).get("PKR", 278),
            "aed": curr.get("conversion_rates", {}).get("AED", 3.67),
            "time": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%I:%M %p"),
            "full_date": datetime.now(pytz.timezone("Asia/Karachi")).strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {"gold": 2750, "silver": 32, "usd": 278, "aed": 3.67, "time": "Error", "full_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

live = get_rates()

# Calculations
gold_tola = ((live["gold"] / 31.1035) * 11.66 * live["usd"]) + st.session_state.new_gold
silver_tola = ((live["silver"] / 31.1035) * 11.66 * live["usd"]) + st.session_state.new_silver
gold_dubai = (live["gold"] / 31.1035) * 11.66 * live["aed"]

# HEADER
st.markdown(f"""
<div style="text-align:center; padding-bottom:5px; margin-bottom:10px; margin-top:15px;">
<div class="brand-title">Islam Jewellery</div>
<div class="brand-subtitle">Sarafa Bazar • Premium Gold</div>
</div>
""", unsafe_allow_html=True)

# GOLD CARD
if st.session_state.gold_market_status == "OPEN":
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge" style="background-color:#e6f4ea; color:#1e8e3e;">● GOLD LIVE</div>
        <div class="big-price">Rs {gold_tola:,.0f}</div>
        <div class="price-label">24K Gold Per Tola</div>
        <div class="stats-container">
            <div class="stat-box"><div class="stat-value">${live["gold"]:,.0f}</div><div style="font-size:0.55rem; color:#888;">Ounce</div></div>
            <div class="stat-box"><div class="stat-value">Rs {live["usd"]:.2f}</div><div style="font-size:0.55rem; color:#888;">Dollar</div></div>
            <div class="stat-box"><div class="stat-value">AED {gold_dubai:,.0f}</div><div style="font-size:0.55rem; color:#888;">Dubai</div></div>
        </div>
        <div style="font-size:0.6rem; color:#aaa; margin-top:8px; padding-top:5px; border-top:1px solid #eee;">
            Last Updated: <b>{live["time"]}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card" style="border:2px solid #dc2626;">
        <div class="live-badge" style="background-color:#fee2e2; color:#dc2626;">● GOLD CLOSED</div>
        <div class="big-price" style="color:#dc2626; font-size:2rem;">⏸️ MARKET CLOSED</div>
        <div class="price-label" style="color:#dc2626;">Currently Unavailable</div>
        <div style="font-size:0.8rem; color:#666; margin-top:10px;">
            Please check back later or contact us
        </div>
    </div>
    """, unsafe_allow_html=True)

# REFRESH
if st.button("🔄 Check for New Gold Rate", use_container_width=True):
    st.experimental_rerun()

# SILVER CARD
if st.session_state.silver_market_status == "OPEN":
    st.markdown(f"""
    <div class="price-card">
        <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
        <div class="big-price">Rs {silver_tola:,.0f}</div>
        <div class="price-label">24K Silver Per Tola</div>
        <div class="stats-container">
            <div class="stat-box"><div class="stat-value">${live["silver"]:,.2f}</div><div style="font-size:0.55rem; color:#888;">Ounce</div></div>
            <div class="stat-box"><div class="stat-value">{live["time"]}</div><div style="font-size:0.55rem; color:#888;">Updated</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="price-card" style="border:2px solid #dc2626;">
        <div class="live-badge" style="background-color:#fee2e2; color:#dc2626;">● SILVER CLOSED</div>
        <div class="big-price" style="color:#dc2626; font-size:2rem;">⏸️ MARKET CLOSED</div>
        <div class="price-label" style="color:#dc2626;">Currently Unavailable</div>
        <div style="font-size:0.8rem; color:#666; margin-top:10px;">
            Please check back later or contact us
        </div>
    </div>
    """, unsafe_allow_html=True)

# CONTACT
st.markdown("""
<div class="btn-grid">
<a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a>
<a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a>
</div>
""", unsafe_allow_html=True)

# ADMIN SECTION
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""<div class="login-card"><div style="font-size:2.5rem;">🔐</div><div class="admin-title">Admin Portal</div><p style="color:#666;">Authorized Only</p></div>""", unsafe_allow_html=True)
        pwd = st.text_input("Password", type="password")
        if st.button("🔓 Login", use_container_width=True):
            if pwd == "123123":
                st.session_state.admin_auth = True
                st.experimental_rerun()
            else:
                st.error("Wrong password")

if st.session_state.admin_auth:
    st.markdown("---")
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown('<div class="admin-title" style="font-size:1.5rem;">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
    with c2:
        if st.button("🔴 Logout"):
            st.session_state.admin_auth = False
            st.experimental_rerun()
    
    tabs = st.tabs(["💰 Update", "📜 History", "📈 Charts"])
    
    # TAB 1: UPDATE RATES & MARKET CONTROL
    with tabs[0]:
        st.markdown("### 🌐 Market Control (ON/OFF)")
        
        # Gold Market Control
        gcol1, gcol2 = st.columns([2,1])
        with gcol1:
            st.markdown(f"**🟡 Gold Market Status:** `{st.session_state.gold_market_status}`")
        with gcol2:
            if st.session_state.gold_market_status == "OPEN":
                if st.button("Turn OFF", key="g_off"):
                    st.session_state.gold_market_status = "CLOSED"
                    st.experimental_rerun()
            else:
                if st.button("Turn ON", key="g_on"):
                    st.session_state.gold_market_status = "OPEN"
                    st.experimental_rerun()
        
        # Silver Market Control
        scol1, scol2 = st.columns([2,1])
        with scol1:
            st.markdown(f"**⚪ Silver Market Status:** `{st.session_state.silver_market_status}`")
        with scol2:
            if st.session_state.silver_market_status == "OPEN":
                if st.button("Turn OFF", key="s_off"):
                    st.session_state.silver_market_status = "CLOSED"
                    st.experimental_rerun()
            else:
                if st.button("Turn ON", key="s_on"):
                    st.session_state.silver_market_status = "OPEN"
                    st.experimental_rerun()
        
        st.divider()
        st.markdown("### 💰 Update Premium Rates")
        
        metal = st.radio("Select:", ["Gold", "Silver"], horizontal=True)
        
        if metal == "Gold":
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("**Gold Premium**")
            c1, c2 = st.columns([1,1])
            with c1:
                if st.button("➖ 500", use_container_width=True):
                    st.session_state.new_gold = max(0, st.session_state.new_gold - 500)
                    st.experimental_rerun()
            with c2:
                if st.button("➕ 500", use_container_width=True):
                    st.session_state.new_gold += 500
                    st.experimental_rerun()
            
            val = st.number_input("Amount", value=st.session_state.new_gold, step=500, key="g_val")
            st.session_state.new_gold = int(val)
            
            calc = ((live["gold"] / 31.1035) * 11.66 * live["usd"]) + st.session_state.new_gold
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem;">
                <div class="metric-card" style="border-bottom-color:#d4af37;">
                    <div style="font-size:0.75rem; color:#666;">Premium</div>
                    <div style="font-size:1.5rem; font-weight:800; color:#d4af37;">Rs {st.session_state.new_gold:,}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size:0.75rem; color:#666;">Final Rate</div>
                    <div style="font-size:1.5rem; font-weight:800;">Rs {calc:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("**Silver Premium**")
            c1, c2 = st.columns([1,1])
            with c1:
                if st.button("➖ 50", use_container_width=True):
                    st.session_state.new_silver = max(0, st.session_state.new_silver - 50)
                    st.experimental_rerun()
            with c2:
                if st.button("➕ 50", use_container_width=True):
                    st.session_state.new_silver += 50
                    st.experimental_rerun()
            
            val = st.number_input("Amount", value=st.session_state.new_silver, step=50, key="s_val")
            st.session_state.new_silver = int(val)
            
            calc = ((live["silver"] / 31.1035) * 11.66 * live["usd"]) + st.session_state.new_silver
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:1rem;">
                <div class="metric-card" style="border-bottom-color:#C0C0C0;">
                    <div style="font-size:0.75rem; color:#666;">Premium</div>
                    <div style="font-size:1.5rem; font-weight:800; color:#666;">Rs {st.session_state.new_silver:,}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size:0.75rem; color:#666;">Final Rate</div>
                    <div style="font-size:1.5rem; font-weight:800;">Rs {calc:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚀 SAVE & PUBLISH ALL", type="primary", use_container_width=True):
            if repo:
                try:
                    # Save settings including market status
                    new_settings = {
                        "gold_premium": st.session_state.new_gold,
                        "silver_premium": st.session_state.new_silver,
                        "gold_market": st.session_state.gold_market_status,
                        "silver_market": st.session_state.silver_market_status
                    }
                    
                    # Update or create manual.json
                    try:
                        cont = repo.get_contents("manual.json")
                        repo.update_file(cont.path, f"Update {datetime.now().strftime('%H:%M')}", json.dumps(new_settings), cont.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
                    # Update history
                    try:
                        hist = repo.get_contents("history.json")
                        history = json.loads(hist.decoded_content.decode())
                    except:
                        history = []
                    
                    history.append({
                        "date": live["full_date"],
                        "gold_pk": float(gold_tola),
                        "silver_pk": float(silver_tola),
                        "gold_ounce": float(live["gold"]),
                        "silver_ounce": float(live["silver"]),
                        "usd": float(live["usd"])
                    })
                    
                    if len(history) > 60:
                        history = history[-60:]
                    
                    try:
                        repo.update_file(hist.path, f"History {datetime.now().strftime('%H:%M')}", json.dumps(history), hist.sha)
                    except:
                        repo.create_file("history.json", "Init", json.dumps(history))
                    
                    st.success("✅ Saved! Refreshing...")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("GitHub not connected")
    
    # TAB 2: HISTORY (WITH OUNCE)
    with tabs[1]:
        st.markdown("### 📜 Rate History")
        
        if st.button("🗑️ Reset History", type="secondary"):
            if repo:
                try:
                    h = repo.get_contents("history.json")
                    repo.update_file(h.path, "Reset", json.dumps([]), h.sha)
                    st.success("Cleared!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        try:
            if repo:
                h = repo.get_contents("history.json")
                data = json.loads(h.decoded_content.decode())
                
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    # Format with ounce columns
                    display = pd.DataFrame({
                        'Date': df['date'],
                        'Gold Oz ($)': df.get('gold_ounce', 0).apply(lambda x: f"${x:,.2f}"),
                        'Gold PKR': df.get('gold_pk', 0).apply(lambda x: f"Rs {x:,.0f}"),
                        'Silver Oz ($)': df.get('silver_ounce', 0).apply(lambda x: f"${x:,.2f}"),
                        'Silver PKR': df.get('silver_pk', 0).apply(lambda x: f"Rs {x:,.0f}"),
                        'USD': df.get('usd', 0).apply(lambda x: f"Rs {x:.2f}")
                    })
                    
                    st.dataframe(display.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
                    
                    csv = df.to_csv(index=False).encode()
                    st.download_button("📥 Download CSV", csv, f"history_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                else:
                    st.info("No history")
        except Exception as e:
            st.info(f"No data: {e}")
    
    # TAB 3: CHARTS
    with tabs[2]:
        st.markdown("### 📈 Charts")
        
        metal_sel = st.selectbox("Metal:", ["Gold", "Silver"])
        chart_type = st.selectbox("Type:", ["Line", "Area"])
        
        if st.button("🗑️ Reset Chart Data"):
            if repo:
                try:
                    h = repo.get_contents("history.json")
                    repo.update_file(h.path, "Reset", json.dumps([]), h.sha)
                    st.success("Cleared!")
                    st.experimental_rerun()
                except:
                    st.error("Error")
        
        try:
            if repo:
                h = repo.get_contents("history.json")
                data = json.loads(h.decoded_content.decode())
                
                if len(data) > 1:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    if metal_sel == "Gold":
                        y_col = 'gold_pk'
                        color = '#d4af37'
                    else:
                        y_col = 'silver_pk'
                        color = '#71797E'
                    
                    base = alt.Chart(df).encode(
                        x='date:T',
                        y=alt.Y(f'{y_col}:Q', scale=alt.Scale(zero=False)),
                        tooltip=['date', f'{y_col}:Q']
                    )
                    
                    if chart_type == "Area":
                        ch = (base.mark_area(color=color, opacity=0.3) + base.mark_line(color=color, strokeWidth=3))
                    else:
                        ch = base.mark_line(color=color, strokeWidth=3, point=True)
                    
                    st.altair_chart(ch.properties(height=400), use_container_width=True)
                else:
                    st.info("Need 2+ records")
        except Exception as e:
            st.error(f"Chart error: {e}")

# FOOTER
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> • Approximate gold prices<br>
⚠️ Verify with shop before buying
</div>
""", unsafe_allow_html=True)
