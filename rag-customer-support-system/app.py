"""
Tesla Cybertruck Customer Support System
RAG-based chatbot with support ticket creation
"""
import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_engine import RAGEngine
import config

# Page configuration
st.set_page_config(
    page_title="Tesla Cybertruck Support",
    page_icon="🚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .citation {
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
        margin-top: 0.5rem;
    }
    .ticket-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .stats-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'rag_engine' not in st.session_state:
    with st.spinner("Initializing support system..."):
        st.session_state.rag_engine = RAGEngine()

# Sidebar
with st.sidebar:
    st.markdown("### 🚙 Tesla Cybertruck Support")
    st.markdown("---")

    st.markdown("### 📞 Contact Information")
    st.markdown(f"**Company:** {config.COMPANY_NAME}")
    st.markdown(f"**Email:** {config.COMPANY_EMAIL}")
    st.markdown(f"**Phone:** {config.COMPANY_PHONE}")

    st.markdown("---")

    st.markdown("### 📊 System Stats")
    stats = st.session_state.rag_engine.get_stats()
    st.markdown(f"**Documents Indexed:** {stats['total_chunks']} chunks")
    st.markdown(f"**Collection:** {stats['collection_name']}")

    st.markdown("---")

    st.markdown("### ℹ️ How to Use")
    st.markdown("""
    1. **Ask Questions** about your Cybertruck
    2. **Get Answers** with source citations
    3. **Create Tickets** when you need help

    **Example Questions:**
    - How do I charge the Cybertruck?
    - What is the towing capacity?
    - How do I enable autopilot?
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main content
st.markdown('<div class="main-header">🚙 Tesla Cybertruck Support Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about your Cybertruck or create support tickets</div>', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    if role == "user":
        st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong><br>{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">🤖 <strong>Assistant:</strong><br>{content}</div>', unsafe_allow_html=True)

        # Display sources if available
        if "sources" in message and message["sources"]:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    metadata = source['metadata']
                    st.markdown(f"**Source {i}:** {metadata['filename']}, Page {metadata['page_number']}")
                    st.text(source['text'][:200] + "...")
                    st.markdown("---")

# Chat input
user_input = st.chat_input("Ask a question or request support...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })

    # Get response from RAG engine
    with st.spinner("Thinking..."):
        # Prepare conversation history for RAG engine
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages[:-1]  # Exclude current message
        ]

        response = st.session_state.rag_engine.query(
            user_message=user_input,
            conversation_history=conversation_history
        )

    # Add assistant response to history
    assistant_message = {
        "role": "assistant",
        "content": response['content'],
        "timestamp": datetime.now(),
        "type": response['type']
    }

    if 'sources' in response:
        assistant_message['sources'] = response['sources']

    if 'ticket_info' in response:
        assistant_message['ticket_info'] = response['ticket_info']

    st.session_state.messages.append(assistant_message)

    # Rerun to display new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    'Powered by OpenAI GPT-4 & ChromaDB | Built with Streamlit'
    '</div>',
    unsafe_allow_html=True
)
