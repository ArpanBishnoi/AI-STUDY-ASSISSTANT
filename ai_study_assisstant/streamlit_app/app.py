import streamlit as st

from session import init_session
from views.auth import render_auth_page
from views.shell import render_sidebar
from views.library import render_library_page
from views.summary import render_summary_page

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📘",
    layout="wide",
)

init_session()

if not st.session_state.authenticated:
    render_auth_page()
else:
    query_params = st.query_params
    page = query_params.get("page", "library")

    render_sidebar(page)

    if page == "summary":
        render_summary_page()
    else:
        render_library_page()
