import streamlit as st
from groq import Groq
import os

# Set up the Streamlit UI
st.set_page_config(page_title="Streamlit and Groq Chatbot", layout="wide")
st.title("Streamlit and Groq Chatbot 🤖")

# Add a sidebar for API key input
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_groq_response_stream(user_prompt, api_key):
    """
    Streams a response from the Groq API.
    """
    if not api_key:
        # Using a generator to yield the message and stop
        def message_generator():
            yield "Please add your Groq API key to continue."
        return message_generator()

    try:
        client = Groq(api_key=api_key)
        
        def response_generator():
            stream = client.chat.completions.create(
                messages=[{"role": "user", "content": user_prompt}],
                model="llama3-8b-8192",
                stream=True,
            )
            for chunk in stream:
                yield chunk.choices[0].delta.content or ""
        
        return response_generator()

    except Exception as e:
        def error_generator():
            yield f"An error occurred: {e}"
        return error_generator()


# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response_stream = get_groq_response_stream(prompt, api_key)
        # st.write_stream returns the full response once the stream is complete
        full_response = st.write_stream(response_stream)

    # Add the full assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

