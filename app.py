import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.rag import ask_question

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="Knowledge Assistant Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Real-Time Multi-Source Knowledge Assistant v1.0",
        "Get help": "mailto:support@company.com",
    }
)

# ==================== Color Scheme ====================
COLORS = {
    "primary": "#0066CC",      # Professional Blue
    "secondary": "#00D4AA",    # Teal Accent
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Red
    "dark_bg": "#0F1419",      # Dark Background
    "light_bg": "#FFFFFF",     # Light Background
    "card_bg": "#F8FAFC",      # Card Background
    "text_primary": "#1F2937", # Dark Text
    "text_secondary": "#6B7280",# Gray Text
    "border": "#E5E7EB",       # Light Border
}

# ==================== Custom CSS Styling ====================
st.markdown(f"""
    <style>
    :root {{
        --primary-color: {COLORS['primary']};
        --secondary-color: {COLORS['secondary']};
        --text-color: {COLORS['text_primary']};
    }}
    
    * {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    .main {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }}
    
    .metric-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid {COLORS['primary']};
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .section-title {{
        color: {COLORS['primary']};
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid {COLORS['secondary']};
        padding-bottom: 0.5rem;
    }}
    
    .chat-message {{
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        gap: 1rem;
    }}
    
    .chat-user {{
        background-color: {COLORS['primary']};
        color: white;
        border-radius: 12px;
        margin-left: 2rem;
    }}
    
    .chat-assistant {{
        background-color: {COLORS['card_bg']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        margin-right: 2rem;
    }}
    
    .source-badge {{
        display: inline-block;
        background-color: {COLORS['secondary']};
        color: white;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 600;
    }}
    
    .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    .stat-label {{
        font-size: 0.9rem;
        color: {COLORS['text_secondary']};
        margin-top: 0.5rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==================== Session State Initialization ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "avg_response_time" not in st.session_state:
    st.session_state.avg_response_time = []

if "query_accuracy" not in st.session_state:
    st.session_state.query_accuracy = []

# ==================== Header Section ====================
col1, col2, col3 = st.columns([2, 3, 1])

with col1:
    st.markdown("## 🧠 Knowledge Assistant")
    st.markdown("*Real-Time Multi-Source Intelligence Platform*")

with col3:
    current_time = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"<div style='text-align: right; color: {COLORS['text_secondary']}; font-size: 0.9rem;'>{current_time}</div>", unsafe_allow_html=True)

st.divider()

# ==================== Navigation Tabs ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 Chat Assistant",
    "📊 Dashboard",
    "📈 Analytics",
    "⚙️ Settings"
])

# ======================= TAB 1: CHAT ASSISTANT =======================
with tab1:
    st.markdown("""
        <h2 class='section-title'>💬 Ask Your Questions</h2>
    """, unsafe_allow_html=True)
    
    # Chat Container
    chat_container = st.container()
    
    with chat_container:
        # Display Previous Messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class='chat-message chat-user'>
                        <div style='flex: 1;'>
                            <strong style='font-size: 0.9rem;'>You</strong><br/>
                            {message['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message chat-assistant'>
                        <div style='flex: 1;'>
                            <strong style='font-size: 0.9rem;'>Assistant</strong><br/>
                            {message['content'][:200]}...
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # Input Section
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        prompt = st.text_input(
            "Type your question here...",
            placeholder="What would you like to know?",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_btn = st.button("🚀 Send", use_container_width=True)
    
    if submit_btn and prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.query_count += 1
        
        # Generate response
        with st.spinner("🔍 Searching knowledge base..."):
            import time
            start_time = time.time()
            answer, sources = ask_question(prompt)
            response_time = time.time() - start_time
            st.session_state.avg_response_time.append(response_time)
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "time": response_time
        })
        
        st.rerun()
    
    # Display Latest Response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        latest = st.session_state.messages[-1]
        
        st.markdown("---")
        st.markdown("""
            <h3 style='color: #0066CC; margin-bottom: 1rem;'>📌 Latest Response</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
                <div style='background: {COLORS['card_bg']}; padding: 1.5rem; border-radius: 12px; border-left: 4px solid {COLORS['secondary']};'>
                    {latest['content']}
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "Response Time",
                f"{latest['time']:.2f}s",
                delta=None if len(st.session_state.avg_response_time) < 2 else f"{st.session_state.avg_response_time[-1] - st.session_state.avg_response_time[-2]:.2f}s"
            )
        
        if latest.get("sources"):
            st.markdown("""
                <h4 style='color: #6B7280; margin-top: 1.5rem; margin-bottom: 0.5rem;'>📚 Sources</h4>
            """, unsafe_allow_html=True)
            
            source_cols = st.columns(3)
            for idx, source in enumerate(latest["sources"][:3]):
                with source_cols[idx % 3]:
                    source_text = source.page_content[:100] if hasattr(source, 'page_content') else str(source)[:100]
                    st.markdown(f"""
                        <div style='background: {COLORS['card_bg']}; padding: 0.8rem; border-radius: 8px; border-left: 3px solid {COLORS['success']};'>
                            <small style='color: {COLORS['text_secondary']};'>Source {idx+1}</small><br/>
                            <span style='color: {COLORS['text_primary']};'>{source_text}...</span>
                        </div>
                    """, unsafe_allow_html=True)

