#!/usr/bin/env python3
"""
DealFinder Pro - AI-First Real Estate Platform
Homepage redirects to AI Assistant for conversational interface
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="DealFinder Pro - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Immediate redirect to AI Assistant (the new homepage)
st.switch_page("pages/7_🤖_AI_Assistant.py")
