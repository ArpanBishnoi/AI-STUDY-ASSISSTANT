import streamlit as st

from session import logout
from views.library import render_library_page


def render_sidebar(current_page: str):
    with st.sidebar:
        st.title("AI Study Assistant")
        st.caption(f"User ID: {st.session_state.user_id}")

        st.divider()
        st.subheader("Navigation")
        st.markdown(f"**{'→ ' if current_page == 'library' else ''}My Library**")
        st.caption("Next: Summarize PDF")

        st.divider()
        st.subheader("Active PDF")
        if st.session_state.pdf_id:
            st.success(f"PDF ID: {st.session_state.pdf_id}")
        else:
            st.info("No PDF selected. Open one from My Library.")

        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
