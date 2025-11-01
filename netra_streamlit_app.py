import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="N.E.T.R.A. Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# North-East India Locations Database
NE_LOCATIONS = {
    'Guwahati_Airport': {'lat': 26.1061, 'lon': 91.5859, 'name': 'Guwahati Airport Road, Assam', 'state': 'Assam'},
    'Imphal_City': {'lat': 24.8170, 'lon': 93.9368, 'name': 'Imphal City Center, Manipur', 'state': 'Manipur'},
    'Kohima_NH29': {'lat': 25.6747, 'lon': 94.1078, 'name': 'Kohima NH-29, Nagaland', 'state': 'Nagaland'},
    'Shillong_Bypass': {'lat': 25.5788, 'lon': 91.8933, 'name': 'Shillong Bypass, Meghalaya', 'state': 'Meghalaya'},
    'Agartala_Station': {'lat': 23.8315, 'lon': 91.2868, 'name': 'Agartala Station, Tripura', 'state': 'Tripura'},
    'Itanagar_Zero': {'lat': 27.0844, 'lon': 93.6053, 'name': 'Itanagar Zero Point, Arunachal Pradesh', 'state': 'Arunachal Pradesh'},
    'Aizawl_NH54': {'lat': 23.7271, 'lon': 92.7176, 'name': 'Aizawl NH-54, Mizoram', 'state': 'Mizoram'},
    'Dimapur_Junction': {'lat': 25.9097, 'lon': 93.7267, 'name': 'Dimapur Junction, Nagaland', 'state': 'Nagaland'},
    'Silchar_Medical': {'lat': 24.8333, 'lon': 92.7789, 'name': 'Silchar Medical Road, Assam', 'state': 'Assam'},
    'Tinsukia_Border': {'lat': 27.4900, 'lon': 95.3600, 'name': 'Tinsukia Border, Assam', 'state': 'Assam'}
}

# NetraAI Engine
class NetraAI:
    def __init__(self):
        self.sensor_weights = {
            'fume': 0.20, 'metal': 0.18, 'gpr': 0.15,
            'ground_cv': 0.12, 'drone_cv': 0.15,
            'disturbance': 0.10, 'thermal': 0.10
        }
    
    def calculate_threat_probability(self, sensors):
        weighted_score = sum(sensors[s] * w for s, w in self.sensor_weights.items())
        correlation_boost = 0
        if sensors['fume'] > 70 and sensors['metal'] > 70:
            correlation_boost += 12
        if abs(sensors['drone_cv'] - sensors['ground_cv']) < 15:
            correlation_boost += 8
        if sensors['thermal'] > 60 and sensors['fume'] > 60:
            correlation_boost += 7
        return min(100, round(weighted_score + correlation_boost, 2))
    
    def get_threat_level(self, probability):
        if probability >= 75:
            return "🔴 CRITICAL", "#dc2626"
        elif probability >= 50:
            return "🟡 HIGH", "#f59e0b"
        elif probability >= 25:
            return "🟢 MODERATE", "#10b981"
        else:
            return "⚪ LOW", "#3b82f6"

# Initialize AI
netra_ai = NetraAI()

# Initialize session state
if 'threat_history' not in st.session_state:
    st.session_state.threat_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ N.E.T.R.A. COMMAND CENTER</h1>
    <p>Next-Gen Eye for Threat Recognition & Analysis</p>
    <p>📍 North-East India Operations | ⏰ 2025-11-01 17:35:02 UTC</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=N.E.T.R.A.+System", use_column_width=True)
    
    st.markdown("### 🎛️ Navigation")
    page = st.radio("", ["🏠 Dashboard", "🔍 Live Analysis", "🗺️ Regional Map", "📊 Batch Analysis", "📄 Reports", "⚙️ Settings"])
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Active Locations", "10")
    st.metric("System Health", "98%")
    st.metric("Threats Detected", len(st.session_state.threat_history))

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown("## 📊 Real-Time Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><h3>✅ 10</h3><p>Active Locations</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>🔴 2</h3><p>Critical Threats</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>🟡 3</h3><p>High Alerts</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><h3>📊 98%</h3><p>System Health</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sample threat timeline
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 24-Hour Threat Timeline")
        hours = list(range(24))
        threats = [20 + np.random.randint(-10, 30) for _ in range(24)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=threats, mode='lines+markers', 
                                fill='tozeroy', line=dict(color='#667eea', width=3)))
        fig.update_layout(height=400, template='plotly_dark',
                         xaxis_title='Hour', yaxis_title='Threat Level (%)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🥧 Threat Distribution")
        labels = ['Critical', 'High', 'Moderate', 'Low']
        values = [2, 3, 3, 2]
        colors = ['#dc2626', '#f59e0b', '#10b981', '#3b82f6']
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, 
                                     marker=dict(colors=colors))])
        fig.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

