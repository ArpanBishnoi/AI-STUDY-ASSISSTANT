import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_explain_page():
    st.title("Explain AI")
    st.caption("Get a simple, step-by-step explanation of any topic from your active PDF.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    question = st.text_area(
        "What would you like explained?",
        placeholder="e.g. Explain how photosynthesis works",
        height=120,
    )

    if st.button("Explain", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a topic or question.")
            return

        with st.spinner("Explaining... this may take a moment."):
            try:
                result = api_client.explain_concept(
                    st.session_state.pdf_id, question.strip(), headers
                )
                explanation = result.get("Your results are")
                if explanation:
                    st.markdown(explanation)
                else:
                    st.warning("No explanation was returned.")
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))


def _handle_api_error(exc: api_client.APIError):
    if exc.status_code == 401:
        logout()
        st.error("Session expired. Please log in again.")
        st.rerun()
    else:
        st.error(str(exc))


def _backend_unreachable_message() -> str:
    return (
        "Could not reach the backend. Start FastAPI first:\n\n"
        "`uvicorn database:app --reload` from the `backend` folder."
    )
