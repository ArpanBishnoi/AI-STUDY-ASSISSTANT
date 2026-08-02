import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_upload_page():
    st.title("Upload PDF")
    st.caption("Add a new PDF to your library. Text is extracted on the server.")

    headers = get_auth_headers()

    uploaded = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Text is extracted on the server after upload.",
    )

    if uploaded is not None:
        st.caption(f"Selected: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

        if st.button("Upload PDF", type="primary", use_container_width=True):
            with st.spinner("Uploading and extracting text..."):
                try:
                    result = api_client.upload_pdf(
                        headers, uploaded.getvalue(), uploaded.name
                    )
                    st.success(result.get("message", "PDF uploaded successfully."))
                    st.session_state.current_page = "library"
                    st.rerun()
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
