import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_revision_page():
    st.title("Revise AI")
    st.caption("Generate ultra-concise revision notes for a quick 5–10 minute review.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    if st.button("Generate Revision Notes", type="primary", use_container_width=True):
        with st.spinner("Generating revision notes... this may take a moment."):
            try:
                result = api_client.get_revision(st.session_state.pdf_id, headers)
                revision = result.get("Results")
                if revision:
                    st.session_state.revision_result = revision
                else:
                    st.warning("No revision notes were returned.")
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))

    revision = st.session_state.get("revision_result")
    if revision:
        st.divider()
        st.subheader("Quick Revision Notes")
        st.markdown(revision)


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
