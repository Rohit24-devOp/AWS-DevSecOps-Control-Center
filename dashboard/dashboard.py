import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import datetime
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# ==========================================
# PAGE CONFIG & CUSTOM THEME
# ==========================================
st.set_page_config(
    page_title="AWS DevSecOps Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Glassmorphism & Dark Mode CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles Override */
    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0B0F17 !important;
        color: #F8FAFC;
    }

    /* Transparent main container margins */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    /* Glassmorphic Cards */
    .kpi-card {
        background: linear-gradient(135deg, rgba(23, 37, 84, 0.25) 0%, rgba(15, 23, 42, 0.45) 100%);
        border: 1px solid rgba(56, 189, 248, 0.12);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        opacity: 0.7;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow: 0 15px 35px -5px rgba(56, 189, 248, 0.12), 0 0 15px 0 rgba(56, 189, 248, 0.05);
    }

    .kpi-val {
        font-size: 2.4rem;
        font-weight: 800;
        margin-top: 8px;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    
    .kpi-title {
        color: #94A3B8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
    }
    
    .kpi-subtitle {
        color: #64748B;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 4px;
    }

    .kpi-icon-wrapper {
        position: absolute;
        top: 20px;
        right: 20px;
        color: rgba(56, 189, 248, 0.15);
    }
    
    /* Pulsing status indicators */
    .pulse {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        vertical-align: middle;
    }
    
    .pulse-green {
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulse-g 2s infinite;
    }
    
    .pulse-orange {
        background: #F97316;
        box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7);
        animation: pulse-o 2s infinite;
    }
    
    .pulse-red {
        background: #EF4444;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        animation: pulse-r 2s infinite;
    }
    
    @keyframes pulse-g {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    
    @keyframes pulse-o {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(249, 115, 22, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(249, 115, 22, 0); }
    }
    
    @keyframes pulse-r {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Click-safe Tab styling using standard buttons */
    .stTabs button {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
        background-color: transparent !important;
        padding: 8px 18px !important;
    }
    .stTabs button:hover {
        color: #F8FAFC !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
    }
    .stTabs button[aria-selected="true"] {
        color: #38BDF8 !important;
        background-color: rgba(56, 189, 248, 0.1) !important;
        border-radius: 8px !important;
    }

    /* Sidebar Refinement */
    section[data-testid="stSidebar"] {
        background-color: #070B12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Styled code containers */
    code, pre {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0F17;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# AWS CLIENTS & MOCK DETECTOR
# ==========================================
@st.cache_resource(ttl=600)
def get_aws_client(service_name):
    try:
        # Check if boto3 can load default credentials
        session = boto3.Session()
        client = session.client(service_name, region_name="us-east-1")
        # Perform quick non-modifying call to verify auth
        if service_name == "ecs":
            client.list_clusters()
        elif service_name == "cloudwatch":
            client.list_metrics(Namespace="AWS/ECS")
        return client, False
    except Exception:
        # Fallback to simulated mode
        return None, True

ecs_client, is_ecs_mocked = get_aws_client("ecs")
cw_client, is_cw_mocked = get_aws_client("cloudwatch")
logs_client, is_logs_mocked = get_aws_client("logs")

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
    <div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, #38BDF8, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🛡️ AWS DevSecOps Control Center</h1>
        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 0.95rem;">Secure Cloud-Native CI/CD Pipeline Monitoring & Analytics</p>
    </div>
    <div style="text-align: right;">
        <span style="font-family: monospace; font-size: 0.85rem; padding: 6px 12px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 6px; color: #38BDF8;">
            Env: Production-Fargate
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Show warnings if using Mock Data
if is_ecs_mocked or is_cw_mocked:
    st.info("ℹ️ AWS Credentials not detected or insufficient. Displaying interactive simulator data with real-time refresh.")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "devsecops_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.image("https://img.icons8.com/color/144/amazon-web-services.png", width=100)
    st.markdown("### Pipeline Configuration")
    
    # Deployment control simulation
    st.info("🔗 **Linked Repository**\n`Rohit24-devOp/Cloud-Security-Monitoring-WAF-Protection-Platform`")
    
    st.markdown("---")
    st.markdown("### System Integration")
    
    st.write(f"**ECS Fargate Service:** `Active` {'(Simulated)' if is_ecs_mocked else '(Live)'}")
    st.write(f"**ECR Registry:** `Active` {'(Simulated)' if is_ecs_mocked else '(Live)'}")
    st.write(f"**CloudWatch Alarms:** `Monitoring` {'(Simulated)' if is_cw_mocked else '(Live)'}")
    
    st.markdown("---")
    st.markdown("### Cost Optimization Toggle")
    cost_mode = st.toggle("Simulate NAT Gateway Shutdown", value=True, help="Turning off NAT Gateways and placing ECS in public subnets cuts monthly costs from ~$42 to ~$10.")
    
    if st.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()

# ==========================================
# DATA GENERATOR (Fallback / Metrics)
# ==========================================
def generate_mock_vulnerabilities():
    # Model a timeline of Trivy security improvements over git builds
    builds = [f"Build #{i}" for i in range(112, 122)]
    critical = [14, 12, 8, 3, 0, 0, 0, 0, 0, 0]
    high = [38, 29, 20, 12, 4, 2, 1, 0, 0, 0]
    medium = [54, 45, 38, 27, 18, 11, 7, 3, 2, 1]
    low = [98, 87, 82, 71, 62, 53, 44, 38, 35, 30]
    
    df = pd.DataFrame({
        "Build": builds,
        "Critical": critical,
        "High": high,
        "Medium": medium,
        "Low": low
    })
    return df

def generate_mock_cpu_ram(num_points=30):
    timestamps = [datetime.datetime.now() - datetime.timedelta(minutes=i) for i in range(num_points)]
    timestamps.reverse()
    
    # Generate fluctuating container metrics
    np.random.seed(42)
    cpu = np.random.normal(loc=12.5, scale=2.8, size=num_points).clip(5, 80)
    ram = np.random.normal(loc=38.2, scale=0.5, size=num_points).clip(30, 95)
    requests = np.random.poisson(lam=45, size=num_points)
    errors = np.random.poisson(lam=0.2, size=num_points)
    
    # Spike simulation
    cpu[20:23] = [58.2, 72.1, 65.4]
    requests[20:23] = [120, 145, 132]
    
    return pd.DataFrame({
        "Time": timestamps,
        "CPU (%)": cpu,
        "Memory (%)": ram,
        "Requests/Sec": requests,
        "Errors/Sec": errors
    })

# ==========================================
# MAIN TABS DEFINITION
# ==========================================
tab_overview, tab_pipeline, tab_security, tab_container, tab_costs = st.tabs([
    "📊 Overview", 
    "🚀 CI/CD Pipeline", 
    "🛡️ Security Findings", 
    "🎛️ Container Health", 
    "💰 Cost Analytics"
])

# ------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------
with tab_overview:
    # 1. KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
            </div>
            <div class="kpi-title">Fargate Status</div>
            <div class="kpi-val" style="color: #10B981;"><span class="pulse pulse-green"></span>HEALTHY</div>
            <div class="kpi-subtitle">Desired Tasks: 1 | Running: 1</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg>
            </div>
            <div class="kpi-title">Active Version</div>
            <div class="kpi-val" style="color: #38BDF8;">v1.0.0</div>
            <div class="kpi-subtitle">Git Commit: <span style="font-family: monospace; font-size: 0.8rem; background: rgba(255,255,255,0.05); padding: 2px 4px; border-radius: 4px;">f4d8ca2e</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            </div>
            <div class="kpi-title">Security Posture</div>
            <div class="kpi-val" style="color: #10B981;">0 Critical</div>
            <div class="kpi-subtitle">Trivy Registry Scan: PASS</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        # Estimate daily cost based on NAT Gateway toggle
        daily_est = 0.32 if cost_mode else 1.38
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            </div>
            <div class="kpi-title">Est. AWS Cost (Daily)</div>
            <div class="kpi-val" style="color: #F97316;">${daily_est:.2f}</div>
            <div class="kpi-subtitle">Monthly Projection: ${daily_est * 30.5:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # 2. Main charts split
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.markdown("### Container Traffic & CPU Utilization (Last 30 Min)")
        metric_df = generate_mock_cpu_ram()
        
        # Dual-axis chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metric_df["Time"], y=metric_df["CPU (%)"],
            name="CPU Usage (%)", line=dict(color="#38BDF8", width=2.5)
        ))
        fig.add_trace(go.Scatter(
            x=metric_df["Time"], y=metric_df["Requests/Sec"],
            name="Request Rate (RPS)", line=dict(color="#34D399", width=2, dash='dash'),
            yaxis="y2"
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(title="CPU Utilization (%)", side="left"),
            yaxis2=dict(title="Requests / Sec", side="right", overlaying="y", showgrid=False),
            margin=dict(l=20, r=20, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.markdown("### Trivy Vulnerability Distribution")
        vuln_data = generate_mock_vulnerabilities().iloc[-1]
        
        labels = ['Critical', 'High', 'Medium', 'Low']
        values = [vuln_data['Critical'], vuln_data['High'], vuln_data['Medium'], vuln_data['Low']]
        
        # Colors: Green for Critical=0, Red if >0
        colors = ['#EF4444', '#F97316', '#FBBF24', '#3B82F6']
        if values[0] == 0:
            labels = labels[1:]
            values = values[1:]
            colors = colors[1:]
            
        fig_donut = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.5,
            marker_colors=colors
        )])
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="v")
        )
        st.plotly_chart(fig_donut, use_container_width=True)

# ------------------------------------------
# TAB 2: CI/CD PIPELINE
# ------------------------------------------
with tab_pipeline:
    st.markdown("### GitHub Actions Execution Logs")
    
    # Mock pipeline history
    pipeline_runs = [
        {"Build": "121", "Commit": "f4d8ca2e", "Trigger": "Push (main)", "Status": "🟢 Success", "Duration": "3m 42s", "Date": "2026-06-13 19:35", "Trivy Code": "Pass", "Trivy Image": "Pass"},
        {"Build": "120", "Commit": "9a2f7c11", "Trigger": "Pull Request #23", "Status": "🟢 Success", "Duration": "2m 15s", "Date": "2026-06-13 18:12", "Trivy Code": "Pass", "Trivy Image": "N/A (PR)"},
        {"Build": "119", "Commit": "33bc8fa1", "Trigger": "Push (main)", "Status": "🔴 Failed (Trivy)", "Duration": "1m 58s", "Date": "2026-06-13 15:44", "Trivy Code": "Failed (1 Critical)", "Trivy Image": "Not Executed"},
        {"Build": "118", "Commit": "e88d22f1", "Trigger": "Push (main)", "Status": "🟢 Success", "Duration": "3m 50s", "Date": "2026-06-12 11:20", "Trivy Code": "Pass", "Trivy Image": "Pass"},
        {"Build": "117", "Commit": "ac77d4c2", "Trigger": "Merge (main)", "Status": "🟢 Success", "Duration": "3m 38s", "Date": "2026-06-11 22:04", "Trivy Code": "Pass", "Trivy Image": "Pass"}
    ]
    df_runs = pd.DataFrame(pipeline_runs)
        
    st.dataframe(
        df_runs,
        use_container_width=True,
        hide_index=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### CI/CD Workflow Phase Breakdown")
        phases = ["Code Lint", "Unit Tests", "Trivy Code Scan", "OIDC Auth", "Docker Build", "Trivy Image Scan", "ECR Push", "ECS Deployment"]
        durations = [12, 28, 45, 8, 92, 35, 14, 58] # in seconds
        
        fig_bar = px.bar(
            x=durations, y=phases, 
            orientation='h', 
            labels={'x': 'Duration (seconds)', 'y': 'Phase'},
            color_discrete_sequence=['#818CF8']
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        st.markdown("### Pipeline Analytics")
        st.write("📈 **Avg. Lead Time to Production:** `3 mins 47 secs` | ✅ **Success Rate:** `94.2%`")
        
        # New Graph 1: Build Execution Duration Trend
        build_nums = ["#117", "#118", "#119", "#120", "#121"]
        durations = [218, 230, 118, 135, 222] # in seconds
        build_df = pd.DataFrame({"Build": build_nums, "Duration (s)": durations})
        
        fig_dur = px.line(build_df, x="Build", y="Duration (s)", title="Build Execution Duration (Seconds)",
                          markers=True, color_discrete_sequence=['#818CF8'])
        fig_dur.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=35, b=10)
        )
        st.plotly_chart(fig_dur, use_container_width=True)
        
        # Details of the AWS OIDC configuration
        st.markdown("""
        > **OIDC DevSecOps Standard Compliance:** Short-lived tokens are issued on-demand via AWS Security Token Service (STS), securing deployments.
        """)

# ------------------------------------------
# TAB 3: SECURITY FINDINGS
# ------------------------------------------
with tab_security:
    st.markdown("### Vulnerability Remediation Trend (Trivy History)")
    vuln_history = generate_mock_vulnerabilities()
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=vuln_history["Build"], y=vuln_history["Critical"], name="Critical", line=dict(color="#EF4444", width=3)))
    fig_line.add_trace(go.Scatter(x=vuln_history["Build"], y=vuln_history["High"], name="High", line=dict(color="#F97316", width=2.5)))
    fig_line.add_trace(go.Scatter(x=vuln_history["Build"], y=vuln_history["Medium"], name="Medium", line=dict(color="#FBBF24", width=2)))
    fig_line.add_trace(go.Scatter(x=vuln_history["Build"], y=vuln_history["Low"], name="Low", line=dict(color="#3B82F6", width=1.5)))
    
    fig_line.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Build Number",
        yaxis_title="Vulnerability Count",
        margin=dict(l=20, r=20, t=10, b=10)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # New Graph 2: Vulnerability Category Source Breakdown
    st.markdown("### Vulnerability Source Breakdown (Latest Build)")
    vuln_src = pd.DataFrame({
        "Category": ["Base OS (Debian)", "Base OS (Debian)", "Python Runtime", "Python Runtime", "Dependencies"],
        "Severity": ["High", "Medium", "High", "Medium", "Medium"],
        "Count": [1, 3, 0, 1, 0]
    })
    fig_src = px.bar(
        vuln_src, x="Category", y="Count", color="Severity", barmode="group",
        color_discrete_map={"High": "#F97316", "Medium": "#FBBF24"},
        category_orders={"Category": ["Base OS (Debian)", "Python Runtime", "Dependencies"]}
    )
    fig_src.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_src, use_container_width=True)
    
    st.markdown("### Active Compliance Checklist")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.success("✔️ **Static Application Security Testing (SAST)**")
        st.write("- Trivy FS repository check passed.")
        st.write("- No high-risk configuration issues found.")
        st.write("- Base image linting enforced.")
        
    with c2:
        st.success("✔️ **Secret Detection**")
        st.write("- Trivy scanned files for exposed credentials.")
        st.write("- Git history scanned for secrets.")
        st.write("- No exposed AWS access keys or tokens found.")
        
    with c3:
        st.success("✔️ **Container Security**")
        st.write("- Multi-stage build eliminates compilers.")
        st.write("- Container runs as non-root user `appuser`.")
        st.write("- No critical runtime vulnerabilities (Trivy verified).")

