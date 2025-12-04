# app.py
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import google.generativeai as genai

# Configure the Gemini API
API_KEY = st.secrets["GEMINI_API_KEY"] # using Streamlit secret in ~/.streamlit/secrets.toml file
# API_KEY = os.getenv("GEMINI_API_KEY") # using python secret in ~/.env file
genai.configure(api_key=API_KEY)

# Configure Streamlit page
st.set_page_config(page_title="Matchmaking Chatbot", layout="centered")
st.title("🌱 Matchmaking Chatbot")
st.subheader("Your AI assistant for University Bremen Professor and Research matchmaking")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm your matchmaking helper to help you find research project at University of Bremen. Ask me anything about Professor and Research Group at University of Bremen. How can I help you today?"
        }
    ]

def display_messages():
    """Display all messages in the chat history"""
    for msg in st.session_state.messages:
        author = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(author):
            st.write(msg["content"])

def friendly_wrap(raw_text):
    """Add a friendly tone to AI responses"""
    return (
        "Great question! 🌱\n\n"
        f"{raw_text.strip()}\n\n"
        "Would you like me to elaborate on any part of this, or do you have other questions?"
    )

# Display existing messages
display_messages()

# Handle new user input
prompt = st.chat_input("Ask me about research project, professor in University of Bremen...")

if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show user message
    with st.chat_message("user"):
        st.write(prompt)

    # Show thinking indicator while processing
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("🤔 Thinking...")

        # Call Gemini API
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(
                f"You are a helpful University of Bremen professor and researcher expert. Please provide accurate, encouraging information about: {prompt}"
            )

            # Extract response text
            answer = response.text
            friendly_answer = friendly_wrap(answer)

        except Exception as e:
            friendly_answer = f"I'm sorry, I encountered an error: {e}. Please try asking your question again."

        # Replace thinking indicator with actual response
        placeholder.write(friendly_answer)

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": friendly_answer})

    # Refresh the page to show updated chat
    st.rerun()