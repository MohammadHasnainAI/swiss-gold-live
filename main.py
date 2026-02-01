import streamlit as st
import requests
import json
from datetime import datetime
import pytz
import pandas as pd
import altair as alt
from github import Github
from streamlit_autorefresh import st_autorefresh

# 1. PAGE CONFIG
st.set_page_config(page_title="Islam Jewellery V13", page_icon="💎", layout="centered")

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

# 3. DESIGN & CSS (ULTRA COMPACT + LIGHT GRAY THEME + ADMIN DASHBOARD STYLES)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

/* Main Background - Light Gray */
.stApp {background-color:#f8f9fa; font-family:'Outfit', sans-serif; color:#333;}
#MainMenu, footer, header {visibility:hidden;}

/* --- SPACE REMOVER --- */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
    margin-top: -40px !important;
    max-width: 700px;
}

/* Header - Tight & Clean */
.header-box {text-align:center; padding-bottom:5px; margin-bottom:10px; margin-top: 15px;}
.brand-title {font-size:1.8rem; font-weight:800; color:#111; letter-spacing:-0.5px; text-transform:uppercase; line-height: 1; margin-bottom: 2px;}
.brand-subtitle {font-size:0.65rem; color:#d4af37; font-weight:700; letter-spacing:1.5px; text-transform:uppercase;}

/* Cards - White on Gray Background */
.price-card {
    background:#ffffff; 
    border-radius:16px; 
    padding:15px; 
    text-align:center; 
    box-shadow:0 4px 6px rgba(0,0,0,0.04); 
    border:1px solid #eef0f2; 
    margin-bottom:8px;
}

.live-badge {background-color:#e6f4ea; color:#1e8e3e; padding:3px 10px; border-radius:30px; font-weight:700; font-size:0.6rem; letter-spacing:0.5px; display:inline-block; margin-bottom:4px;}
.big-price {font-size:2.6rem; font-weight:800; color:#222; line-height:1; margin:4px 0; letter-spacing:-1px;}
.price-label {font-size:0.85rem; color:#666; font-weight:500;}

/* Stats Container - Gray Boxes */
.stats-container {display:flex; gap:6px; margin-top:10px; justify-content:center;}
.stat-box {
    background:#f1f3f5;
    border-radius:8px; 
    padding:8px; 
    text-align:center; 
    border:1px solid #ebebeb; 
    flex: 1; 
}
.stat-value {font-size:0.9rem; font-weight:700; color:#d4af37;}
.stat-label {font-size:0.55rem; color:#888; font-weight:600; text-transform:uppercase;}

/* Buttons */
.btn-grid {display: flex; gap: 8px; margin-top: 12px; justify-content: center;}
.contact-btn {
    flex: 1; 
    padding: 12px; 
    border-radius: 10px; 
    text-align: center; 
    text-decoration: none; 
    font-weight: 600; 
    font-size: 0.85rem; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    color: white !important;
}
.btn-call {background-color:#222;}
.btn-whatsapp {background-color:#25D366;}
.contact-btn:hover {opacity:0.9;}

/* Footer */
.footer {
    background:#f1f3f5;
    padding:10px; 
    border-radius: 10px;
    text-align:center; 
    font-size:0.7rem; 
    color:#666; 
    margin-top:15px; 
}

/* Admin Dashboard Premium Styles */
.login-card {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    max-width: 450px;
    margin: 2rem auto;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.2);
    animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}

.admin-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

.admin-subtitle {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border-left: 4px solid #667eea;
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #333;
    margin: 0.5rem 0;
}

.metric-label {
    color: #666;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

.success-msg {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 12px;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
    animation: slideInRight 0.5s ease-out;
}

.error-msg {
    background: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 12px;
    border-left: 4px solid #dc3545;
    margin: 1rem 0;
    animation: shake 0.5s ease-out;
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-10px); }
    75% { transform: translateX(10px); }
}
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

# 5. SETTINGS ENGINE
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

# 6. DATA ENGINE
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
    <div style="font-size:0.6rem; color:#aaa; margin-top:8px; padding-top:5px; border-top:1px solid #eee;">
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
    <div class="live-badge" style="background-color:#eef2f6; color:#555;">● SILVER LIVE</div>
    <div class="big-price">Rs {silver_tola:,.0f}</div>
    <div class="price-label">24K Silver Per Tola</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-value">${live_data['silver']:,.2f}</div><div class="stat-label">Ounce</div></div>
        <div class="stat-box"><div class="stat-value">{live_data['time']}</div><div class="stat-label">Updated</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="btn-grid"><a href="tel:03492114166" class="contact-btn btn-call">📞 Call Now</a><a href="https://wa.me/923492114166" class="contact-btn btn-whatsapp">💬 WhatsApp</a></div>""", unsafe_allow_html=True)

# 10. PROFESSIONAL ADMIN DASHBOARD
# Initialize auth state
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# Login Screen
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
            <div class="admin-title">Admin Portal</div>
            <div class="admin-subtitle">Secure Access Required</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter admin password...", label_visibility="collapsed")
            if st.button("🔓 Access Dashboard", use_container_width=True, type="primary"):
                if password == "123123":
                    st.session_state.admin_auth = True
                    st.balloons()
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="error-msg">
                        ⚠️ Invalid password. Please try again.
                    </div>
                    """, unsafe_allow_html=True)

# Dashboard Screen
if st.session_state.admin_auth:
    st.markdown("---")
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style="margin-bottom: 2rem;">
            <div style="font-size: 2rem; font-weight: 800; color: #333;">⚙️ Admin Dashboard</div>
            <div style="color: #666; font-size: 0.9rem;">Manage gold rates and view analytics</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("🔴 Logout", key="logout_btn"):
            st.session_state.admin_auth = False
            st.rerun()
    
    # Professional Tabs
    tabs = st.tabs(["💰 Update Rates", "📊 Statistics", "📜 History", "📈 Charts"])
    
    # TAB 1: Update Rates
    with tabs[0]:
        st.markdown("### Adjust Premium Rates")
        
        # Metal Selection with visual cards
        metal_cols = st.columns(2)
        with metal_cols[0]:
            gold_selected = st.button("🟡 Gold", use_container_width=True, 
                                    type="primary" if st.session_state.get('selected_metal', 'Gold') == 'Gold' else "secondary")
            if gold_selected:
                st.session_state.selected_metal = 'Gold'
                
        with metal_cols[1]:
            silver_selected = st.button("⚪ Silver", use_container_width=True,
                                      type="primary" if st.session_state.get('selected_metal', 'Gold') == 'Silver' else "secondary")
            if silver_selected:
                st.session_state.selected_metal = 'Silver'
        
        metal = st.session_state.get('selected_metal', 'Gold')
        
        # Premium Control Section
        st.markdown(f"#### {metal} Premium Control")
        
        control_cols = st.columns([1, 2, 1])
        
        # Current values display
        current_val = st.session_state.new_gold if metal == "Gold" else st.session_state.new_silver
        step_val = 500 if metal == "Gold" else 50
        
        with control_cols[0]:
            if st.button(f"➖ {step_val}", use_container_width=True, key=f"dec_{metal}"):
                if metal == "Gold":
                    st.session_state.new_gold = max(0, st.session_state.new_gold - step_val)
                else:
                    st.session_state.new_silver = max(0, st.session_state.new_silver - step_val)
                st.rerun()
        
        with control_cols[1]:
            new_val = st.number_input("", 
                                    value=int(current_val), 
                                    step=int(step_val),
                                    key=f"input_{metal}",
                                    label_visibility="collapsed")
            if metal == "Gold":
                st.session_state.new_gold = new_val
            else:
                st.session_state.new_silver = new_val
        
        with control_cols[2]:
            if st.button(f"➕ {step_val}", use_container_width=True, key=f"inc_{metal}"):
                if metal == "Gold":
                    st.session_state.new_gold += step_val
                else:
                    st.session_state.new_silver += step_val
                st.rerun()
        
        # Live Preview
        preview_cols = st.columns(3)
        with preview_cols[0]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current Premium</div>
                <div class="metric-value">Rs {current_val:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with preview_cols[1]:
            calculated = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + (st.session_state.new_gold if metal == "Gold" else 0)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #f5576c;">
                <div class="metric-label">Final {metal} Rate</div>
                <div class="metric-value">Rs {calculated:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with preview_cols[2]:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #2ed573;">
                <div class="metric-label">USD Rate</div>
                <div class="metric-value">Rs {live_data['usd']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Publish Button with loading state
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Publish to Live Server", type="primary", use_container_width=True):
            with st.spinner("Updating global rates..."):
                if repo:
                    try:
                        # Update manual.json
                        new_settings = {
                            "gold_premium": int(st.session_state.new_gold), 
                            "silver_premium": int(st.session_state.new_silver)
                        }
                        
                        try:
                            contents = repo.get_contents("manual.json")
                            repo.update_file(contents.path, f"Update rates - {datetime.now()}", 
                                           json.dumps(new_settings), contents.sha)
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
                            "gold_pk": float(gold_tola),
                            "silver_pk": float(silver_tola),
                            "usd": float(live_data['usd'])
                        })
                        if len(history) > 60: 
                            history = history[-60:]
                        
                        try:
                            repo.update_file(h_content.path, f"History update - {datetime.now()}", 
                                           json.dumps(history), h_content.sha)
                        except:
                            repo.create_file("history.json", "Init", json.dumps(history))
                        
                        st.markdown("""
                        <div class="success-msg">
                            ✅ Successfully published! Changes will reflect globally within 5 seconds.
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        manual_refresh()
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="error-msg">
                            ❌ Error: {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-msg">
                        ❌ GitHub repository connection failed. Check your secrets.
                    </div>
                    """, unsafe_allow_html=True)
    
    # TAB 2: Statistics
    with tabs[1]:
        st.markdown("### Real-time Market Statistics")
        
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🟡</div>
                <div style="font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Gold Premium</div>
                <div style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">Rs {int(st.session_state.new_gold):,}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Added to base rate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[1]:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚪</div>
                <div style="font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Silver Premium</div>
                <div style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">Rs {int(st.session_state.new_silver):,}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Added to base rate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[2]:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💵</div>
                <div style="font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">USD/PKR</div>
                <div style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">Rs {live_data['usd']:.2f}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Live exchange rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional Metrics
        st.markdown("<br>", unsafe_allow_html=True)
        detail_cols = st.columns(2)
        
        with detail_cols[0]:
            st.markdown("#### Gold Breakdown")
            st.markdown(f"""
            - **International Price:** ${live_data['gold']:,.2f}/oz
            - **Per Tola (11.66g):** Rs {gold_tola:,.0f}
            - **Dubai Rate:** AED {gold_dubai_tola:,.0f}
            - **Last Updated:** {live_data['time']}
            """)
            
        with detail_cols[1]:
            st.markdown("#### Silver Breakdown")
            st.markdown(f"""
            - **International Price:** ${live_data['silver']:,.2f}/oz
            - **Per Tola (11.66g):** Rs {silver_tola:,.0f}
            - **Premium Applied:** Rs {int(st.session_state.new_silver)}
            - **Status:** 🟢 Live
            """)
    
    # TAB 3: History
    with tabs[2]:
        st.markdown("### Rate History (Last 60 Updates)")
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
                    df = df.rename(columns={
                        'date': 'Date/Time',
                        'gold_pk': 'Gold Rate (PKR)',
                        'usd': 'USD Rate'
                    })
                    
                    # Styled table
                    st.dataframe(
                        df.sort_values('Date/Time', ascending=False),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Date/Time": st.column_config.DatetimeColumn("Date/Time", width="medium"),
                            "Gold Rate (PKR)": st.column_config.NumberColumn("Gold Rate (PKR)", format="Rs %,.0f"),
                            "USD Rate": st.column_config.NumberColumn("USD Rate", format="Rs %.2f")
                        }
                    )
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"gold_history_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No history records found.")
            else:
                st.error("Repository connection failed.")
        except Exception as e:
            st.info("📭 No history found. Click 'Publish Rate' to create your first record.")
    
    # TAB 4: Charts
    with tabs[3]:
        st.markdown("### Gold Price Trends")
        
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if len(history_data) > 1:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Professional Chart with Altair
                    chart = alt.Chart(df).mark_line(
                        point=True,
                        color='#667eea',
                        strokeWidth=3
                    ).encode(
                        x=alt.X('date:T', title='Date & Time', axis=alt.Axis(format='%d %b %H:%M')),
                        y=alt.Y('gold_pk:Q', title='Gold Rate (PKR)', scale=alt.Scale(zero=False)),
                        tooltip=[
                            alt.Tooltip('date:T', title='Date', format='%Y-%m-%d %H:%M'),
                            alt.Tooltip('gold_pk:Q', title='Rate', format='Rs ,.0f'),
                            alt.Tooltip('usd:Q', title='USD', format='Rs ,.2f')
                        ]
                    ).properties(
                        height=400
                    ).configure_axis(
                        grid=True,
                        gridColor='#f0f0f0',
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_view(
                        strokeWidth=0,
                        fill='white'
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Highest Rate", f"Rs {df['gold_pk'].max():,.0f}")
                    with col2:
                        st.metric("Lowest Rate", f"Rs {df['gold_pk'].min():,.0f}")
                    with col3:
                        st.metric("Average", f"Rs {df['gold_pk'].mean():,.0f}")
                else:
                    st.info("📊 At least 2 data points required to generate chart. Please publish rates multiple times.")
        except Exception as e:
            st.info("Chart will appear after first data update.")

# 11. FOOTER
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
