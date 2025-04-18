import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os



# Configure Gemini
GEMINI_API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# Available models
MODELS = {
    "Gemini 1.5 flash (Text)": "gemini-1.5-flash",
    "Gemini 1.5 Pro (Multimodal)": "gemini-1.5-pro-latest",
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "gemini-1.5-pro"

# Sidebar controls
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model selection
    selected_model = st.selectbox(
        "Choose Model",
        list(MODELS.keys()),
        index=0
    )
    st.session_state.model = MODELS[selected_model]
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Image/PDF (for Gemini 1.5)",
        type=["jpg", "png", "pdf"]
    )
    
    # Clear chat button
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown(f"**Current Model:** `{st.session_state.model}`")
    st.markdown("Powered by [Google Gemini](https://ai.google.dev/)")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"], width=300)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "type": "text",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare multimodal content
    content = [prompt]
    if uploaded_file:
        if uploaded_file.type.startswith('image/'):
            image = Image.open(uploaded_file)
            st.session_state.messages.append({
                "role": "user",
                "type": "image",
                "content": image
            })
            content.append(image)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                model = genai.GenerativeModel(st.session_state.model)
                
                if uploaded_file and "1.5" in st.session_state.model:
                    # Multimodal processing
                    response = model.generate_content(content)
                else:
                    # Text-only processing
                    if uploaded_file:
                        st.warning("This model doesn't support images. Using text-only mode.")
                    chat = model.start_chat(history=[])
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "text",
                    "content": response.text
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")