
import streamlit as st
import requests

# API configuration
API_URL = "http://127.0.0.1:8000/chat"

# Page configuration
st.set_page_config(
    page_title="Kryptix Assistant",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .stApp {
        background-color: #0e1117;
    }

    h1, h2, h3, p, label {
        color: white;
    }

    .subtitle {
        color: #a0aec0;
        text-align: center;
        margin-bottom: 25px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 Kryptix Assistant")

st.markdown(
    '<p class="subtitle">Your AI-powered personal assistant</p>',
    unsafe_allow_html=True
)

st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Powered by Google Gemini")
    st.write("Backend: FastAPI")

    if st.button("🗑️ New Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

    st.divider()
    st.caption("Kryptix Assistant | Internship Task 1")

# Welcome message
if not st.session_state.messages:
    st.info(
        "Hello! 👋 I'm Kryptix Assistant. "
        "Ask me anything and let's get started!"
    )

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Send message to backend
    with st.chat_message("assistant"):

        with st.spinner("Kryptix Assistant is thinking..."):

            try:
                payload = {
                    "message": user_input,
                    "conversation_id": st.session_state.conversation_id
                }

                response = requests.post(
                    API_URL,
                    json=payload,
                    timeout=45
                )

                response.raise_for_status()

                data = response.json()

                # Save conversation ID
                st.session_state.conversation_id = (
                    data["conversation_id"]
                )

                assistant_reply = data["reply"]

                st.markdown(assistant_reply)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply
                })

            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the backend. "
                    "Please make sure FastAPI is running."
                )

            except requests.exceptions.RequestException as error:
                st.error(f"API Error: {error}")

            except Exception as error:
                st.error(f"Unexpected error: {error}")
