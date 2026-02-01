# 10. PROFESSIONAL ADMIN DASHBOARD (FIXED CHARTS & RESET)
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
.login-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
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
.control-box {
    background: #fafafa;
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid #e0e0e0;
    margin-top: 1rem;
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
.warning-banner {
    background: #fff3cd;
    color: #856404;
    padding: 0.75rem;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 1rem 0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize reset confirmation states
if "confirm_reset_history" not in st.session_state:
    st.session_state.confirm_reset_history = False
if "confirm_reset_chart" not in st.session_state:
    st.session_state.confirm_reset_chart = False

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
    
    # TAB 1: Update Rates (UNCHANGED WORKING VERSION)
    with tabs[0]:
        st.markdown("### Select Metal")
        
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("🟡 GOLD", use_container_width=True, 
                        type="primary" if st.session_state.selected_metal == "Gold" else "secondary"):
                st.session_state.selected_metal = "Gold"
                st.rerun()
        
        with btn_cols[1]:
            if st.button("⚪ SILVER", use_container_width=True,
                        type="primary" if st.session_state.selected_metal == "Silver" else "secondary"):
                st.session_state.selected_metal = "Silver"
                st.rerun()
        
        if st.session_state.selected_metal == "Gold":
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### 🟡 Gold Premium Control")
            
            step = 500
            current = int(st.session_state.new_gold)
            
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 500", use_container_width=True):
                    st.session_state.new_gold = max(0, current - 500)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 500", use_container_width=True):
                    st.session_state.new_gold = current + 500
                    st.rerun()
            
            val = st.number_input("Gold Premium", value=current, step=step)
            st.session_state.new_gold = val
            
            calculated = ((live_data['gold'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_gold
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro">
                    <div class="metric-label-pro">Premium</div>
                    <div class="metric-value-pro" style="color: #d4af37;">Rs {int(st.session_state.new_gold):,}</div>
                </div>
                <div class="metric-card-pro">
                    <div class="metric-label-pro">Final Rate</div>
                    <div class="metric-value-pro">Rs {calculated:,.0f}</div>
                </div>
                <div class="metric-card-pro">
                    <div class="metric-label-pro">USD</div>
                    <div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="control-box">', unsafe_allow_html=True)
            st.markdown("### ⚪ Silver Premium Control")
            
            step = 50
            current = int(st.session_state.new_silver)
            
            adj_cols = st.columns([1, 1, 2])
            with adj_cols[0]:
                if st.button("➖ 50", use_container_width=True, key="s1"):
                    st.session_state.new_silver = max(0, current - 50)
                    st.rerun()
            with adj_cols[1]:
                if st.button("➕ 50", use_container_width=True, key="s2"):
                    st.session_state.new_silver = current + 50
                    st.rerun()
            
            val = st.number_input("Silver Premium", value=current, step=step, key="sil_in")
            st.session_state.new_silver = val
            
            calculated = ((live_data['silver'] / 31.1035) * 11.66 * live_data['usd']) + st.session_state.new_silver
            
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;">
                    <div class="metric-label-pro">Premium</div>
                    <div class="metric-value-pro" style="color: #666;">Rs {int(st.session_state.new_silver):,}</div>
                </div>
                <div class="metric-card-pro" style="border-bottom-color: #C0C0C0;">
                    <div class="metric-label-pro">Final Rate</div>
                    <div class="metric-value-pro">Rs {calculated:,.0f}</div>
                </div>
                <div class="metric-card-pro">
                    <div class="metric-label-pro">USD</div>
                    <div class="metric-value-pro" style="font-size: 1.4rem;">Rs {live_data['usd']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 PUBLISH RATE", type="primary", use_container_width=True):
            if repo:
                try:
                    new_settings = {
                        "gold_premium": int(st.session_state.new_gold), 
                        "silver_premium": int(st.session_state.new_silver)
                    }
                    
                    try:
                        contents = repo.get_contents("manual.json")
                        repo.update_file(contents.path, f"Update - {datetime.now().strftime('%H:%M')}", 
                                       json.dumps(new_settings), contents.sha)
                    except:
                        repo.create_file("manual.json", "Init", json.dumps(new_settings))
                    
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
                    
                    st.markdown('<div class="success-msg">✅ Published! Live in 5 seconds.</div>', unsafe_allow_html=True)
                    manual_refresh()
                    
                except Exception as e:
                    st.markdown(f'<div class="error-msg">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-msg">❌ GitHub not connected</div>', unsafe_allow_html=True)
    
    # TAB 2: Statistics (UNCHANGED)
    with tabs[1]:
        st.markdown("### Market Overview")
        
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.markdown(f"""
            <div style="background: #1a1a1a; color: #d4af37; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #d4af37;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🟡</div>
                <div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">Gold Premium</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {int(st.session_state.new_gold):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[1]:
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 1.5rem; text-align: center; border: 2px solid #C0C0C0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚪</div>
                <div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px;">Silver Premium</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0; color: #666;">Rs {int(st.session_state.new_silver):,}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #d4af37 0%, #f4e5c2 100%); color: #1a1a1a; border-radius: 12px; padding: 1.5rem; text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💵</div>
                <div style="font-size: 0.8rem; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px;">USD/PKR</div>
                <div style="font-size: 1.8rem; font-weight: 800; margin: 0.5rem 0;">Rs {live_data['usd']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        detail_cols = st.columns(2)
        
        with detail_cols[0]:
            st.markdown("""
            <div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #d4af37;">
                <h4 style="margin-top: 0; color: #1a1a1a;">🟡 Gold Details</h4>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Int'l:</strong> ${:,.2f}/oz</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Tola:</strong> Rs {:,.0f}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Dubai:</strong> AED {:,.0f}</p>
            </div>
            """.format(live_data['gold'], gold_tola, gold_dubai_tola), unsafe_allow_html=True)
            
        with detail_cols[1]:
            st.markdown("""
            <div style="background: #fafafa; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #C0C0C0;">
                <h4 style="margin-top: 0; color: #1a1a1a;">⚪ Silver Details</h4>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Int'l:</strong> ${:,.2f}/oz</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Tola:</strong> Rs {:,.0f}</p>
                <p style="margin: 0.5rem 0; color: #555;"><strong>Premium:</strong> Rs {:,}</p>
            </div>
            """.format(live_data['silver'], silver_tola, int(st.session_state.new_silver)), unsafe_allow_html=True)
    
    # TAB 3: History (WITH RESET BUTTON)
    with tabs[2]:
        st.markdown("### Rate History")
        
        # Reset functionality
        reset_col1, reset_col2 = st.columns([3, 1])
        with reset_col1:
            st.caption("Last 60 records")
        with reset_col2:
            if st.button("🗑️ Reset All", type="secondary", key="reset_hist_btn"):
                st.session_state.confirm_reset_history = True
        
        if st.session_state.confirm_reset_history:
            st.markdown('<div class="warning-banner">⚠️ This will delete all history permanently!</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes, Delete", type="primary", key="confirm_yes_hist"):
                    if repo:
                        try:
                            empty = []
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset history", json.dumps(empty), h_content.sha)
                            st.session_state.confirm_reset_history = False
                            st.success("✅ History cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            with c2:
                if st.button("❌ Cancel", key="cancel_hist"):
                    st.session_state.confirm_reset_history = False
                    st.rerun()
        
        # Display history
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 0:
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
                    st.info("📭 History is empty. Publish rates to build history.")
            else:
                st.error("GitHub not connected")
        except Exception as e:
            st.info("No history available yet.")
    
    # TAB 4: Charts (FIXED WITH GOLD/SILVER SELECTOR & RESET)
    with tabs[3]:
        st.markdown("### Price Trends")
        
        # Chart controls
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
        
        with ctrl_col1:
            chart_metal = st.selectbox("Select Metal:", ["Gold", "Silver"], key="chart_selector")
        
        with ctrl_col3:
            if st.button("🗑️ Reset", type="secondary", key="reset_chart_btn"):
                st.session_state.confirm_reset_chart = True
        
        # Reset confirmation
        if st.session_state.confirm_reset_chart:
            st.markdown('<div class="warning-banner">⚠️ Delete all chart data?</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Delete", type="primary", key="confirm_yes_chart"):
                    if repo:
                        try:
                            empty = []
                            h_content = repo.get_contents("history.json")
                            repo.update_file(h_content.path, "Reset chart data", json.dumps(empty), h_content.sha)
                            st.session_state.confirm_reset_chart = False
                            st.success("✅ Data cleared!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            with c2:
                if st.button("❌ Cancel", key="cancel_chart"):
                    st.session_state.confirm_reset_chart = False
                    st.rerun()
        
        # Chart display
        try:
            if repo:
                contents = repo.get_contents("history.json")
                history_data = json.loads(contents.decoded_content.decode())
                
                if history_data and len(history_data) > 1:
                    df = pd.DataFrame(history_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    
                    # Ensure numeric columns
                    df['gold_pk'] = pd.to_numeric(df['gold_pk'], errors='coerce')
                    df['silver_pk'] = pd.to_numeric(df['silver_pk'], errors='coerce')
                    
                    # Select data based on metal
                    if chart_metal == "Gold":
                        y_col = 'gold_pk'
                        color = '#d4af37'
                        title = "Gold Rate Trend"
                    else:
                        y_col = 'silver_pk'
                        color = '#C0C0C0'
                        title = "Silver Rate Trend"
                    
                    # Create chart with proper configuration
                    chart = alt.Chart(df).mark_line(
                        point=True,
                        color=color,
                        strokeWidth=3
                    ).encode(
                        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%d %b %H:%M')),
                        y=alt.Y(f'{y_col}:Q', title='Rate (PKR)', scale=alt.Scale(zero=False)),
                        tooltip=[
                            alt.Tooltip('date:T', title='Date', format='%Y-%m-%d %H:%M'),
                            alt.Tooltip(f'{y_col}:Q', title=chart_metal, format='Rs ,.0f')
                        ]
                    ).properties(
                        title=title,
                        height=400
                    ).configure_axis(
                        grid=True,
                        gridColor='#f0f0f0',
                        labelFontSize=12,
                        titleFontSize=14
                    ).configure_view(
                        strokeWidth=0,
                        fill='white'
                    ).configure_title(
                        fontSize=16,
                        fontWeight=800,
                        color='#1a1a1a'
                    )
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Statistics for selected metal
                    stats_cols = st.columns(3)
                    with stats_cols[0]:
                        st.metric("Highest", f"Rs {df[y_col].max():,.0f}")
                    with stats_cols[1]:
                        st.metric("Lowest", f"Rs {df[y_col].min():,.0f}")
                    with stats_cols[2]:
                        st.metric("Average", f"Rs {df[y_col].mean():,.0f}")
                else:
                    st.info("📊 Need at least 2 records to generate chart. Publish rates multiple times.")
        except Exception as e:
            st.error(f"Chart error: {str(e)}")
            st.info("Make sure history exists and contains valid data.")

# 11. FOOTER (UNCHANGED)
st.markdown("""
<div class="footer">
<strong>Islam Jewellery</strong> website shows approximate gold prices.<br>
⚠️ <strong>Disclaimer:</strong> Verify with shop before buying.
</div>
""", unsafe_allow_html=True)
