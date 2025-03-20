from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import time

load_dotenv()   # load all env. variables

# set api key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# initialize our models
vis_model = genai.GenerativeModel("gemini-1.5-flash")
langugae_model = genai.GenerativeModel("gemini-pro")

# function to load gemini pro vision model and get responses
def get_gemini_response(input, image):
    # if there present any text input besides image, then generate both
    if (input != "") and (image != ""):
        response = vis_model.generate_content([input, image])
    elif (input != "") and (image == ""):
        response = langugae_model.generate_content(input)
    else:
        response = vis_model.generate_content(image)
    return response.text

def stream_data(prompt, image):
    sentences = get_gemini_response(prompt, image).split(". ")
    for sentence in sentences:
        for word in sentence.split():
            yield word + " "
            time.sleep(0.02)

# initialize our streamlit app
st.set_page_config(
    page_title="Multimodal Content Generation",
    page_icon="⚡️",
    layout="wide"
)

# give title
st.sidebar.title(":rainbow[MULTIMODAL CONTENT GENERATION]")
st.sidebar.divider()

# Multimodals Options
multimodal_options = st.sidebar.radio(
    "**Select What To Do...**",
    options=["Chat and Image Summarization", "Text 2 Image"],
    index=0,
    horizontal=False,
)
st.sidebar.divider()

# New chat button, to get the fresh chat page
if st.sidebar.button("Get **New Chat** Fresh Page"):
    st.session_state["messages"] = []  # Clear chat history
    st.experimental_rerun()  # Trigger page reload
# create image upload option in sidebar
with st.expander("**Wanna Upload an Image?**"):
    uploaded_file = st.file_uploader("Choose an image for **Image Summarizer** task...",
                                    type=["jpg", "jpeg", "png"])
    image=""
    if uploaded_file is not None:
        image=Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
# Create a container to hold the entire chat history
chat_container = st.container()
# initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with chat_container:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
# create input prompt (textbox)
if prompt := st.chat_input("Type here..."):
    # display user message in chat message container
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)
    # add user message to chat history
    st.session_state.messages.append({"role" : "user",
                                    "content" : prompt})
    # display assistant message in chat message container
    with chat_container:
        with st.chat_message("assistant"):
            should_format_as_code = any(keyword in prompt.lower() for keyword in ["code", "python", "java", "javascript", "c++", "c", "program", "react", "reactjs", "node", "nodejs", "html", "css", "javascript", "js"])
            if should_format_as_code:
                st.code(get_gemini_response(prompt, image))
            else:
                st.write_stream(stream_data(prompt, image))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": get_gemini_response(prompt, image)})