# Live Analysis Page
elif page == "🔍 Live Analysis":
    st.markdown("## 🔍 Live Threat Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎛️ Sensor Controls")
        
        location_key = st.selectbox("📍 Select Location", 
                                   options=list(NE_LOCATIONS.keys()),
                                   format_func=lambda x: NE_LOCATIONS[x]['name'])
        
        st.markdown("#### 🚗 Rover Sensors")
        fume = st.slider("💨 Fume Sensor", 0, 100, 50)
        metal = st.slider("🔩 Metal Detector", 0, 100, 50)
        gpr = st.slider("📡 GPR Sensor", 0, 100, 50)
        ground_cv = st.slider("👁️ Ground Vision", 0, 100, 50)
        
        st.markdown("#### 🚁 Drone Sensors")
        drone_cv = st.slider("🚁 Drone Vision", 0, 100, 50)
        disturbance = st.slider("🌍 Soil Disturbance", 0, 100, 50)
        thermal = st.slider("🌡️ Thermal Scan", 0, 100, 50)
        
        if st.button("🔍 ANALYZE THREAT NOW", type="primary"):
            sensors = {
                'fume': fume, 'metal': metal, 'gpr': gpr,
                'ground_cv': ground_cv, 'drone_cv': drone_cv,
                'disturbance': disturbance, 'thermal': thermal
            }
            
            probability = netra_ai.calculate_threat_probability(sensors)
            threat_level, color = netra_ai.get_threat_level(probability)
            
            location = NE_LOCATIONS[location_key]
            
            # Store in history
            st.session_state.threat_history.append({
                'timestamp': datetime.utcnow(),
                'location': location['name'],
                'probability': probability,
                'level': threat_level
            })
            
            with col2:
                st.markdown("### 🎯 Analysis Results")
                st.markdown(f"<h1 style='text-align:center;color:{color};'>{probability:.1f}%</h1>", 
                           unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;color:{color};'>{threat_level}</h3>", 
                           unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown(f"**📍 Location:** {location['name']}")
                st.markdown(f"**🗺️ State:** {location['state']}")
                st.markdown(f"**📐 Coordinates:** {location['lat']:.4f}°N, {location['lon']:.4f}°E")
                
                # Sensor readings
                st.markdown("### 📊 Sensor Readings")
                sensor_df = pd.DataFrame({
                    'Sensor': list(sensors.keys()),
                    'Value': list(sensors.values())
                })
                st.dataframe(sensor_df, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 System Status")
        st.success("✅ Rover: Online (87%)")
        st.success("✅ Drone: Active (50m)")
        st.success("✅ Comms: Connected")
        st.info("🧠 AI: Bayesian Fusion Active")

# Regional Map Page
elif page == "🗺️ Regional Map":
    st.markdown("## 🗺️ North-East India Threat Map")
    
    m = folium.Map(location=[26.0, 92.5], zoom_start=6)
    
    for key, loc in NE_LOCATIONS.items():
        threat = np.random.randint(0, 100)
        color = 'red' if threat >= 75 else 'orange' if threat >= 50 else 'green'
        
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=f"{loc['name']}<br>Threat: {threat}%%",
            tooltip=loc['name'],
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    folium_static(m, width=1400, height=600)

# Batch Analysis Page
elif page == "📊 Batch Analysis":
    st.markdown("## 📊 Batch Threat Analysis")
    
    if st.button("🔍 Run Batch Analysis on All Locations"):
        with st.spinner("Analyzing all 10 locations..."):
            results = []
            progress_bar = st.progress(0)
            
            for idx, (key, loc) in enumerate(NE_LOCATIONS.items()):
                sensors = {s: np.random.randint(10, 95) for s in netra_ai.sensor_weights.keys()}
                prob = netra_ai.calculate_threat_probability(sensors)
                level, _ = netra_ai.get_threat_level(prob)
                
                results.append({
                    'Location': loc['name'],
                    'State': loc['state'],
                    'Probability': prob,
                    'Level': level
                })
                
                progress_bar.progress((idx + 1) / len(NE_LOCATIONS))
                time.sleep(0.2)
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df, x='Location', y='Probability', color='Level',
                           title='Threat Levels by Location')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                state_avg = df.groupby('State')['Probability'].mean().reset_index()
                fig = px.pie(state_avg, values='Probability', names='State',
                           title='Average Threat by State')
                st.plotly_chart(fig, use_container_width=True)

# Reports Page
elif page == "📄 Reports":
    st.markdown("## 📄 Threat Reports")
    
    report_type = st.selectbox("Select Report Type", 
                              ["Threat Assessment", "Daily Summary", "Weekly Analysis"])
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    if st.button("📊 Generate Report"):
        st.success("✅ Report generated successfully!")
        st.download_button("📥 Download Report (PDF)", 
                         data="Sample report content", 
                         file_name="netra_report.pdf")

# Settings Page
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ System Settings")
    
    st.markdown("### 🚨 Alert Thresholds")
    critical = st.slider("🔴 Critical Threshold (%)", 0, 100, 75)
    high = st.slider("🟡 High Threshold (%)", 0, 100, 50)
    moderate = st.slider("🟢 Moderate Threshold (%)", 0, 100, 25)
    
    st.markdown("### 🔔 Notifications")
    email_alerts = st.checkbox("Email Alerts", value=True)
    sms_alerts = st.checkbox("SMS Alerts", value=False)
    
    if st.button("💾 Save Settings"):
        st.success("✅ Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    🛡️ N.E.T.R.A. Command Center v1.0 | 
    🔒 Classification: RESTRICTED | 
    © 2025 Defense Systems
</div>
""", unsafe_allow_html=True)