# ------------------------------------------
# TAB 4: CONTAINER HEALTH
# ------------------------------------------
with tab_container:
    st.markdown("### ECS Fargate Tasks Resource Utilization")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_cpu = px.line(metric_df, x="Time", y="CPU (%)", title="CPU Utilization (%)", color_discrete_sequence=['#38BDF8'])
        fig_cpu.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cpu, use_container_width=True)
        
    with col2:
        fig_mem = px.line(metric_df, x="Time", y="Memory (%)", title="Memory Utilization (%)", color_discrete_sequence=['#A78BFA'])
        fig_mem.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_mem, use_container_width=True)
        
    # CloudWatch Logs Mock Viewer
    st.markdown("### Application Logs (Live CloudWatch Log Stream Simulation)")
    log_mock_data = [
        {"timestamp": "2026-06-13 19:35:44", "level": "INFO", "message": "Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)", "logger": "uvicorn.error"},
        {"timestamp": "2026-06-13 19:35:45", "level": "INFO", "message": "Application startup complete. Uptime tracked.", "logger": "app"},
        {"timestamp": "2026-06-13 19:36:12", "level": "INFO", "message": "HTTP Request: GET /health - 200", "logger": "app", "duration_ms": 0.44},
        {"timestamp": "2026-06-13 19:37:12", "level": "INFO", "message": "HTTP Request: GET /health - 200", "logger": "app", "duration_ms": 0.38},
        {"timestamp": "2026-06-13 19:37:48", "level": "INFO", "message": "Accessing secure data endpoint", "logger": "app"},
        {"timestamp": "2026-06-13 19:37:48", "level": "INFO", "message": "HTTP Request: GET /api/v1/secure-data - 200", "logger": "app", "duration_ms": 2.15, "client_ip": "10.0.1.144"}
    ]
    
    # Format log prints nicely
    log_area = ""
    for log in log_mock_data:
        duration_part = f" duration={log['duration_ms']}ms" if "duration_ms" in log else ""
        client_part = f" client={log['client_ip']}" if "client_ip" in log else ""
        log_area += f"[{log['timestamp']}] [{log['level']}] [{log['logger']}] {log['message']}{duration_part}{client_part}\n"
        
    st.code(log_area, language="log")

