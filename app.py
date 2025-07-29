import streamlit as st
from sympy import python
from codexia_engine.loader import load_and_split_repo
from codexia_engine.vector_store import create_vector_store
from codexia_engine.qa_handler import create_qa_chain
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Codexia",
    page_icon="💻",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Button Styling */
    div.stButton > button {
        background-color: #003366;
        color: white;
        border: 1px solid white;
        border-radius: 5px;
    }

    div.stButton > button:hover {
        background-color: #218838;
        color: white;
        border: 1px solid white;
    }

    div.stButton > button:active,
    div.stButton > button:focus,
    div.stButton > button:visited {
        background-color: #218838 !important;
        color: white !important;
        border: 1px solid white !important;
        outline: none !important;
        box-shadow: none !important;
    }

    div.stButton > button:focus-visible {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Text Input Box */
    div[data-testid="stTextInput"] > div {
        border: 1px solid white;
        border-radius: 5px;
    }
    div[data-testid="stTextInput"] > div:focus-within {
        border-color: white !important;
        box-shadow: none !important;
    }

    /* Chat Input Fix */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stChatInput"] > div:first-child {
        background-color: #262730 !important;
        border: 1px solid grey !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] > div:first-child:focus-within {
        border-color: white !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        outline: none !important;
        box-shadow: none !important;
    }

    .chat-name {
        font-weight: bold;
        font-size: 0.85rem;
        margin-bottom: 4px;
        color: #ccc;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Function to Render Response ---
def render_response(response):
    """
    Parses the AI response and renders text with markdown and code with st.code.
    """
    # Regex to find code blocks (e.g., 

    code_pattern = r"```(\w*)\n(.*?)```"

    
    # Find all code blocks and split the response text by them
    parts = re.split(code_pattern, response, flags=re.DOTALL)
    
    # The parts list will be like [text, lang, code, text, lang, code, ...]
    for i in range(len(parts)):
        part = parts[i]
        if not part:
            continue
        
        # Check if the part is a language specifier (from the regex capture group)
        if i % 3 == 1:
            lang = part
            code = parts[i+1]
            st.code(code, language=lang or "plaintext")
        # Check if the part is a code block
        elif i % 3 == 2:
            # This part is code, which we've already handled with its language, so skip
            continue
        # Otherwise, it's plain text
        else:
            st.markdown(part)


# --- Session State Initialization ---
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Welcome Screen ---
if st.session_state.show_welcome:
    st.title("Welcome to Codexia 💻")
    st.markdown("### Your AI-powered GitHub Repository Analyst")
    st.markdown("""
    Codexia allows you to chat with any public GitHub repository to understand its structure, functionality, and code.

    **How to use:**
    1.  Click the "Get Started" button below.
    2.  Paste a GitHub repository URL into the input box.
    3.  Click "Analyze Repository" and let the AI work its magic.
    4.  Once analyzed, ask any question about the codebase!
    """)
    if st.button("Get Started"):
        st.session_state.show_welcome = False
        st.rerun()
else:
    # --- Main Application Screen ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("Codexia: Chat with any GitHub Repository 💬")
    with col2:
        # "Clear Chat" button is placed here
        if st.session_state.qa_chain:
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()


    st.write("Enter a public GitHub Repository URL to begin:")

    repo_url = st.text_input("GitHub URL", label_visibility="collapsed")

    if st.button("Analyze Repository"):
        if repo_url:
            with st.spinner("Analyzing repository... This may take a moment."):
                try:
                    chunks, file_names = load_and_split_repo(repo_url)

                    if chunks:
                        vector_store = create_vector_store(chunks)
                        if vector_store:
                            st.session_state.qa_chain = create_qa_chain(vector_store, file_names)
                            st.session_state.chat_history = []
                            st.success("Repository analyzed successfully! You can now ask questions.")
                        else:
                            st.error("Failed to create the vector store.")
                    else:
                        st.warning("Could not find any documents to process in the repository.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a repository URL.")

    # --- Chat Interface ---
    if st.session_state.qa_chain:
        # Display previous chat messages
        for message in st.session_state.chat_history:
            avatar_icon = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar_icon):
                name = "You" if message["role"] == "user" else "Codexia"
                st.markdown(f'<div class="chat-name">{name}</div>', unsafe_allow_html=True)
                # Use the helper function to render the response
                render_response(message["content"])

        # Handle new user input
        if user_question := st.chat_input("Your question..."):
            # Add user message to history and display it
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user", avatar="👤"):
                st.markdown(f'<div class="chat-name">You</div>', unsafe_allow_html=True)
                render_response(user_question)

            # Get and display AI response
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(f'<div class="chat-name">Codexia</div>', unsafe_allow_html=True)
                with st.spinner("Thinking..."):
                    result = st.session_state.qa_chain.invoke({"question": user_question})
                    ai_response = result.get("answer", "Sorry, I could not find an answer.")
                    # Use the helper function to render the AI response
                    render_response(ai_response)

            # Add the complete AI response to the chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})