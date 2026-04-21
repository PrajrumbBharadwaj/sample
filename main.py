import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ---- 1. SETUP & AUTH ----
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("🚨 API Key missing!")
    st.stop()

# Using Gemini 3.1 for high speed and better memory handling
MODEL_ID = "gemini-3.1-flash-lite-preview" 
model = genai.GenerativeModel(MODEL_ID)

# ---- 2. UI STYLING (VIBEY DARK) ----
st.set_page_config(page_title="UrbanBot Pro", page_icon="⚡")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.1); }
    .stMarkdown p { color: white !important; font-weight: 500 !important; text-shadow: 1px 1px 2px black; }
    h1 { text-align: center; background: linear-gradient(to right, #00dbde, #fc00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>UrbanBot Pro</h1>", unsafe_allow_html=True)
st.caption("<p style='text-align:center; color:#00dbde;'>Active Session • Memory Enabled</p>", unsafe_allow_html=True)

# ---- 3. STATEFUL CHAT SESSION (THE FIX) ----

# Initialize the actual AI Chat Session in Streamlit memory
if "chat_session" not in st.session_state:
    # This 'history' list is what the AI actually "reads" to remember you
    st.session_state.chat_session = model.start_chat(history=[])

# Initialize the display messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Greeting
    intro = "✨ **UrbanBot Pro at your service.** What can I do for your home today?"
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---- 4. RESPONSIVE INTERACTION ----
if prompt := st.chat_input("Tell me what you need..."):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response using the CHAT SESSION
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # We add a hidden instruction to every message to keep it on track
            instruction = f"""
            Context: You are UrbanBot. 
            User provided: {prompt}
            Instructions: 
            - Check your chat history. 
            - If the user already provided Pincode, Service, or Time, DO NOT ask for them again.
            - If all details (Service, Pincode, Time, Issue) are present, say "BOOKING FINALIZED" and summarize the details.
            - Be very concise.
            """
            
            try:
                # 'send_message' automatically tracks history now!
                response = st.session_state.chat_session.send_message(instruction)
                bot_text = response.text
                
                st.markdown(bot_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_text})
            except Exception as e:
                st.error(f"Error: {e}")