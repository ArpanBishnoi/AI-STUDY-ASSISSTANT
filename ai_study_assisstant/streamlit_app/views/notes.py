import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_notes_page():
    st.title("Study Notes")
    st.caption("Generate detailed, well-organized study notes from your active PDF.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    if st.button("Generate Notes", type="primary", use_container_width=True):
        with st.spinner("Generating notes... this may take a moment."):
            try:
                result = api_client.get_notes(st.session_state.pdf_id, headers)
                notes = result.get("Your notes are")
                if notes:
                    st.session_state.notes_result = notes
                else:
                    st.warning("No notes were returned.")
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))

    notes = st.session_state.get("notes_result")
    if notes:
        st.divider()
        st.subheader("Your Notes")
        st.markdown(notes)


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
