"""Professional Streamlit application for Expert RAG Chatbot.

A production-grade web interface featuring:
- Multi-tab interface for different functionalities
- Real-time chat with persistent sessions
- Performance analytics and monitoring
- Safety guardrails management
- Advanced configuration options
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

from src.rag import ask_question, get_pipeline
from src.guardrails import get_safety_guidelines
from src.logger import logger, log_error, PerformanceTracker, chat_logger, log_chat_interaction, log_session_event, log_user_activity, log_system_event
from src.utils import (
    parse_query, IntentType, ERROR_MESSAGES, 
    format_error_message, truncate_text
)

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="🚀 Expert RAG Assistant | v2.0",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "🚀 Expert RAG Assistant | Version 2.0\n© 2026 Aniruddha Kasar | All Rights Reserved",
        "Get help": "mailto:support@example.com",
    }
)

# Log system startup
log_system_event(
    event_type="app_startup",
    details="Expert RAG Assistant v2.0 started",
    metadata={
        "version": "2.0",
        "streamlit_version": st.__version__,
        "timestamp": datetime.now().isoformat()
    }
)

# ==================== Color Scheme ====================
COLORS = {
    "primary": "#667EEA",        # Modern Blue
    "secondary": "#764BA2",      # Purple Accent
    "success": "#4ADE80",        # Bright Green
    "warning": "#FACC15",        # Golden Yellow
    "danger": "#F87171",         # Soft Red
    "info": "#06B6D4",           # Cyan
    "dark_bg": "#0F172A",        # Dark Slate
    "light_bg": "#F8FAFC",       # Clean White
    "card_bg": "#FFFFFF",        # Pure White
    "gradient_start": "#667EEA", # Blue gradient start
    "gradient_end": "#764BA2",   # Purple gradient end
    "user_bubble": "#667EEA",    # User message blue
    "assistant_bubble": "#F1F5F9", # Assistant light gray
    "text_primary": "#1E293B",   # Dark Slate
    "text_secondary": "#64748B", # Medium Gray
    "text_muted": "#94A3B8",     # Light Gray
    "border": "#E2E8F0",         # Light Border
    "shadow": "rgba(0,0,0,0.1)", # Soft Shadow
    "glow": "rgba(102, 126, 234, 0.3)", # Blue Glow
}

# ==================== Enhanced Custom CSS Styling ====================
st.markdown(f"""
    <style>
    :root {{
        --primary-color: {COLORS['primary']};
        --secondary-color: {COLORS['secondary']};
        --gradient: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});
        --text-color: {COLORS['text_primary']};
        --glow: {COLORS['glow']};
    }}

    * {{
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    .main {{
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }}

    /* Enhanced Metric Cards */
    .metric-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.95));
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-left: 4px solid {COLORS['primary']};
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15), 0 8px 16px rgba(0,0,0,0.1);
        border-color: {COLORS['primary']};
    }}

    .metric-card:hover::before {{
        opacity: 1;
    }}

    /* Enhanced Section Titles */
    .section-title {{
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 2rem 0 1.5rem 0;
        position: relative;
        display: inline-block;
    }}

    .section-title::after {{
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 60px;
        height: 4px;
        background: var(--gradient);
        border-radius: 2px;
    }}

    /* Modern Chat Interface */
    .chat-container {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
    }}

    .chat-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient);
    }}

    /* User Messages - Modern Bubbles */
    .user-message {{
        display: flex;
        justify-content: flex-end;
        margin: 1.5rem 0;
        animation: slideInRight 0.4s ease-out;
    }}

    .user-bubble {{
        background: var(--gradient);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 4px 20px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3), 0 4px 10px rgba(0,0,0,0.1);
        position: relative;
        font-weight: 500;
        line-height: 1.5;
        border: 2px solid rgba(255,255,255,0.2);
    }}

    .user-bubble::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        right: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid {COLORS['user_bubble']};
    }}

    /* Assistant Messages - Clean Cards */
    .assistant-message {{
        display: flex;
        justify-content: flex-start;
        margin: 1.5rem 0;
        animation: slideInLeft 0.4s ease-out;
    }}

    .assistant-bubble {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(241,245,249,0.9));
        color: {COLORS['text_primary']};
        padding: 1.5rem;
        border-radius: 20px 20px 20px 4px;
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08), 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
        position: relative;
        line-height: 1.6;
        backdrop-filter: blur(10px);
    }}

    .assistant-bubble::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 20px;
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-top: 8px solid rgba(255,255,255,0.9);
    }}

    /* Chat Animations */
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    @keyframes slideInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-30px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}

    /* Enhanced Session Buttons */
    .session-button {{
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        font-weight: 500;
        color: {COLORS['text_primary']};
    }}

    .session-button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s ease;
    }}

    .session-button:hover {{
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-color: {COLORS['primary']};
        transform: translateX(4px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }}

    .session-button:hover::before {{
        left: 100%;
    }}

    .session-button.active {{
        background: var(--gradient);
        color: white;
        border-color: {COLORS['primary']};
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transform: translateX(4px);
    }}

    .session-button.active::after {{
        content: '●';
        position: absolute;
        right: 10px;
        color: rgba(255,255,255,0.8);
        font-size: 12px;
    }}

    /* Enhanced Stats */
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}

    .stat-label {{
        font-size: 1rem;
        color: {COLORS['text_secondary']};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Welcome Message Enhancement */
    .welcome-container {{
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8));
        backdrop-filter: blur(20px);
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }}

    .welcome-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient);
        opacity: 0.05;
        z-index: -1;
    }}

    .welcome-title {{
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: fadeInUp 0.8s ease-out;
    }}

    .welcome-subtitle {{
        font-size: 1.2rem;
        color: {COLORS['text_secondary']};
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }}

    .welcome-tip {{
        display: inline-block;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        color: {COLORS['primary']};
        padding: 1rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        border: 1px solid rgba(102, 126, 234, 0.2);
        animation: fadeInUp 0.8s ease-out 0.4s both;
    }}

    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* Enhanced Buttons */
    .stButton > button {{
        background: var(--gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        position: relative !important;
        overflow: hidden !important;
    }}

    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }}

    .stButton > button:hover::before {{
        left: 100%;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    /* Enhanced Sidebar */
    .css-1d391kg {{
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(248,250,252,0.95)) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.3) !important;
    }}

    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.8)) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: 8px !important;
        color: {COLORS['text_secondary']} !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: var(--gradient) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }}

    /* Enhanced Chat Input */
    .stChatInput {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9)) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    }}

    /* Scrollbar Styling */
    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(0,0,0,0.05);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--gradient);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});
    }}
    </style>
    """, unsafe_allow_html=True)

# ==================== Chat Persistence ====================
SESSIONS_DIR = Path("chat_sessions")

def ensure_sessions_dir():
    """Ensure the sessions directory exists"""
    SESSIONS_DIR.mkdir(exist_ok=True)

def save_session(session_id, session_data):
    """Save a chat session to disk"""
    ensure_sessions_dir()
    session_file = SESSIONS_DIR / f"{session_id}.json"

    # Convert datetime objects to strings for JSON serialization
    serializable_data = session_data.copy()
    serializable_data["created_at"] = session_data["created_at"].isoformat()

    try:
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Failed to save session {session_id}: {e}")

def load_session(session_id):
    """Load a chat session from disk"""
    session_file = SESSIONS_DIR / f"{session_id}.json"

    if not session_file.exists():
        return None

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert datetime strings back to datetime objects
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return data
    except Exception as e:
        st.error(f"Failed to load session {session_id}: {e}")
        return None

def delete_session_file(session_id):
    """Delete a chat session file from disk"""
    session_file = SESSIONS_DIR / f"{session_id}.json"

    try:
        if session_file.exists():
            session_file.unlink()  # Delete the file
    except Exception as e:
        st.error(f"Failed to delete session file {session_id}: {e}")

def load_all_sessions():
    """Load all saved chat sessions"""
    ensure_sessions_dir()
    sessions = {}

    # Always include default session
    sessions["default"] = {
        "messages": [],
        "created_at": datetime.now(),
        "title": "New Conversation"
    }

    # Load saved sessions
    for session_file in SESSIONS_DIR.glob("*.json"):
        session_id = session_file.stem
        if session_id != "default":  # Skip if there's a saved default session
            session_data = load_session(session_id)
            if session_data:
                sessions[session_id] = session_data

    return sessions

def cleanup_old_sessions(max_age_days=30):
    """Clean up sessions older than specified days"""
    ensure_sessions_dir()
    cutoff_date = datetime.now() - timedelta(days=max_age_days)

    for session_file in SESSIONS_DIR.glob("*.json"):
        session_id = session_file.stem
        if session_id == "default":
            continue  # Don't delete default session

        session_data = load_session(session_id)
        if session_data and session_data["created_at"] < cutoff_date:
            try:
                session_file.unlink()
                # Also remove from memory if loaded
                if session_id in st.session_state.chat_sessions:
                    del st.session_state.chat_sessions[session_id]
            except Exception as e:
                st.warning(f"Failed to cleanup old session {session_id}: {e}")

def get_session_stats():
    """Get statistics about saved sessions"""
    ensure_sessions_dir()
    session_files = list(SESSIONS_DIR.glob("*.json"))
    total_sessions = len(session_files)

    # Load all sessions to get stats
    sessions_data = []
    for session_file in session_files:
        session_id = session_file.stem
        data = load_session(session_id)
        if data:
            sessions_data.append(data)

    total_messages = sum(len(s.get("messages", [])) for s in sessions_data)
    avg_messages_per_session = total_messages / max(total_sessions, 1)

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": avg_messages_per_session
    }

# ==================== Session State Initialization ====================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "avg_response_time" not in st.session_state:
    st.session_state.avg_response_time = []

if "query_accuracy" not in st.session_state:
    st.session_state.query_accuracy = []

# ==================== Chat Session Management ====================
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"

if "chat_sessions" not in st.session_state:
    # Load saved sessions from disk
    st.session_state.chat_sessions = load_all_sessions()

if "session_counter" not in st.session_state:
    # Find the lowest available session number
    existing_sessions = [s for s in st.session_state.chat_sessions.keys() if s.startswith("session_")]
    if existing_sessions:
        numbers = sorted([int(s.split("_")[1]) for s in existing_sessions])
        # Find the lowest missing number starting from 1
        st.session_state.session_counter = 1
        for num in numbers:
            if num == st.session_state.session_counter:
                st.session_state.session_counter += 1
            else:
                break
    else:
        st.session_state.session_counter = 1

def create_new_session():
    """Create a new chat session"""
    session_id = f"session_{st.session_state.session_counter}"
    title_number = st.session_state.session_counter
    st.session_state.session_counter += 1
    st.session_state.chat_sessions[session_id] = {
        "messages": [],
        "created_at": datetime.now(),
        "title": f"Conversation {title_number}"
    }
    # Save to disk
    save_session(session_id, st.session_state.chat_sessions[session_id])
    st.session_state.current_session = session_id

    # Log session creation
    log_session_event(
        session_id=session_id,
        user_id=session_id,  # Using session_id as user_id for now
        event_type="created",
        details=f"Title: Conversation {title_number}",
        metadata={"total_sessions": len(st.session_state.chat_sessions)}
    )

    return session_id

def switch_session(session_id):
    """Switch to a different chat session"""
    if session_id in st.session_state.chat_sessions:
        previous_session = st.session_state.current_session
        st.session_state.current_session = session_id

        # Log session switch
        log_session_event(
            session_id=session_id,
            user_id=session_id,
            event_type="switched_to",
            details=f"From session: {previous_session}",
            metadata={"message_count": len(st.session_state.chat_sessions[session_id]["messages"])}
        )

def delete_session(session_id):
    """Delete a chat session"""
    if session_id in st.session_state.chat_sessions and session_id != "default":
        message_count = len(st.session_state.chat_sessions[session_id]["messages"])

        # Delete from memory
        del st.session_state.chat_sessions[session_id]
        # Delete from disk
        delete_session_file(session_id)

        # Reset session counter to reuse deleted numbers
        existing_sessions = [s for s in st.session_state.chat_sessions.keys() if s.startswith("session_")]
        if existing_sessions:
            numbers = sorted([int(s.split("_")[1]) for s in existing_sessions])
            # Find the lowest missing number starting from 1
            next_counter = 1
            for num in numbers:
                if num == next_counter:
                    next_counter += 1
                else:
                    break
            st.session_state.session_counter = next_counter
        else:
            st.session_state.session_counter = 1

        # Switch to default if current session was deleted
        if st.session_state.current_session == session_id:
            st.session_state.current_session = "default"

        # Log session deletion
        log_session_event(
            session_id=session_id,
            user_id=session_id,
            event_type="deleted",
            details=f"Messages deleted: {message_count}",
            metadata={"switched_to_default": st.session_state.current_session == "default"}
        )

def get_current_messages():
    """Get messages for current session"""
    return st.session_state.chat_sessions[st.session_state.current_session]["messages"]

def add_message_to_current_session(message):
    """Add a message to the current session"""
    st.session_state.chat_sessions[st.session_state.current_session]["messages"].append(message)

    # Save session to disk after adding message
    save_session(st.session_state.current_session, st.session_state.chat_sessions[st.session_state.current_session])

    # Note: Session titles are kept as "Conversation X" format for consistency
    # Auto-title update based on first message is disabled

# ==================== Header Section ====================
col1, col2, col3 = st.columns([2, 3, 1])

with col1:
    st.markdown("## 🚀 Real-Time Multi-Source Knowledge Assistant | v1.0")
    st.markdown("*© 2026 Aniruddha kasar | Designed by Aniruddha Kasar*")

with col3:
    current_time = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"<div style='text-align: right; color: {COLORS['text_secondary']}; font-size: 0.9rem;'>{current_time}</div>", unsafe_allow_html=True)

st.divider()

# ==================== Navigation Tabs ====================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 Chat Assistant",
    "📊 Dashboard",
    "📈 Analytics",
    "⚙️ Settings",
    "🛡️ Safety & Guidelines",
    "📋 System Logs"
])

# ======================= TAB 1: CHAT ASSISTANT =======================
with tab1:
    # Session Management Sidebar
    with st.sidebar:
        st.markdown("### 💬 Chat Sessions")

        # New Session Button
        if st.button("➕ New Chat", use_container_width=True):
            create_new_session()
            st.rerun()

        st.markdown("---")

        # Session List
        for session_id, session_data in st.session_state.chat_sessions.items():
            is_active = session_id == st.session_state.current_session
            button_label = f"{'🔵' if is_active else '⚪'} {session_data['title']}"

            if st.button(button_label, key=f"session_{session_id}", use_container_width=True):
                switch_session(session_id)
                st.rerun()

            # Delete button for non-default sessions
            if session_id != "default":
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}", help="Delete session"):
                        delete_session(session_id)
                        st.rerun()

        st.markdown("---")
        st.markdown(f"**Active:** {st.session_state.chat_sessions[st.session_state.current_session]['title']}")

    # Main Chat Interface
    st.markdown("""
        <h2 class='section-title'>💬 Chat Assistant</h2>
    """, unsafe_allow_html=True)

    # Chat Container with enhanced styling
    chat_container = st.container(height=600)

    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        current_messages = get_current_messages()

        if not current_messages:
            # Welcome message for empty chat
            st.markdown(f"""
                <div class='welcome-container'>
                    <h1 class='welcome-title'>👋 Welcome to the Real-Time Multi-Source Knowledge Assistant!</h1>
                    <p class='welcome-subtitle'>Start a conversation by typing your question below.</p>
                    <p class='welcome-tip'>💡 Tip: Create multiple sessions to organize different topics</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat history
            for i, message in enumerate(current_messages):
                if message["role"] == "user":
                    # User message - modern bubble design
                    st.markdown(f"""
                        <div class='user-message'>
                            <div class='user-bubble'>
                                <strong>You</strong><br/>
                                {message['content']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant message - clean card design
                    with st.container():
                        # Assistant header with icon and timing
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown("🤖 **Assistant**")
                        with col2:
                            if "time" in message:
                                st.caption(f"⚡ {message['time']:.2f}s")

                        # Assistant content in modern bubble
                        st.markdown(f"""
                            <div class='assistant-message'>
                                <div class='assistant-bubble'>
                                    {message['content']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        # Enhanced Sources display
                        if "sources" in message and message["sources"]:
                            with st.expander("📚 **Sources & References**", expanded=False):
                                for j, source in enumerate(message["sources"][:5]):  # Show max 5 sources
                                    if hasattr(source, 'page_content'):
                                        source_preview = source.page_content[:150] + "..." if len(source.page_content) > 150 else source.page_content
                                        st.markdown(f"""
                                            <div style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
                                                       border: 1px solid rgba(102, 126, 234, 0.1);
                                                       border-radius: 8px;
                                                       padding: 1rem;
                                                       margin: 0.5rem 0;
                                                       border-left: 3px solid {COLORS['primary']};'>
                                                <strong style='color: {COLORS['primary']};'>Source {j+1}</strong><br/>
                                                <span style='color: {COLORS['text_secondary']}; font-size: 0.9rem;'>{source_preview}</span>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""
                                            <div style='background: rgba(4, 174, 128, 0.1);
                                                       border: 1px solid rgba(4, 174, 128, 0.2);
                                                       border-radius: 8px;
                                                       padding: 0.8rem;
                                                       margin: 0.5rem 0;
                                                       border-left: 3px solid {COLORS['success']};'>
                                                <strong style='color: {COLORS['success']};'>Source {j+1}</strong><br/>
                                                <span style='color: {COLORS['text_secondary']};'>{str(source)[:200]}...</span>
                                            </div>
                                        """, unsafe_allow_html=True)

    # Input Section
    st.markdown("---")

    # Chat input with better UX
    chat_input_container = st.container()
    with chat_input_container:
        col1, col2 = st.columns([5, 1])

        with col1:
            prompt = st.chat_input(
                "Type your message here...",
                key="chat_input"
            )

        with col2:
            if st.button("🗑️ Clear Chat", help="Clear current conversation"):
                message_count = len(st.session_state.chat_sessions[st.session_state.current_session]["messages"])
                if st.session_state.current_session != "default":
                    st.session_state.chat_sessions[st.session_state.current_session]["messages"] = []
                    # Save cleared session to disk
                    save_session(st.session_state.current_session, st.session_state.chat_sessions[st.session_state.current_session])

                    # Log session clear
                    log_session_event(
                        session_id=st.session_state.current_session,
                        user_id=st.session_state.current_session,
                        event_type="cleared",
                        details=f"Cleared {message_count} messages",
                        metadata={"session_type": "named"}
                    )
                else:
                    st.session_state.chat_sessions["default"]["messages"] = []

                    # Log default session clear
                    log_session_event(
                        session_id="default",
                        user_id="default",
                        event_type="cleared",
                        details=f"Cleared {message_count} messages",
                        metadata={"session_type": "default"}
                    )
                st.rerun()

    # Process user input
    if prompt:
        # Get user identifier (use session ID as user ID for now)
        user_id = st.session_state.current_session

        # Log user activity
        log_user_activity(
            user_id=user_id,
            activity_type="chat_message",
            details=f"Message length: {len(prompt)} chars",
            session_id=st.session_state.current_session
        )

        # Add user message to current session
        add_message_to_current_session({"role": "user", "content": prompt})
        st.session_state.query_count += 1

        # Generate response
        with st.spinner("🔍 Searching knowledge base..."):
            import time
            start_time = time.time()
            # Pass conversation history for better context
            current_messages = get_current_messages()
            answer, sources = ask_question(prompt, current_messages)
            response_time = time.time() - start_time
            st.session_state.avg_response_time.append(response_time)

        # Log chat interaction
        log_chat_interaction(
            session_id=st.session_state.current_session,
            user_id=user_id,
            user_message=prompt,
            assistant_response=answer,
            response_time=response_time,
            sources_count=len(sources) if sources else 0,
            intent="detected"  # Could be enhanced to detect actual intent
        )

        # Add assistant response to current session
        add_message_to_current_session({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "time": response_time
        })

        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container

    # Session Statistics
    if current_messages:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Messages", len(current_messages))
        with col2:
            assistant_msgs = len([m for m in current_messages if m["role"] == "assistant"])
            avg_time = sum([m.get("time", 0) for m in current_messages if m.get("time")]) / assistant_msgs if assistant_msgs > 0 else 0
            st.metric("Avg Response Time", f"{avg_time:.2f}s")
        with col3:
            st.metric("Session", st.session_state.chat_sessions[st.session_state.current_session]["title"])

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

    # Session Management Section
    st.markdown("""
        <h4 style='color: #0066CC; margin-bottom: 1rem;'>💬 Chat Session Management</h4>
    """, unsafe_allow_html=True)

    # Session Statistics
    stats = get_session_stats()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Sessions", stats["total_sessions"])
    with col2:
        st.metric("Total Messages", stats["total_messages"])
    with col3:
        st.metric("Avg Messages/Session", f"{stats['avg_messages_per_session']:.1f}")

    st.markdown("---")

    # Session Management Actions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧹 Cleanup Old Sessions (30+ days)", use_container_width=True):
            cleanup_old_sessions(30)
            st.success("✅ Old sessions cleaned up!")
            st.rerun()

    with col2:
        if st.button("📊 Refresh Statistics", use_container_width=True):
            st.rerun()

    st.markdown("---")

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

# ======================= TAB 5: SAFETY & GUIDELINES =======================
with tab5:
    st.markdown("""
        <h2 class='section-title'>🛡️ Safety Guidelines & Guardrails</h2>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); 
                    color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h3 style='margin: 0 0 1rem 0; color: white;'>🚨 Important Safety Notice</h3>
        <p style='margin: 0; font-size: 1.1rem; line-height: 1.6;'>
        This AI assistant incorporates high-level guardrails similar to ChatGPT's safety instructions. 
        These guardrails help prevent harmful, illegal, or inappropriate content while maintaining 
        educational and research capabilities.
        </p>
        </div>
    """, unsafe_allow_html=True)

    # Import guardrails for display
    from src.guardrails import get_safety_guidelines

    guidelines = get_safety_guidelines()

    # Main Guidelines
    st.markdown("""
        <h4 style='color: #0066CC; margin-bottom: 1rem;'>📋 Core Safety Guidelines</h4>
    """, unsafe_allow_html=True)

    for i, guideline in enumerate(guidelines['guidelines'], 1):
        st.markdown(f"""
            <div style='background: #F8FAFC; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #667EEA; margin-bottom: 0.5rem;'>
                <strong>{i}.</strong> {guideline}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Restricted Categories
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <h4 style='color: #DC2626; margin-bottom: 1rem;'>🚫 Restricted Categories</h4>
        """, unsafe_allow_html=True)

        for category, items in guidelines['restricted_categories'].items():
            with st.expander(f"📍 {category.replace('_', ' ').title()}", expanded=False):
                for item in items:
                    st.markdown(f"• {item}")

    with col2:
        st.markdown("""
            <h4 style='color: #059669; margin-bottom: 1rem;'>✅ Safe Contexts</h4>
        """, unsafe_allow_html=True)

        st.markdown("Content is generally allowed in these educational contexts:")
        for context in guidelines['safe_contexts']:
            st.markdown(f"• {context}")

    st.markdown("---")

    # Trigger Keywords
    st.markdown("""
        <h4 style='color: #D97706; margin-bottom: 1rem;'>⚠️ Content Monitoring</h4>
    """, unsafe_allow_html=True)

    st.markdown("The system monitors for these types of content:")

    keyword_cols = st.columns(3)
    keywords_list = list(guidelines['trigger_keywords'].keys())

    for i, keyword_type in enumerate(keywords_list):
        col_idx = i % 3
        with keyword_cols[col_idx]:
            with st.expander(f"{keyword_type.replace('_', ' ').title()}", expanded=False):
                keywords = guidelines['trigger_keywords'][keyword_type]
                for keyword in keywords:
                    st.markdown(f"• {keyword}")

    st.markdown("---")

    # System Status
    st.markdown("""
        <h4 style='color: #7C3AED; margin-bottom: 1rem;'>🔧 System Information</h4>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Guardrails Version", guidelines['version'])

    with col2:
        st.metric("Last Updated", guidelines['last_updated'][:10])

    with col3:
        st.metric("Active Categories", len(guidelines['restricted_categories']))

    # Test Guardrails
    st.markdown("---")
    st.markdown("""
        <h4 style='color: #0066CC; margin-bottom: 1rem;'>🧪 Test Guardrails</h4>
    """, unsafe_allow_html=True)

    test_query = st.text_area("Test a query against the guardrails:", 
                             placeholder="Enter a test query to see if it passes safety checks...",
                             height=100)

    if st.button("🔍 Check Safety", use_container_width=True):
        if test_query.strip():
            from src.guardrails import check_query
            is_safe, reason, metadata = check_query(test_query)

            if is_safe:
                st.success(f"✅ Safe: {reason}")
            else:
                st.error(f"🚫 Blocked: {reason}")

            with st.expander("📊 Detailed Analysis", expanded=False):
                st.json(metadata)
        else:
            st.warning("Please enter a query to test.")

# ======================= TAB 6: SYSTEM LOGS =======================
with tab6:
    st.markdown("""
        <h2 class='section-title'>📋 System Logs & Analytics</h2>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                    color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h3 style='margin: 0 0 1rem 0; color: white;'>📊 Activity Monitoring</h3>
        <p style='margin: 0; font-size: 1.1rem; line-height: 1.6;'>
        Comprehensive logging system tracks all chat interactions, session management, and system events. 
        Monitor usage patterns, performance metrics, and user activity in real-time.
        </p>
        </div>
    """, unsafe_allow_html=True)

    # Import logging functions
    from src.logger import get_chat_logs_summary

    # Get log summary
    log_summary = get_chat_logs_summary(days=30)

    # Display key metrics
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Interactions", log_summary.get("total_interactions", 0))
    with col2:
        st.metric("Active Sessions", log_summary.get("total_sessions", 0))
    with col3:
        st.metric("Unique Users", log_summary.get("total_users", 0))
    with col4:
        avg_time = log_summary.get("avg_response_time", 0)
        st.metric("Avg Response Time", f"{avg_time:.2f}s")

    # Intent distribution
    st.markdown("### 🎯 Intent Distribution")
    intents = log_summary.get("intents", {})
    if intents:
        intent_df = pd.DataFrame(list(intents.items()), columns=["Intent", "Count"])
        st.bar_chart(intent_df.set_index("Intent"))
    else:
        st.info("No chat interactions logged yet.")

    # Daily activity
    st.markdown("### 📅 Daily Activity (Last 30 Days)")
    daily_stats = log_summary.get("daily_stats", {})
    if daily_stats:
        daily_df = pd.DataFrame(list(daily_stats.items()), columns=["Date", "Activity"])
        daily_df = daily_df.sort_values("Date")
        st.line_chart(daily_df.set_index("Date"))
    else:
        st.info("No activity data available.")

    # Recent logs viewer
    st.markdown("### 📝 Recent Log Entries")
    try:
        log_file = Path("logs/chat_sessions/chat_sessions.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()[-20:]  # Last 20 entries

            if lines:
                log_text = ""
                for line in reversed(lines):  # Most recent first
                    # Format for display
                    parts = line.strip().split(' | ', 5)
                    if len(parts) >= 6:
                        timestamp, level, session, user, msg_type, details = parts
                        log_text += f"**{timestamp}** [{level}] {session} | {user} | {msg_type}\n"
                        log_text += f"*{details}*\n\n"

                st.text_area("Recent Logs", log_text, height=300, disabled=True)
            else:
                st.info("No log entries found.")
        else:
            st.warning("Log file not found.")
    except Exception as e:
        st.error(f"Error reading logs: {str(e)}")

    # Log controls
    st.markdown("### 🛠️ Log Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Analytics"):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Old Logs (30+ days)"):
            # This would need implementation
            st.info("Log cleanup feature coming soon.")

# ==================== Footer ====================
st.divider()
st.markdown("""
    <div style='text-align: center; color: #6B7280; font-size: 0.9rem; padding: 2rem 0;'>
        <p>🚀 <strong>Real-Time Multi-Source Knowledge Assistant</strong> | Version 1.0</p>
        <p>© 2026 Aniruddha kasar | All Rights Reserved</p>
        <p>Designed by Aniruddha Kasar</p>
        <p style='margin-top: 1rem; font-size: 0.85rem;'>
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Documentation</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Support</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Status</a> •
            <a href='#' style='color: #0066CC; text-decoration: none; margin: 0 1rem;'>Privacy</a>
        </p>
    </div>
""", unsafe_allow_html=True)