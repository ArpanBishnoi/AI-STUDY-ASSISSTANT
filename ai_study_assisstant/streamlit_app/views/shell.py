import streamlit as st

from session import logout


def render_sidebar():
    with st.sidebar:
        st.title("AI Study Assistant")
        st.caption(f"User ID: {st.session_state.user_id}")

        st.divider()
        st.subheader("Navigation")
        current = st.session_state.get("current_page", "library")
        if st.button(
            "My Library",
            key="nav_library",
            use_container_width=True,
            type="primary" if current == "library" else "secondary",
        ):
            st.session_state.current_page = "library"
            st.rerun()
        if st.button(
            "Summarize PDF",
            key="nav_summary",
            use_container_width=True,
            type="primary" if current == "summary" else "secondary",
        ):
            st.session_state.current_page = "summary"
            st.rerun()
        if st.button(
            "Ask a Question",
            key="nav_ask",
            use_container_width=True,
            type="primary" if current == "ask" else "secondary",
        ):
            st.session_state.current_page = "ask"
            st.rerun()
        if st.button(
            "Upload PDF",
            key="nav_upload",
            use_container_width=True,
            type="primary" if current == "upload" else "secondary",
        ):
            st.session_state.current_page = "upload"
            st.rerun()
        if st.button(
            "Flashcards & Quiz",
            key="nav_flashcards",
            use_container_width=True,
            type="primary" if current == "flashcards" else "secondary",
        ):
            st.session_state.current_page = "flashcards"
            st.rerun()
        if st.button(
            "Summary History",
            key="nav_summary_history",
            use_container_width=True,
            type="primary" if current == "summary_history" else "secondary",
        ):
            st.session_state.current_page = "summary_history"
            st.rerun()
        if st.button(
            "Explain AI",
            key="nav_explain",
            use_container_width=True,
            type="primary" if current == "explain" else "secondary",
        ):
            st.session_state.current_page = "explain"
            st.rerun()
        if st.button(
            "Study Notes",
            key="nav_notes",
            use_container_width=True,
            type="primary" if current == "notes" else "secondary",
        ):
            st.session_state.current_page = "notes"
            st.rerun()
        if st.button(
            "Question Bank",
            key="nav_question_bank",
            use_container_width=True,
            type="primary" if current == "question_bank" else "secondary",
        ):
            st.session_state.current_page = "question_bank"
            st.rerun()
        if st.button(
            "Revise AI",
            key="nav_revision",
            use_container_width=True,
            type="primary" if current == "revision" else "secondary",
        ):
            st.session_state.current_page = "revision"
            st.rerun()
        if st.button(
            "Chat History",
            key="nav_chat_history",
            use_container_width=True,
            type="primary" if current == "chat_history" else "secondary",
        ):
            st.session_state.current_page = "chat_history"
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

        st.divider()
        st.markdown(
            "<div style='text-align:center; opacity:0.5; font-size:0.75rem; "
            "padding-top:0.5rem;'>PRODUCED BY #AV</div>",
            unsafe_allow_html=True,
        )
