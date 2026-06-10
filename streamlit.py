import streamlit as st
import requests
import uuid

import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
st.title("My AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Render FastAPI endpoint
    backend_url = os.getenv("BACKEND_URL")
    
    payload = {
        "message": prompt,
        "thread_id": st.session_state.thread_id
    }

    try:
        response = requests.post(backend_url, json=payload)
    
        if response.status_code == 200:
            response_json = response.json()
            
            ai_response = response_json.get("answer", "Error: 'answer' key missing from backend data.")
        
        else:
            ai_response = f"Backend Server Error (Status {response.status_code}): {response.text}"
            
    except requests.exceptions.RequestException as network_error:
        ai_response = f"Connection failure. Render service may be warming up. Error details: {network_error}"

    with st.chat_message("assistant"):
        st.markdown(ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    