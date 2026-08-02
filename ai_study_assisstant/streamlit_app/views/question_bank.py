import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_question_bank_page():
    st.title("Probable Question Bank")
    st.caption("Generate likely exam questions from your active PDF to practice with.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    if st.button("Generate Questions", type="primary", use_container_width=True):
        with st.spinner("Generating probable questions... this may take a moment."):
            try:
                result = api_client.get_question_bank(st.session_state.pdf_id, headers)
                questions = result.get("Most probabable questions")
                if questions:
                    st.session_state.question_bank_result = questions
                else:
                    st.warning("No questions were returned.")
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))

    questions = st.session_state.get("question_bank_result")
    if questions:
        st.divider()
        st.subheader("Probable Exam Questions")
        st.markdown(questions)


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