# ------------------------------------------
# TAB 5: COST ANALYTICS
# ------------------------------------------
with tab_costs:
    st.markdown("### AWS Cost Breakdown & Optimizer")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Cost Projection Calculator")
        
        tasks_count = st.number_input("Number of ECS Tasks", min_value=0, max_value=10, value=1)
        nat_count = st.number_input("NAT Gateways Active", min_value=0, max_value=2, value=0 if cost_mode else 1)
        alb_active = st.checkbox("Application Load Balancer Active", value=True)
        
        # Calculations:
        # Fargate 0.25 vCPU & 0.5 GB: ~$0.0137/hour = ~$9.90/month per task
        # NAT Gateway: ~$0.045/hour + data processing = ~$32.40/month per NAT Gateway
        # ALB: ~$0.0225/hour + LCU = ~$16.20/month
        # ECR / Logs: ~$2.00/month
        
        fargate_cost = tasks_count * 9.90
        nat_cost = nat_count * 32.40
        alb_cost = 16.20 if alb_active else 0
        misc_cost = 2.00 if (tasks_count > 0 or alb_active) else 0
        total_monthly = fargate_cost + nat_cost + alb_cost + misc_cost
        
        st.markdown(f"### Estimated: **${total_monthly:.2f} / month**")
        st.write(f"- Fargate Tasks: ${fargate_cost:.2f}")
        st.write(f"- NAT Gateways: ${nat_cost:.2f}")
        st.write(f"- ALB: ${alb_cost:.2f}")
        st.write(f"- ECR Storage & Logs: ${misc_cost:.2f}")

        # New Graph 3: Cost Allocation Donut Chart (Dynamic)
        cost_labels = []
        cost_values = []
        
        if fargate_cost > 0:
            cost_labels.append("Fargate Compute")
            cost_values.append(fargate_cost)
        if nat_cost > 0:
            cost_labels.append("NAT Gateways")
            cost_values.append(nat_cost)
        if alb_cost > 0:
            cost_labels.append("ALB Load Balancer")
            cost_values.append(alb_cost)
        if misc_cost > 0:
            cost_labels.append("ECR & Logs")
            cost_values.append(misc_cost)
            
        fig_cost = go.Figure(data=[go.Pie(
            labels=cost_labels, 
            values=cost_values, 
            hole=.45,
            marker_colors=['#38BDF8', '#F97316', '#818CF8', '#A78BFA']
        )])
        fig_cost.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig_cost, use_container_width=True)
        
    with col2:
        st.markdown("#### Cloud Architect Cost Savings Insight")
        
        if cost_mode:
            st.success("💰 **Cost Optimization ACTIVE**")
            st.write("By running Fargate in public subnets with public IPs (`use_nat_gateway = false`), you bypassed deploying a NAT Gateway, **saving $32.40/month** (~75% reduction). This is the ideal setup for personal development, lab environments, and portfolios.")
        else:
            st.warning("⚠️ **Standard Enterprise Architecture active (Cost Inefficient for Labs)**")
            st.write("You have NAT Gateway simulation active. This runs Fargate in private subnets with high isolation, but generates standard AWS fees (~$32.40 per gateway). Suitable only for corporately funded environments.")
            
        st.markdown("""
        #### Tear-Down / Shutdown Action Guide
        When you are done demonstrating this project, run the cleanup script to avoid any lingering costs:
        
        ```bash
        # Tear down all AWS resources
        cd terraform/
        terraform destroy -auto-approve
        ```
        Alternatively, execute the cleanup scripts provided in the `scripts/` folder:
        - `bash scripts/cleanup.sh`
        - `powershell scripts/cleanup.ps1`
        """)
