import streamlit as st

from session import init_session
from views.auth import render_auth_page
from views.shell import render_sidebar
from views.library import render_library_page
from views.summary import render_summary_page
from views.ask import render_ask_page
from views.upload import render_upload_page
from views.flashcards import render_flashcards_page
from views.summary_history import render_summary_history_page

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📘",
    layout="wide",
)

init_session()

if "current_page" not in st.session_state:
    st.session_state.current_page = "library"

if not st.session_state.authenticated:
    render_auth_page()
else:
    render_sidebar()

    page = st.session_state.current_page

    if page == "summary":
        render_summary_page()
    elif page == "ask":
        render_ask_page()
    elif page == "upload":
        render_upload_page()
    elif page == "flashcards":
        render_flashcards_page()
    elif page == "summary_history":
        render_summary_history_page()
    else:
        render_library_page()
