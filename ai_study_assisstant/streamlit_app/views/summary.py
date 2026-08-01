import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_summary_page():
    st.title("Summarize PDF")
    st.caption("Generate a concise chapter-level summary of your active PDF.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    if st.button("Generate Summary", type="primary", use_container_width=True):
        with st.spinner("Summarizing... this may take a moment."):
            try:
                result = api_client.summarize_pdf(st.session_state.pdf_id, headers)
                summary = result.get(" Your summary")
                if summary:
                    st.markdown(summary)
                else:
                    st.warning("No summary was returned.")
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
