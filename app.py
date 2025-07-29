import streamlit as st
from codexia_engine.loader import load_and_split_repo
from codexia_engine.vector_store import create_vector_store
from codexia_engine.qa_handler import create_qa_chain
import os

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
    /* Remove all styling from the main container */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
        border: none !important;
    }

    /* Style the inner div that Streamlit wraps the textarea in */
    div[data-testid="stChatInput"] > div:first-child {
        background-color: #262730 !important;
        border: 1px solid grey !important;
        border-radius: 10px !important;
    }

    /* On focus, change the border of that inner div and kill the shadow */
    div[data-testid="stChatInput"] > div:first-child:focus-within {
        border-color: white !important;
        box-shadow: none !important;
    }

    /* Ensure the textarea itself has no background or border */
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
    st.header("Codexia: Chat with any GitHub Repository 💬")

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
        for message in st.session_state.chat_history:
            avatar_icon = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar_icon):
                name = "You" if message["role"] == "user" else "Codexia"
                st.markdown(f'<div class="chat-name">{name}</div>', unsafe_allow_html=True)
                st.markdown(f'<div>{message["content"]}</div>', unsafe_allow_html=True)

        if user_question := st.chat_input("Your question..."):
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            with st.chat_message("user", avatar="👤"):
                st.markdown(f'<div class="chat-name">You</div>', unsafe_allow_html=True)
                st.markdown(f'<div>{user_question}</div>', unsafe_allow_html=True)

            with st.spinner("Thinking..."):
                result = st.session_state.qa_chain.invoke({"question": user_question})
                ai_response = result["answer"]
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f'<div class="chat-name">Codexia</div>', unsafe_allow_html=True)
                    st.markdown(f'<div>{ai_response}</div>', unsafe_allow_html=True)
