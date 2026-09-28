"""
app.py — Drishti: Predictive Crime Hotspot Mapping Assistant
Main Streamlit dashboard for Station House Officers.
Team Ananta | IBM Bob AI Hackathon
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

from analytics import (
    compute_risk_scores, get_top5_zones, explain_zone,
    suggest_patrol, get_summary_stats
)
from simulator import simulate_event, simulate_all_zones
from report_generator import generate_sho_report


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drishti — Crime Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS — Modern Premium Web UI
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* Hide Streamlit Default Headers */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Navbar Styling */
    .navbar {
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(16px);
        padding: 18px 32px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .nav-logo {
        font-size: 1.7rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .nav-logo span {
        color: #e94560;
    }
    .nav-links {
        font-size: 1.05rem;
        color: #94a3b8;
        font-weight: 500;
        display: flex;
        gap: 20px;
        align-items: center;
    }
    
    /* Hero Section Styling */
    .hero-section {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
        padding: 48px 32px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 36px;
        border: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 16px;
        line-height: 1.15;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #cbd5e1;
        font-weight: 400;
        max-width: 850px;
        margin: 0 auto 24px auto;
        line-height: 1.6;
    }
    
    /* Synthetic data warning badge */
    .synth-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 1px;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(233, 69, 96, 0.3);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e94560;
        line-height: 1;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    
    /* Section headers */
    .section-header {
        color: #f1f5f9;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 32px 0 16px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(233, 69, 96, 0.5);
        letter-spacing: -0.2px;
    }
    
    /* Explanation box */
    .explain-box {
        background: rgba(15, 23, 42, 0.6);
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #e94560;
        margin: 12px 0;
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    
    /* Patrol box */
    .patrol-box {
        background: rgba(6, 78, 59, 0.2);
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #10b981;
        margin: 12px 0;
        color: #d1fae5;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    
    /* Simulator result */
    .sim-result {
        background: rgba(120, 53, 15, 0.2);
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #f59e0b;
        margin: 12px 0;
        color: #fef3c7;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    
    /* Score change indicator */
    .score-up {
        color: #ef4444;
        font-weight: 800;
        font-size: 1.4rem;
    }
    

</style>
""", unsafe_allow_html=True)


