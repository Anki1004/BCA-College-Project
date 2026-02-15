import streamlit as st
import google.generativeai as genai
import requests
from streamlit_lottie import st_lottie
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="BCA AI Assistant", page_icon="🤖", layout="wide")

# --- 2. 3D ANIMATION LOADER ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Professional 3D Robot Animation for your BCA Project
lottie_robot = load_lottieurl("https://lottie.host/8e31a980-607b-498c-87d3-f57f6139163d/vXvUvT4O9H.json")

# --- 3. API KEY ROTATION LOGIC ---
def get_gemini_response(prompt):
    # Fetch your list of keys from Streamlit Secrets
    api_keys = st.secrets["GEMINI_KEYS"]
    
    for key in api_keys:
        try:
            genai.configure(api_key=key)
            # Using 1.5-flash for maximum stability in 2026
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                # If this key is out of quota, it tries the next key automatically
                continue
            else:
                return f"⚠️ Technical Error: {e}"
    
    return "🚀 All AI channels are busy right now. Please wait 30 seconds and try again!"

# --- 4. SIDEBAR (Student Profile & 3D Element) ---
with st.sidebar:
    if lottie_robot:
        st_lottie(lottie_robot, height=200, key="robot")
    
    st.title("🎓 Project Details")
    st.info("**Student Name:** Ankit Gupta, Khushi , Ayush")
    st.info("**Course:** BCA")
    st.info("**Project:** AI Chatbot")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN CHAT INTERFACE ---
st.title("🤖 My College AI Assistant")
st.subheader("BCA Final Year Project")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. CHAT INPUT & EXECUTION ---
if prompt := st.chat_input("Ask me about BCA, Coding, or Data Science..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("🔄 Rotating keys & generating response..."):
            ai_response = get_gemini_response(prompt)
            st.markdown(ai_response)

            st.session_state.messages.append({"role": "assistant", "content": ai_response})
