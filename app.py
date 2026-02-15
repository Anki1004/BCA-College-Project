import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# Replace 'YOUR_API_KEY' with the key from Google AI Studio
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. SIDEBAR (Perfect for College Projects) ---
with st.sidebar:
    st.title("🎓 Project Details")
    st.info("**Student Name:** Ankit Gupta")
    st.info("**Course:** BCA")
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 3. MAIN UI ---
st.title("🤖 My College AI Assistant")
st.subheader("BCA Final Year Project")

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. CHAT LOGIC ---
if prompt := st.chat_input("Ask me about BCA, Coding, or Projects..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            try:
                # Send the message to the model
                response = model.generate_content(prompt)
                full_res = response.text
                st.markdown(full_res)
                
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": full_res})
            except Exception as e:
                st.error(f"Something went wrong: {e}")