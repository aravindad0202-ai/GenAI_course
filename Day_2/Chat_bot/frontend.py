import streamlit as st
import requests
import uuid

# --- Configuration ---
BACKEND_BASE_URL = "http://localhost:8000"

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "chats" not in st.session_state:
    st.session_state.chats = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4()) # Generate dynamic tracking ID for the first chat
if "active_messages" not in st.session_state:
    st.session_state.active_messages = [] # Holds the currently visible conversation turns

# --- Helper Functions ---
def load_session_messages(session_id: str):
    """Fetches past conversation turns from the backend for the selected session."""
    try:
        response = requests.get(
            f"{BACKEND_BASE_URL}/chat/{session_id}",
            params={"user_id": st.session_state.user_id}
        )
        if response.status_code == 200:
            st.session_state.active_messages = response.json()
            st.session_state.current_session_id = session_id
        else:
            st.toast("Failed to load conversation history.", icon="⚠️")
    except requests.exceptions.ConnectionError:
        st.error("Backend unreachable.")

# --- UI Components ---
def login_page():
    st.title("Login")
    with st.form("login_form"):
        email_id = st.text_input("Email ID")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            try:
                response = requests.post(
                    f"{BACKEND_BASE_URL}/login", 
                    json={"email_id": email_id, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user_id = data.get("userID")
                    st.session_state.chats = data.get("chats", [])
                    st.session_state.logged_in = True
                    st.session_state.active_messages = []
                    st.session_state.current_session_id = str(uuid.uuid4()) # Fresh ID for a new login session
                    st.rerun()
                else:
                    st.toast("Invalid user", icon="🚨")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to backend on port 8000.")

def main_app():
    # --- Sidebar ---
    with st.sidebar:
        st.title("Your Chats")
        
        # Option to quickly start a completely new chat session
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session_id = str(uuid.uuid4())
            st.session_state.active_messages = []
            st.rerun()
            
        st.divider()
        
        # Render historical chat sessions mapping from the database
        if st.session_state.chats:
            for chat in st.session_state.chats:
                # Highlight or distinguish the active button visually matching the active session
                is_active = chat["sessionId"] == st.session_state.current_session_id
                button_label = f"💬 {chat['chatName']}" if not is_active else f"👉 {chat['chatName']}"
                
                if st.button(button_label, key=chat["sessionId"], use_container_width=True):
                    load_session_messages(chat["sessionId"])
                    st.rerun()
        else:
            st.write("No recent chats.")
            
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- Main Screen Conversation Window ---
    st.title("Gemini Chat Wrapper")
    
    # 1. Render all historical messages sequentially from memory
    for msg in st.session_state.active_messages:
        # Convert backend names ("model") to frontend recognizable avatar names ("assistant")
        avatar_role = "assistant" if msg["role"] == "model" else "user"
        with st.chat_message(avatar_role):
            st.write(msg["text"])

    # 2. Accept incoming user prompts
    prompt = st.chat_input("Type your message...")
    
    if prompt:
        # Display the user message right away locally
        with st.chat_message("user"):
            st.write(prompt)
            
        # Append locally to state immediately to avoid UI lag
        st.session_state.active_messages.append({"role": "user", "text": prompt})
        
        # Send payload matching your updated backend format
        payload = {
            "session_id": st.session_state.current_session_id,
            "user_id": st.session_state.user_id,
            "prompt": prompt
        }
        
        try:
            response = requests.post(f"{BACKEND_BASE_URL}/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                ai_text = data.get("response")
                
                # Render model turn locally
                with st.chat_message("assistant"):
                    st.write(ai_text)
                st.session_state.active_messages.append({"role": "model", "text": ai_text})
                
                # If this was the first prompt of a new session, update the sidebar list
                if not any(c["sessionId"] == st.session_state.current_session_id for c in st.session_state.chats):
                    st.session_state.chats.insert(0, {
                        "chatName": prompt[:25] + "...",
                        "sessionId": st.session_state.current_session_id
                    })
                    st.rerun()
            else:
                st.error("Error communicating with Gemini engine.")
        except requests.exceptions.ConnectionError:
            st.error("Backend communication failed.")

# --- Routing Logic ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()