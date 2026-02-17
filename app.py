import streamlit as st
import google.generativeai as genai
import requests
from streamlit_lottie import st_lottie
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="BCA AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

.chat-title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    background: -webkit-linear-gradient(#38bdf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.chat-subtitle {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 20px;
}

.stChatMessage {
    border-radius: 15px !important;
}

.stButton>button {
    border-radius: 10px;
    background-color: #6366f1;
    color: white;
}

.stButton>button:hover {
    background-color: #4f46e5;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOTTIE LOADER ----------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_robot = load_lottieurl(
    "https://lottie.host/8e31a980-607b-498c-87d3-f57f6139163d/vXvUvT4O9H.json"
)

# ---------------- GEMINI RESPONSE ----------------
def get_gemini_response(prompt):
    try:
        api_keys = st.secrets["GEMINI_KEYS"]
    except:
        return "⚠️ API keys not found in Streamlit Secrets."

    for key in api_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                continue
            else:
                return f"⚠️ Error: {e}"

    return "🚀 All AI channels are busy. Please try again in 30 seconds."

# ---------------- SIDEBAR ----------------
with st.sidebar:
    if lottie_robot:
        st_lottie(lottie_robot, height=200)

    st.markdown("## 🎓 Project Details")
    st.markdown("**Student:** Ankit Gupta, Khush , Ayush")
    st.markdown("**Course:** BCA")
    st.markdown("**Project:** AI Chatbot")

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------- MAIN HEADER ----------------
st.markdown('<div class="chat-title">🤖 My College AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-subtitle">BCA Final Year AI Project</div>', unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("Ask me about BCA, Coding, Python, Data Science..."):
    
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking..."):
            response = get_gemini_response(prompt)

            # Typing animation effect
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})


