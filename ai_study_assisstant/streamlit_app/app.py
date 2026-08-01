import streamlit as st

from session import init_session
from views.auth import render_auth_page
from views.shell import render_sidebar
from views.library import render_library_page

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📘",
    layout="wide",
)

init_session()

if not st.session_state.authenticated:
    render_auth_page()
else:
    render_sidebar("library")
    render_library_page()
