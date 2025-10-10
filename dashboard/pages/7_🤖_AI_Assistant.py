"""
AI Assistant - Conversational Property Search & Analysis
Full-screen chat interface powered by Claude
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
dashboard_dir = Path(__file__).parent.parent
project_root = dashboard_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(dashboard_dir))

from modules.ai_agent import AIPropertyAgent

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .user-message {
        background: #007bff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px 0;
        max-width: 70%;
        margin-left: auto;
        float: right;
        clear: both;
    }
    .assistant-message {
        background: white;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 10px 0;
        max-width: 70%;
        border: 1px solid #dee2e6;
        float: left;
        clear: both;
    }
    .message-time {
        font-size: 0.75em;
        color: #6c757d;
        margin-top: 4px;
    }
    .quick-action-btn {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 20px;
        cursor: pointer;
        font-size: 0.9em;
    }
    .quick-action-btn:hover {
        background: #e9ecef;
    }
    .property-card-compact {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 AI Property Assistant")
st.markdown("Ask me anything about properties, investments, or market trends!")
st.markdown("---")

# Initialize session state
if 'ai_agent' not in st.session_state:
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not configured")
        st.markdown("""
        ### Setup Required

        To use the AI Assistant, you need to configure your Anthropic API key:

        1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
        2. Add to your `.env` file:
           ```
           ANTHROPIC_API_KEY=your_key_here
           ```
        3. Restart the dashboard

        **Note:** The AI Assistant uses Claude to provide intelligent property analysis
        and recommendations. Standard dashboard features work without this.
        """)
        st.stop()

    try:
        st.session_state.ai_agent = AIPropertyAgent(api_key=api_key)
        st.session_state.chat_messages = []
    except Exception as e:
        st.error(f"Failed to initialize AI Agent: {e}")
        st.stop()

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Quick Action Buttons
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔥 Show Hot Deals", use_container_width=True):
        st.session_state.quick_action = "Show me the hottest deals available right now"

with col2:
    if st.button("📊 Market Overview", use_container_width=True):
        st.session_state.quick_action = "Give me an overview of the current market"

with col3:
    if st.button("💡 Investment Tips", use_container_width=True):
        st.session_state.quick_action = "What should I look for in an investment property?"

with col4:
    if st.button("🏘️ Best Neighborhoods", use_container_width=True):
        st.session_state.quick_action = "Which neighborhoods have the best deals?"

st.markdown("---")

# Chat History Display
st.markdown("### 💬 Conversation")

# Display chat messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_messages:
        if msg['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                {msg['content']}
                <div class="message-time">{msg['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                {msg['content']}
                <div class="message-time">{msg['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

# Handle quick actions
if 'quick_action' in st.session_state:
    user_input = st.session_state.quick_action
    del st.session_state.quick_action
else:
    user_input = None

# Chat Input
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])

    with col1:
        user_message = st.text_input(
            "Ask me anything...",
            placeholder="E.g., 'Show me 3 bedroom homes under $700K in La Jolla'",
            label_visibility="collapsed",
            value=user_input or ""
        )

    with col2:
        submit_button = st.form_submit_button("Send 📤", use_container_width=True)

# Process message
if submit_button and user_message:
    # Add user message
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": timestamp
    })

    # Get AI response
    with st.spinner("🤔 Thinking..."):
        try:
            # Get context
            context = {
                "page": "AI Assistant",
                "user_preferences": {}
            }

            # Add properties to context if viewing
            if 'scraped_properties' in st.session_state:
                context['properties_loaded'] = len(st.session_state['scraped_properties'])

            # Get AI response
            response = st.session_state.ai_agent.chat(user_message, context=context)

            # Add assistant response
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}",
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

    # Rerun to display new messages
    st.rerun()

# Sidebar with conversation management
with st.sidebar:
    st.markdown("### 💾 Conversation")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_messages = []
        # Reinitialize AI agent to pick up any system prompt changes
        api_key = os.getenv('ANTHROPIC_API_KEY')
        st.session_state.ai_agent = AIPropertyAgent(api_key=api_key)
        st.rerun()

    st.markdown(f"**Messages:** {len(st.session_state.chat_messages)}")

    st.markdown("---")
    st.markdown("### 📊 Statistics")

    if 'scraped_properties' in st.session_state:
        props = st.session_state['scraped_properties']
        st.metric("Properties Loaded", len(props))

        hot_count = len([p for p in props if p.get('opportunity_score', 0) >= 90])
        st.metric("Hot Deals", hot_count)
    else:
        st.info("No properties loaded yet")

    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    **Try asking:**
    - "Show me 3 bed homes under $700K"
    - "Analyze 1234 Main St"
    - "Compare properties in La Jolla vs Pacific Beach"
    - "What's the average price in San Diego?"
    - "Calculate ROI for $600K property"
    """)

# Example queries section (if no messages yet)
if not st.session_state.chat_messages:
    st.markdown("---")
    st.markdown("### 💬 Get Started - Try These Examples:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🔍 Search & Discovery**
        - "Show me hot deals in San Diego"
        - "Find 3 bedroom homes under $800K"
        - "Properties with high cash flow potential"
        - "What's new this week?"
        """)

        st.markdown("""
        **📊 Market Analysis**
        - "What's happening in the San Diego market?"
        - "Which neighborhoods have the best deals?"
        - "Show me price trends"
        - "Compare San Diego vs Las Vegas"
        """)

    with col2:
        st.markdown("""
        **🏠 Property Analysis**
        - "Analyze [property address]"
        - "Why is this a good deal?"
        - "What are the risks?"
        - "Calculate ROI for this property"
        """)

        st.markdown("""
        **⚙️ Configuration**
        - "Set my budget to $500K-$1M"
        - "Only show me properties over 15% below market"
        - "Alert me for new hot deals"
        - "What's my current criteria?"
        """)

# Footer
st.markdown("---")
st.markdown("""
**Powered by Claude (Anthropic)** |
[Report Issue](https://github.com/anthropics/claude-code/issues) |
[Documentation](https://docs.claude.com/)
""")
