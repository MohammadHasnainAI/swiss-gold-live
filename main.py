# 10. PROFESSIONAL ADMIN DASHBOARD
# Custom CSS for modern admin panel
st.markdown("""
<style>
/* Admin Dashboard Premium Styles */
.admin-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

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

.stTextInput input {
    border-radius: 10px !important;
    border: 2px solid #e0e0e0 !important;
    padding: 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s !important;
}

.stTextInput input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Metric Cards */
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

/* Control Buttons */
.control-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    margin: 0.25rem 0;
}

.control-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.control-btn:active {
    transform: scale(0.95);
}

/* Premium Buttons */
.premium-btn {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border: none;
    color: white;
    padding: 1rem 2rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    width: 100%;
    margin-top: 1rem;
}

.premium-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(255,255,255,0.1);
    padding: 0.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    color: #666;
    transition: all 0.3s;
}

.stTabs [aria-selected="true"] {
    background: white !important;
    color: #667eea !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* History Table Styling */
.history-table {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* Logout Button */
.logout-btn {
    background: #ff4757;
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 20px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s;
    float: right;
    margin-bottom: 1rem;
}

.logout-btn:hover {
    background: #ff3838;
    transform: scale(1.05);
}

/* Success/Error Messages */
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

/* Premium Input Styling */
.premium-input {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 1rem;
    font-size: 1.2rem;
    font-weight: 700;
    text-align: center;
    color: #333;
    width: 100%;
    margin: 0.5rem 0;
}

/* Chart Container */
.chart-container {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize auth state
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# Login Screen
if not st.session_state.admin_auth:
    st.markdown("""
    <div class="login-card">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
        <div class="admin-title">Admin Portal</div>
        <div class="admin-subtitle">Secure Access Required</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("", type="password", placeholder="Enter admin password...", label_visibility="collapsed")
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
                                    value=current_val, 
                                    step=step_val,
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
                <div class="metric-value">Rs {current_val:,}</div>
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
                <div style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">Rs {st.session_state.new_gold:,}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Added to base rate</div>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[1]:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚪</div>
                <div style="font-size: 0.9rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Silver Premium</div>
                <div style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">Rs {st.session_state.new_silver:,}</div>
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
            - **Premium Applied:** Rs {st.session_state.new_silver}
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