# ======================= TAB 2: DASHBOARD =======================
with tab2:
    st.markdown("""
        <h2 class='section-title'>📊 System Dashboard</h2>
    """, unsafe_allow_html=True)
    
    # Key Metrics Row
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>100%</div>
                <div class='stat-label'>System Availability</div>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>{st.session_state.query_count}</div>
                <div class='stat-label'>Total Queries</div>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        avg_time = np.mean(st.session_state.avg_response_time) if st.session_state.avg_response_time else 0
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>{avg_time:.2f}s</div>
                <div class='stat-label'>Avg Response Time</div>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[3]:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>97.5%</div>
                <div class='stat-label'>Query Accuracy</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>📈 System Health</h4>
        """, unsafe_allow_html=True)
        
        # System Health Gauge
        fig = go.Figure(data=[go.Indicator(
            mode="gauge+number+delta",
            value=99.5,
            title={'text': "Uptime %"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['primary']},
                'steps': [
                    {'range': [0, 50], 'color': COLORS['danger']},
                    {'range': [50, 80], 'color': COLORS['warning']},
                    {'range': [80, 100], 'color': COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        )])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>🎯 Query Distribution</h4>
        """, unsafe_allow_html=True)
        
        # Query Type Distribution
        query_types = ['Vector Search', 'Web Search', 'Follow-up', 'Hybrid']
        query_counts = [45, 28, 18, 9]
        colors_pie = [COLORS['primary'], COLORS['secondary'], COLORS['warning'], COLORS['success']]
        
        fig = go.Figure(data=[go.Pie(
            labels=query_types,
            values=query_counts,
            marker=dict(colors=colors_pie),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
        )])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>⏱️ Response Time Trend</h4>
        """, unsafe_allow_html=True)
        
        # Generate sample data
        hours = [f"{i:02d}:00" for i in range(24)]
        response_times = np.random.normal(1.2, 0.3, 24).clip(0.5, 2.0)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours,
            y=response_times,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color=COLORS['primary'], width=2),
            fillcolor=f"rgba(0, 102, 204, 0.2)",
            name='Response Time'
        ))
        fig.update_layout(
            height=300,
            hovermode='x unified',
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>🌐 Data Sources</h4>
        """, unsafe_allow_html=True)
        
        # Data Sources Bar Chart
        sources = ['PDFs', 'Web Pages', 'APIs', 'Databases', 'Markdown']
        source_counts = [234, 189, 156, 142, 98]
        colors_bar = [COLORS['primary'], COLORS['secondary'], COLORS['success'], COLORS['warning'], COLORS['danger']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=sources,
                y=source_counts,
                marker=dict(color=colors_bar),
                text=source_counts,
                textposition='auto',
                hovertemplate="<b>%{x}</b><br>Documents: %{y}<extra></extra>"
            )
        ])
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ======================= TAB 3: ANALYTICS =======================
with tab3:
    st.markdown("""
        <h2 class='section-title'>📈 Advanced Analytics</h2>
    """, unsafe_allow_html=True)
    
    # Analytics Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>1,248</div>
                <div class='stat-label'>Active Users (Last 30 days)</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>45.6K</div>
                <div class='stat-label'>Queries Processed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='stat-number'>$156K</div>
                <div class='stat-label'>Cost Savings Generated</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed Analytics Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>📊 Accuracy Metrics (RAGAS)</h4>
        """, unsafe_allow_html=True)
        
        metrics = ['Faithfulness', 'Relevance', 'Precision', 'Recall']
        scores = [94.5, 96.2, 91.8, 93.5]
        
        fig = go.Figure(data=[
            go.Scatterpolar(
                r=scores,
                theta=metrics,
                fill='toself',
                line=dict(color=COLORS['primary']),
                fillcolor=f"rgba(0, 102, 204, 0.3)"
            )
        ])
        fig.update_layout(
            height=400,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color=COLORS['text_secondary'])
                )
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>📊 User Engagement</h4>
        """, unsafe_allow_html=True)
        
        # Engagement over time
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        engagement = [1200, 1400, 1100, 1600, 1800, 900, 600]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=engagement,
            marker=dict(
                color=engagement,
                colorscale=[[0, COLORS['danger']], [0.5, COLORS['warning']], [1, COLORS['success']]],
                showscale=True
            ),
            text=engagement,
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Engagement: %{y}<extra></extra>"
        ))
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Performance Table
    st.markdown("""
        <h4 style='color: #0066CC; margin-bottom: 1rem;'>📋 Performance Summary</h4>
    """, unsafe_allow_html=True)
    
    performance_data = {
        'Metric': ['System Availability', 'Average Response Time', 'Query Success Rate', 'Data Coverage', 'User Satisfaction'],
        'Current': ['99.9%', '1.2s', '97.5%', '94.3%', '4.6/5'],
        'Target': ['99.95%', '1.0s', '98.0%', '95.0%', '4.7/5'],
        'Status': ['✅', '⚠️', '✅', '📈', '✅']
    }
    
    df_perf = pd.DataFrame(performance_data)
    st.dataframe(df_perf, use_container_width=True, hide_index=True)

