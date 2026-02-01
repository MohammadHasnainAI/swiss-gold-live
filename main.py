# 10. PROFESSIONAL ADMIN DASHBOARD (FIXED COLORS & TOGGLE)
# Initialize auth state
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False
if "selected_metal" not in st.session_state:
    st.session_state.selected_metal = "Gold"
if "new_gold" not in st.session_state:
    st.session_state.new_gold = settings.get("gold_premium", 0)
if "new_silver" not in st.session_state:
    st.session_state.new_silver = settings.get("silver_premium", 0)

# Professional Gold Theme CSS
st.markdown("""
<style>
/* Admin Gold Theme */
.admin-box {
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    border: 2px solid #d4af37;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.login-card {
    background: white;
    border-radius: 16px;
    padding: 3rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    max-width: 400px;
    margin: 2rem auto;
    text-align: center;
    border-top: 4px solid #d4af37;
}

.admin-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #d4af37;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.metric-card-pro {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-bottom: 3px solid #d4af37;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card-pro:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.12);
}

.metric-value-pro {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1a1a1a;
    margin: 0.5rem 0;
}

.metric-label-pro {
    color: #666;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* Metal Selection Buttons */
.metal-btn-gold {
    background: #d4af37 !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
}

.metal-btn-silver {
    background: #C0C0C0 !important;
    color: #1a1a1a !important;
    border: none !important;
    font-weight: 700 !important;
}

.metal-btn-inactive {
    background: #f0f0f0 !important;
    color: #666 !important;
    border: 1px solid #ddd !important;
}

/* Control Section */
.control-box {
    background: #fafafa;
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid #e0e0e0;
    margin-top: 1rem;
}

.premium-display {
    background: #1a1a1a;
    color: #d4af37;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    margin: 1rem 0;
}

.success-msg {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}

.error-msg {
    background: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #dc3545;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Login Screen
if not st.session_state.admin_auth:
    with st.expander("🔒 Admin Login"):
        st.markdown("""
        <div class="login-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔐</div>
            <div class="admin-title">Admin Portal</div>
            <p style="color: #666; margin-bottom: 2rem;">Authorized Personnel Only</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password...")
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if password == "123123":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">⚠️ Invalid password</div>', unsafe_allow_html=True)

# Dashboard Screen
if st.session_state.admin_auth:
    st.markdown("---")
    
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<div class="admin-title" style="margin-bottom: 0;">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #666; margin-top: 0;">Manage premium rates & analytics</p>', unsafe_allow_html=True)
    with col2:
        if st.button("🔴 Logout", type="secondary"):
            st.session_state.admin_auth = False
            st.rerun()
    
    tabs = st.tabs(["💰 Update Rates", "📊 Statistics", "📜 History", "📈 Charts"])
    
    # TAB 1: Update Rates (FIXED TOGGLE)
    with tabs[0]:
        st.markdown("### Select Metal")
        
        # Metal Selection Buttons (FIXED LOGIC)
        btn_cols = st.columns(2)
        
        with btn_cols[0]:
            is_gold_active = st.session_state.selected_metal == "Gold"
            if st.button("🟡 GOLD", use_container_width=True, 
                        type="primary" if is_gold_active else "secondary",
                        key="btn_gold_select"):
                st.session_state.selected_metal = "Gold"
                st.rerun()
        
        with btn_cols[1]:
            is_silver_active = st.session_state.selected_metal == "Silver"
            if st.button("⚪ SILVER", use_container_width=True,
                        type="primary" if is_silver_active else "secondary", 
                        key="btn_silver_select"):
                st.session_state.selected_metal = "Silver"
                st.rerun()
        
        # DYNAMIC CONTENT BASED ON SELECTION (THIS WAS MISSING)
        current_metal = st.session_state.selected_metal
        
        if current_metal == "Gold":
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### 🟡 Gold Premium Control")
            
            step = 500
            current_premium = int(st.session_state.new_gold)
            
            # Quick Adjust Buttons
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 500", use_container_width=True):
                    st.session_state.new_gold = max(0, current_premium - 500)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 500", use_container_width=True):
                    st.session_state.new_gold = current_premium + 500
                    st.rerun()
            
            # Manual Input
            new_val = st.number_input("Gold Premium Amount", 
                                    value=current_premium, 
                                    step=step, 
                                    key="gold_premium_input")
            st.session_state.new_gold = new_val
            
            # Calculations Preview
            calculated_gold = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro">
                    <div class="metric-label-pro">Premium</div>
                    <div class="metric-value-pro" style="color: #d4af37;">Rs {int(st.session_state.new_gold):,}</div>
                </div>
                <div class="metric-card-pro" style="border-bottom-color: #1a1a1a;">
                    <div class="metric-label-pro">Final Gold Rate</div>
                    <div class="metric-value-pro">Rs {calculated_gold:,.0f}</div>
                </div>
                <div class="metric-card-pro" style="border-bottom-color: #666;">
                    <div class="metric-label-pro">USD Rate</div>
                    <div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:  # Silver Selected
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### ⚪ Silver Premium Control")
            
            step = 50
            current_premium = int(st.session_state.new_silver)
            
            # Quick Adjust Buttons
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 50", use_container_width=True, key="sil_sub"):
                    st.session_state.new_silver = max(0, current_premium - 50)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 50", use_container_width=True, key="sil_add"):
                    st.session_state.new_silver = current_premium + 50
                    st.rerun()
            
            # Manual Input
            new_val = st.number_input("Silver Premium Amount", 
                                    value=current_premium, 
                                    step=step,
                                    key="silver_premium_input")
            st.session_state.new_silver = new_val
            
            # Calculations Preview for Silver
            calculated_silver = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_silver
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro">
                    <div class="metric-label-pro">Premium</div>
                    <div class="metric-value-pro" style="color: #C0C0C0;">Rs {int(st.session_state.new_silver):,}</div>
                </div>
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;">
                    <div class="metric-label-pro">Final Silver Rate</div>
                    <div class="metric-value-pro">Rs {calculated_silver:,.0f}</div>
                </div>
                <div class="metric-card-pro" style="border-bottom-color: #666;">
                    <div class="metric-label-pro">USD Rate</div>
                    <div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Publish Button (Works for both)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 PUBLISH RATE", type="primary", use_container_width=True):
            if repo:
                try:
                    new_settings = {
                        "gold_premium": int(st.session_state.new_gold), 
                        "silver_premium": int(st.session_state.new_silver)
                    }
                    
                    # Update manual.json
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, f"Update - {datetime.now().strftime('%H:%M')}", 
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
                        repo.update_file(h_content.path, f"Hist - {datetime.now().strftime('%H:%M')}", 
                                       json.dumps(history), h_content.sha)
                    except:
                        repo.create_file("history.json", "Init", json.dumps(history))
                    
                    st.markdown('<div class="success-msg">✅ Published successfully! Live in 5 seconds.</div>', unsafe_allow_html=True)
                    manual_refresh()
                    
                except Exception as e:
                    st.markdown(f'<div class="error-msg">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ GitHub not connected</div>', unsafe_allow_html=True)
    
    # TAB 2: Statistics (PROFESSIONAL COMPANY COLORS - GOLD/BLACK)
    with tabs[1]:
        st.markdown("### Market Overview")
        
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.markdown(f"""
            <div style="background: #1a1a1a; color: #d4af37; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #d4af37;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🟡</div>
                <div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">Gold Premium</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {int(st.session_state.new_gold):,}</div>
                <div style="font-size: 0.7rem; opacity: 0.6;">Added to spot</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[1]:
            st.markdown(f"""
            <div style="background: white; color: #1a1a1a; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #C0C0C0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚪</div>
                <div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px;">Silver Premium</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0; color: #666;">Rs {int(st.session_state.new_silver):,}</div>
                <div style="font-size: 0.7rem; color: #999;">Added to spot</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #d4af37 0%, #f4e5c2 100%); color: #1a1a1a; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💵</div>
                <div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">USD/PKR</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {live_data['usd']:.2f}</div>
                <div style="font-size: 0.7rem; opacity: 0.7;">Live forex</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Details Section
        st.markdown("<br>", unsafe_allow_html=True)
        detail_cols = st.columns(2)
        
        with detail_cols[0]:
            st.markdown("""
            <div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #d4af37;">
                <h4 style="margin-top: 0; color: #1a1a1a;">🟡 Gold Details</h4>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Int'l Price:</strong> ${:,.2f}/oz</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Local Tola:</strong> Rs {:,.0f}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Dubai:</strong> AED {:,.0f}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Updated:</strong> {}</p>
            </div>
            """.format(live_data['gold'], gold_tola, gold_dubai_tola, live_data['time']), unsafe_allow_html=True)
            
        with detail_cols[1]:
            st.markdown("""
            <div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #C0C0C0;">
                <h4 style="margin-top: 0; color: #1a1a1a;">⚪ Silver Details</h4>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Int'l Price:</strong> ${:,.2f}/oz</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Local Tola:</strong> Rs {:,.0f}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Premium:</strong> Rs {:,}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Status:</strong> 🟢 Live</p>
            </div>
            """.format(live_data['silver'], silver_tola, int(st.session_state.new_silver)), unsafe_allow_html=True)
    
    # TAB 3: History
    with tabs[2]:
        st.markdown("### Rate History")
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
                    df = df.rename(columns={
                        'date': 'Date/Time',
                        'gold_pk': 'Gold (PKR)',
                        'silver_pk': 'Silver (PKR)',
                        'usd': 'USD Rate'
                    })
                    
                    st.dataframe(df.sort_values('Date/Time', ascending=False), 
                                use_container_width=True, hide_index=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export CSV", csv, 
                                     f"rates_{datetime.now().strftime('%Y%m%d')}.csv", 
                                     "text/csv")
                else:
                    st.info("No records found.")
        except:
            st.info("No history available. Publish rates to create history.")
    
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
                    
                    chart = alt.Chart(df).mark_line(
                        point=True,
                        color='#d4af37',
                        strokeWidth=3
                    ).encode(
                        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%d %b')),
                        y=alt.Y('gold_pk:Q', title='Rate (PKR)', scale=alt.Scale(zero=False)),
                        tooltip=[
                            alt.Tooltip('date:T', title='Date', format='%Y-%m-%d %H:%M'),
                            alt.Tooltip('gold_pk:Q', title='Gold', format='Rs ,.0f')
                        ]
                    ).properties(height=400).configure_view(strokeWidth=0)
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("High", f"Rs {df['gold_pk'].max():,.0f}")
                    col2.metric("Low", f"Rs {df['gold_pk'].min():,.0f}")
                    col3.metric("Avg", f"Rs {df['gold_pk'].mean():,.0f}")
                else:
                    st.info("Need 2+ records for chart.")
        except:
            st.info("Chart available after first update.")

# 11. FOOTER (Keep your original exactly)
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