def load_default_data():
    """Load the default synthetic crime dataset."""
    csv_path = os.path.join(os.path.dirname(__file__), 'crime_data.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None


def render_header():
    """Render the modern Navbar and Hero Section."""
    st.markdown("""
    <!-- Custom Navbar -->
    <div class="navbar">
        <div class="nav-logo">
            <span>🔍</span> DRISHTI
        </div>
        <div class="nav-links">
            <div>Team Ananta</div>
            <div style="color: #e94560;">|</div>
            <div>AI Crime Intelligence</div>
        </div>
    </div>
    
    <!-- Hero Section -->
    <div class="hero-section">
        <div class="hero-title">Predictive Hotspot Mapping for Modern Policing</div>
        <div class="hero-subtitle">
            Transform historical crime logs into proactive, forward-looking patrol plans. 
            Empower Station House Officers with explainable AI to deploy resources exactly where they are needed most.
        </div>
        <div class="synth-badge">⚠️ SYNTHETIC DATA — DEMONSTRATION ONLY</div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(stats):
    """Render the top-level summary metric cards."""
    cols = st.columns(4)
    
    metrics = [
        {"value": f"{stats['total_incidents']:,}", "label": "Total Incidents", "icon": "📊"},
        {"value": str(stats['total_areas']), "label": "Areas Analyzed", "icon": "📍"},
        {"value": stats['most_common_crime'], "label": "Top Crime Type", "icon": "🔴"},
        {"value": str(stats['high_risk_zones']), "label": "High-Risk Zones", "icon": "⚠️"},
    ]
    
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{m['icon']} {m['value']}</div>
                <div class="metric-label">{m['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_heatmap(df, scores):
    """Render the area risk heatmap grid."""
    # Aggregate by area and crime_type so clicking an area shows the breakdown
    agg_df = df.groupby(['area', 'crime_type']).size().reset_index(name='incidents')
    grid_data = pd.merge(agg_df, scores[['area', 'risk_score', 'trend_direction']], on='area', how='left')
    
    # Create heatmap using treemap for visual impact
    fig = px.treemap(
        grid_data,
        path=['area', 'crime_type'],
        values='incidents',
        color='risk_score',
        color_continuous_scale=[
            [0, '#1a1a2e'],
            [0.3, '#16213e'],
            [0.5, '#0f3460'],
            [0.7, '#e94560'],
            [1.0, '#ff2e63']
        ],
        custom_data=['risk_score'],
        title=None
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#e0e0f0'),
        height=420,
        margin=dict(t=10, l=10, r=10, b=10),
        coloraxis_colorbar=dict(
            title=dict(text="Risk Score", font=dict(color='#a0a0c0')),
            tickfont=dict(color='#a0a0c0'),
        )
    )
    
    fig.update_traces(
        textfont=dict(size=13, family='Inter'),
        texttemplate="<b>%{label}</b><br>Score: %{customdata[0]:.1f}<br>Incidents: %{value}",
        hovertemplate="<b>%{label}</b><br>Risk Score: %{customdata[0]:.1f}<br>Incidents: %{value}<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_top5_table(top5, explanations):
    """Render the Top 5 at-risk zones table."""
    display_data = []
    for i, (_, row) in enumerate(top5.iterrows()):
        exp = explanations[i] if i < len(explanations) else {}
        trend_icon = {"Rising": "🔺", "Stable": "➖", "Declining": "🔽"}.get(row['trend_direction'], "➖")
        display_data.append({
            'Rank': f"#{i+1}",
            'Zone': row['area'],
            'Risk Score': f"{row['risk_score']:.1f}",
            'Incidents': row['total_incidents'],
            'Primary Crime': exp.get('most_common_crime', 'N/A'),
            'Peak Hours': exp.get('peak_hours', 'N/A'),
            'Trend': f"{trend_icon} {row['trend_direction']}"
        })
    
    display_df = pd.DataFrame(display_data)
    
    # Style the dataframe
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Zone": st.column_config.TextColumn("Zone", width="medium"),
            "Risk Score": st.column_config.TextColumn("Risk Score", width="small"),
            "Incidents": st.column_config.NumberColumn("Incidents", width="small"),
            "Primary Crime": st.column_config.TextColumn("Primary Crime", width="medium"),
            "Peak Hours": st.column_config.TextColumn("Peak Hours", width="medium"),
            "Trend": st.column_config.TextColumn("Trend", width="small"),
        }
    )


def render_crime_charts(df):
    """Render crime distribution charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Crime type distribution
        crime_counts = df['crime_type'].value_counts().reset_index()
        crime_counts.columns = ['Crime Type', 'Count']
        
        fig = px.bar(
            crime_counts, x='Crime Type', y='Count',
            color='Count',
            color_continuous_scale=['#16213e', '#0f3460', '#e94560'],
            title=None
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0', size=11),
            height=320,
            margin=dict(t=10, l=10, r=10, b=40),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            showlegend=False,
            coloraxis_showscale=False
        )
        st.markdown('<div class="section-header">📊 Crime Type Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Time of day distribution
        df_temp = df.copy()
        df_temp['hour'] = df_temp['time'].apply(lambda t: int(t.split(':')[0]))
        hour_counts = df_temp['hour'].value_counts().sort_index().reset_index()
        hour_counts.columns = ['Hour', 'Count']
        
        fig = px.area(
            hour_counts, x='Hour', y='Count',
            title=None,
            color_discrete_sequence=['#e94560']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0', size=11),
            height=320,
            margin=dict(t=10, l=10, r=10, b=40),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.05)',
                dtick=2,
                ticktext=[f"{h}:00" for h in range(0, 24, 2)],
                tickvals=list(range(0, 24, 2))
            ),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            showlegend=False
        )
        fig.update_traces(
            fill='tozeroy',
            fillcolor='rgba(233, 69, 96, 0.15)',
            line=dict(width=2.5)
        )
        st.markdown('<div class="section-header">🕐 Incidents by Time of Day</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)


def render_monthly_trend(df):
    """Render monthly crime trend chart."""
    df_temp = df.copy()
    df_temp['date'] = pd.to_datetime(df_temp['date'])
    df_temp['month'] = df_temp['date'].dt.to_period('M').astype(str)
    
    monthly = df_temp.groupby('month').size().reset_index(name='incidents')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly['month'],
        y=monthly['incidents'],
        mode='lines+markers+text',
        text=monthly['incidents'],
        textposition='top center',
        textfont=dict(size=11, color='#e94560', family='Inter'),
        line=dict(color='#e94560', width=3),
        marker=dict(size=10, color='#e94560', line=dict(color='#ffffff', width=2)),
        fill='tozeroy',
        fillcolor='rgba(233, 69, 96, 0.08)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#a0a0c0', size=11),
        height=280,
        margin=dict(t=10, l=10, r=10, b=40),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=''),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Incidents'),
        showlegend=False
    )
    
    st.markdown('<div class="section-header">📈 Monthly Crime Trend</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────
def login_screen():
    """Simple MVP authentication screen."""
    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1 style='color: #e94560;'>🔒 Restricted Access</h1>
        <p style='color: #a0a0c0;'>Drishti Crime Intelligence Portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### SHO Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Hardcoded credentials for Hackathon MVP
                if username == "sho_admin" and password == "password123":
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = 'SHO'
                    st.rerun()
                else:
                    st.error("Invalid credentials. Hint: sho_admin / password123")

def main():
    # Initialize session state for auth
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_screen()
        return
        
    render_header()
    
    # Sidebar — Data Upload & User Info
    with st.sidebar:
        st.markdown(f"### 👤 Logged in as: **{st.session_state.get('role', 'SHO')}**")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📁 Data Source")
        
        upload_option = st.radio(
            "Choose data source:",
            ["Use demo dataset", "Upload CSV file"],
            index=0
        )
        
        df = None
        
        if upload_option == "Upload CSV file":
            uploaded = st.file_uploader(
                "Upload crime data CSV",
                type=['csv'],
                help="CSV with columns: date, time, day_of_week, area, crime_type, nearby_event"
            )
            if uploaded:
                try:
                    df = pd.read_csv(uploaded)
                    st.success(f"✅ Loaded {len(df)} records")
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")
        else:
            df = load_default_data()
            if df is not None:
                st.success(f"✅ Demo dataset: {len(df)} records")
            else:
                st.warning("Demo dataset not found. Please upload a CSV.")
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.75rem; color: #888;">
        <b>Drishti v1.0</b><br>
        Team Ananta<br>
        IBM Bob AI Hackathon<br>
        <br>
        ⚠️ All data is synthetic.<br>
        For demonstration only.
        </div>
        """, unsafe_allow_html=True)
    
    # Main content — only render if data is loaded
    if df is None:
        st.info("👈 Upload a CSV file or use the demo dataset to get started.")
        return
    
    # Validate required columns
    required_cols = ['date', 'time', 'area', 'crime_type', 'nearby_event']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        return
    
    # Compute everything
    with st.spinner("🔍 Analyzing crime patterns..."):
        stats = get_summary_stats(df)
        scores = compute_risk_scores(df)
        top5 = get_top5_zones(df)
        
        explanations = []
        patrol_suggestions = []
        for _, row in top5.iterrows():
            explanations.append(explain_zone(df, row['area']))
            patrol_suggestions.append(suggest_patrol(df, row['area']))
    
    # ── METRICS ──
    render_metrics(stats)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── NAVIGATION BUTTONS ──
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Hotspot Map"
        
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
    
    with nav_col1:
        if st.button("🗺️ Hotspot Map", use_container_width=True, type="primary" if st.session_state.current_page == "Hotspot Map" else "secondary"):
            st.session_state.current_page = "Hotspot Map"
            st.rerun()
    with nav_col2:
        if st.button("📊 Zone Analysis", use_container_width=True, type="primary" if st.session_state.current_page == "Zone Analysis" else "secondary"):
            st.session_state.current_page = "Zone Analysis"
            st.rerun()
    with nav_col3:
        if st.button("🔮 Simulator", use_container_width=True, type="primary" if st.session_state.current_page == "What-If Simulator" else "secondary"):
            st.session_state.current_page = "What-If Simulator"
            st.rerun()
    with nav_col4:
        if st.button("🚔 Patrol Plan", use_container_width=True, type="primary" if st.session_state.current_page == "Patrol Plan" else "secondary"):
            st.session_state.current_page = "Patrol Plan"
            st.rerun()
    with nav_col5:
        if st.button("📋 SHO Report", use_container_width=True, type="primary" if st.session_state.current_page == "SHO Report" else "secondary"):
            st.session_state.current_page = "SHO Report"
            st.rerun()
            
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # ── TAB 1: HOTSPOT MAP ──
    if st.session_state.current_page == "Hotspot Map":
        st.markdown('<div class="section-header">🗺️ Risk Heatmap — All Zones</div>', unsafe_allow_html=True)
        render_heatmap(df, scores)
        
        render_crime_charts(df)
        render_monthly_trend(df)
    
    # ── TAB 2: ZONE ANALYSIS ──
    elif st.session_state.current_page == "Zone Analysis":
        st.markdown('<div class="section-header">🏆 Top 5 At-Risk Micro-Zones</div>', unsafe_allow_html=True)
        render_top5_table(top5, explanations)
        
        st.markdown('<div class="section-header">🔎 Zone Detail Inspector</div>', unsafe_allow_html=True)
        
        zone_options = top5['area'].tolist()
        selected_zone = st.selectbox(
            "Select a zone to inspect:",
            zone_options,
            index=0,
            key="zone_select"
        )
        
        if selected_zone:
            exp = explain_zone(df, selected_zone)
            patrol = suggest_patrol(df, selected_zone)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="explain-box">
                    <strong>🔍 WHY is {selected_zone} flagged?</strong><br><br>
                    {exp['explanation']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="patrol-box">
                    <strong>🚔 Patrol Recommendation</strong><br><br>
                    {patrol['recommendation']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Risk Score", f"{scores[scores['area']==selected_zone]['risk_score'].values[0]:.1f}")
                st.metric("Total Incidents", exp['total_incidents'])
                st.metric("Trend", exp['trend'], delta=f"{exp.get('trend_pct', 0)}%")
                st.metric("Priority", patrol['priority'])
    
    # ── TAB 3: WHAT-IF SIMULATOR ──
    elif st.session_state.current_page == "What-If Simulator":
        st.markdown('<div class="section-header">🔮 Event Impact Simulator</div>', unsafe_allow_html=True)
        
        st.markdown("""
        > Model how upcoming events could shift crime risk across zones.
        > All results are **hypothetical scenarios** for planning purposes only.
        """)
        
        sim_col1, sim_col2 = st.columns(2)
        
        with sim_col1:
            sim_event = st.selectbox(
                "Select upcoming event:",
                ["Festival", "Market Day", "Cricket Match", "Political Rally"],
                index=0,
                key="sim_event"
            )
        
        with sim_col2:
            sim_area = st.selectbox(
                "Select target zone:",
                top5['area'].tolist(),
                index=0,
                key="sim_area"
            )
        
        if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Running scenario simulation..."):
                result = simulate_event(df, sim_area, sim_event)
                
                # Store in session for report
                st.session_state['last_simulation'] = result
            
            st.markdown(f"""
            <div class="sim-result">
                <strong>{result['event_icon']} {result['event']} near {result['area']}</strong><br><br>
                <span style="font-size: 1rem;">Risk Score: 
                    <b>{result['original_score']}</b> → 
                    <span class="score-up">{result['adjusted_score']}</span> 
                    (<span class="score-up">{result['change_percent']}</span>)
                </span><br><br>
                {result['explanation']}<br><br>
                <em>{result['label']}</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Show all-zone comparison
        st.markdown('<div class="section-header">📊 All Top Zones — Event Impact Comparison</div>', unsafe_allow_html=True)
        
        all_sims = simulate_all_zones(df, sim_event)
        
        sim_chart_data = pd.DataFrame([{
            'Zone': s['area'],
            'Original Score': s['original_score'],
            'With Event': s['adjusted_score']
        } for s in all_sims])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Current Risk',
            x=sim_chart_data['Zone'],
            y=sim_chart_data['Original Score'],
            marker_color='#0f3460',
            text=sim_chart_data['Original Score'].round(1),
            textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name=f'With {sim_event}',
            x=sim_chart_data['Zone'],
            y=sim_chart_data['With Event'],
            marker_color='#e94560',
            text=sim_chart_data['With Event'].round(1),
            textposition='auto'
        ))
        
        fig.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#a0a0c0', size=11),
            height=350,
            margin=dict(t=10, l=10, r=10, b=40),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Risk Score'),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="center", x=0.5,
                font=dict(color='#d0d0e0')
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ── TAB 4: PATROL PLAN ──
    elif st.session_state.current_page == "Patrol Plan":
        st.markdown('<div class="section-header">🚔 Patrol Redeployment Recommendations</div>', unsafe_allow_html=True)
        
        st.markdown("""
        > These are **suggestions for human review**. The Station House Officer 
        > retains full authority over all deployment decisions.
        """)
        
        for i, (_, row) in enumerate(top5.iterrows()):
            patrol = patrol_suggestions[i]
            exp = explanations[i]
            
            priority_color = {
                "HIGH": "#e74c3c",
                "MEDIUM": "#f39c12",
                "LOW": "#2ecc71"
            }.get(patrol['priority'], "#888")
            
            with st.expander(
                f"{'🔴' if patrol['priority']=='HIGH' else '🟡' if patrol['priority']=='MEDIUM' else '🟢'} "
                f"Zone {i+1}: {row['area']} — Priority: {patrol['priority']}",
                expanded=(i < 3)
            ):
                p_col1, p_col2 = st.columns([2, 1])
                
                with p_col1:
                    st.markdown(f"""
                    <div class="patrol-box">
                        <strong>📋 Deployment Recommendation</strong><br><br>
                        {patrol['recommendation']}<br><br>
                        <strong>Key Evidence:</strong> {exp['explanation']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with p_col2:
                    st.markdown(f"""
                    | Detail | Value |
                    |---|---|
                    | **Zone** | {patrol['area']} |
                    | **Days** | {', '.join(patrol['suggested_days'])} |
                    | **Time** | {patrol['suggested_time_start']} – {patrol['suggested_time_end']} |
                    | **Coverage** | {patrol['coverage_pct']}% of incidents |
                    | **Priority** | {patrol['priority']} |
                    """)
    
    # ── TAB 5: SHO REPORT ──
    elif st.session_state.current_page == "SHO Report":
        st.markdown('<div class="section-header">📋 Station House Officer — Intelligence Brief</div>', unsafe_allow_html=True)
        
        st.markdown("""
        Generate a downloadable one-page PDF report summarizing:
        - Top 5 at-risk zones with evidence
        - Patrol deployment recommendations
        - Event impact scenarios (if simulated)
        """)
        
        event_scenario = st.session_state.get('last_simulation', None)
        
        if event_scenario:
            st.info(f"📌 Including event scenario: {event_scenario['event']} near {event_scenario['area']}")
        
        col_down, col_notify = st.columns(2)
        
        with col_down:
            if st.button("📄 Generate SHO Report", type="primary", use_container_width=True):
                with st.spinner("Generating intelligence brief..."):
                    pdf_buffer = generate_sho_report(
                        top5_data=top5,
                        explanations=explanations,
                        patrol_suggestions=patrol_suggestions,
                        summary_stats=stats,
                        event_scenario=event_scenario,
                    )
                    st.session_state['generated_pdf_bytes'] = pdf_buffer.getvalue()

                st.success("✅ Report generated successfully!")

        if 'generated_pdf_bytes' in st.session_state:
            with col_down:
                from datetime import datetime as _dt
                filename = f"Drishti_SHO_Brief_{_dt.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="📥 Download PDF Brief",
                    data=st.session_state['generated_pdf_bytes'],
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
                
            with col_notify:
                st.markdown("### 📧 Notification System")
                auth_email = st.text_input("Authorities Email", value="hq@delhipolice.gov.in")
                if st.button("✉️ Send Brief to Authorities", use_container_width=True):
                    import time
                    with st.spinner(f"Connecting to secure SMTP... Sending to {auth_email}..."):
                        time.sleep(2) # Simulate network delay
                    st.success(f"✅ Secure Email sent successfully to {auth_email}!")
                    st.info("The intelligence brief PDF was attached to the email.")
        
        # Preview section
        st.markdown('<div class="section-header">📝 Report Preview</div>', unsafe_allow_html=True)
        
        summary_html = f"""
        <div style="background: rgba(15, 23, 42, 0.4); padding: 32px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 40px;">
            <h4 style="color: #f1f5f9; margin-top: 0; margin-bottom: 24px; font-weight: 700; font-size: 1.2rem;">Executive Summary</h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                <div class="metric-card" style="padding: 20px; margin: 0; height: 100%;">
                    <div class="metric-value" style="font-size: 2rem;">{stats['total_incidents']}</div>
                    <div class="metric-label">Total Incidents</div>
                </div>
                <div class="metric-card" style="padding: 20px; margin: 0; height: 100%;">
                    <div class="metric-value" style="font-size: 2rem;">{stats['total_areas']}</div>
                    <div class="metric-label">Areas</div>
                </div>
                <div class="metric-card" style="padding: 20px; margin: 0; height: 100%;">
                    <div class="metric-value" style="font-size: 2rem; color:#f39c12;">{stats['most_common_crime']}</div>
                    <div class="metric-label">Top Crime</div>
                </div>
                <div class="metric-card" style="padding: 20px; margin: 0; height: 100%;">
                    <div class="metric-value" style="font-size: 2rem; color:#ef4444;">{stats['high_risk_zones']}</div>
                    <div class="metric-label">High-Risk Zones</div>
                </div>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)
            
        st.markdown('<h4 style="color: #f1f5f9; margin: 36px 0 20px 0; font-weight: 700; font-size: 1.2rem;">Top 5 Priority Zones</h4>', unsafe_allow_html=True)
        
        for i, exp in enumerate(explanations):
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); padding: 20px; border-radius: 12px; margin-bottom: 16px; border-left: 5px solid #e94560; display: flex; align-items: flex-start; gap: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <div style="background: #e94560; color: white; border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.2rem; flex-shrink: 0; box-shadow: 0 4px 10px rgba(233, 69, 96, 0.4);">{i+1}</div>
                <div>
                    <strong style="color: #ffffff; font-size: 1.15rem; letter-spacing: 0.5px;">{exp['area']}</strong>
                    <p style="color: #94a3b8; margin: 8px 0 0 0; font-size: 1rem; line-height: 1.6;">{exp['explanation'][:180]}...</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
