import streamlit as st
import requests
import uuid

# Set up clean web page configuration
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
st.title("My AI Chatbot")

# 1. Initialize session state for tracking chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Initialize a persistent thread_id string for this conversation session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# 3. Render previous dialogue bubbles from history upon refresh
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Listen for and process fresh user chat submissions
if prompt := st.chat_input("Ask me anything..."):
    
    # Render user message locally inside the UI interface
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Target URL pointing to your Render FastAPI endpoint
    backend_url = "https://rag-agent-with-langgraph.onrender.com/chat"
    
    # Request Payload built perfectly to match your exact ChatRequest model schema
    payload = {
        "message": prompt,
        "thread_id": st.session_state.thread_id
    }

    try:
        # Deliver network POST transaction over the web
        response = requests.post(backend_url, json=payload)
        
        # Scenario A: Connection successful and validated
        if response.status_code == 200:
            response_json = response.json()
            
            # FIXED: Now matches your FastAPI key configuration ("answer")
            ai_response = response_json.get("answer", "Error: 'answer' key missing from backend data.")
            
        # Scenario B: Target server rejects layout rules or experiences errors
        else:
            ai_response = f"Backend Server Error (Status {response.status_code}): {response.text}"
            
    # Scenario C: Network architecture offline or unreachable
    except requests.exceptions.RequestException as network_error:
        ai_response = f"Connection failure. Render service may be warming up. Error details: {network_error}"

    # Render assistant's reply inside a dedicated chat bubble block
    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    