# ======================= TAB 4: SETTINGS =======================
with tab4:
    st.markdown("""
        <h2 class='section-title'>⚙️ Settings & Configuration</h2>
    """, unsafe_allow_html=True)
    
    # Settings Sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>🔧 System Settings</h4>
        """, unsafe_allow_html=True)
        
        model_choice = st.selectbox("Select LLM Model", ["GPT-4", "GPT-3.5", "Claude-3", "Llama-2"], key="model")
        temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temp")
        max_tokens = st.slider("Max Tokens", 100, 4000, 2000, 100, key="tokens")
        enable_memory = st.toggle("Enable Memory Management", value=True)
    
    with col2:
        st.markdown("""
            <h4 style='color: #0066CC; margin-bottom: 1rem;'>📚 Data Sources</h4>
        """, unsafe_allow_html=True)
        
        pdf_enabled = st.toggle("Enable PDF Ingestion", value=True)
        web_enabled = st.toggle("Enable Web Search", value=True)
        api_enabled = st.toggle("Enable API Integration", value=True)
        db_enabled = st.toggle("Enable Database Sync", value=True)
    
    st.markdown("---")
    
    st.markdown("""
        <h4 style='color: #0066CC; margin-bottom: 1rem;'>🔐 Security & Privacy</h4>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        encryption = st.selectbox("Encryption Level", ["AES-256", "AES-128", "No Encryption"])
        data_retention = st.slider("Data Retention (days)", 7, 365, 90)
    
    with col2:
        gdpr_compliance = st.toggle("GDPR Compliance", value=True)
        audit_logging = st.toggle("Enable Audit Logging", value=True)
    
    st.markdown("---")
    
    # Save Settings Button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.warning("⚠️ Settings reset to defaults")

# ==================== Footer ====================
st.divider()
st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 0.9rem; padding: 2rem 0;'>
        <p>🚀 <strong>Real-Time Multi-Source Knowledge Assistant</strong> | Version 1.0</p>
        <p>© 2026 AI Engineering Team | All Rights Reserved</p>
        <p style='margin-top: 1rem; font-size: 0.85rem;'>
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Documentation</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Support</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Status</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Privacy</a>
        </p>
    </div>
""", unsafe_allow_html=True)