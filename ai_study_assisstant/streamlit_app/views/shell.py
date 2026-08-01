import streamlit as st

from session import logout


def render_sidebar(current_page: str):
    with st.sidebar:
        st.title("AI Study Assistant")
        st.caption(f"User ID: {st.session_state.user_id}")

        st.divider()
        st.subheader("Navigation")
        if st.button(
            "My Library",
            key="nav_library",
            use_container_width=True,
            type="primary" if current_page == "library" else "secondary",
        ):
            st.query_params.page = "library"
            st.rerun()
        if st.button(
            "Summarize PDF",
            key="nav_summary",
            use_container_width=True,
            type="primary" if current_page == "summary" else "secondary",
        ):
            st.query_params.page = "summary"
            st.rerun()

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
