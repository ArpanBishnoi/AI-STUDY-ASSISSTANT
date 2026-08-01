import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_library_page():
    st.title("My Library")
    st.caption("Upload PDFs and manage your study materials.")

    headers = get_auth_headers()

    _render_upload_section(headers)
    st.divider()
    _render_pdf_list(headers)


def _render_upload_section(headers: dict):
    st.subheader("Upload PDF")
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
                    result = api_client.upload_pdf(headers, uploaded.getvalue(), uploaded.name)
                    st.success(result.get("message", "PDF uploaded successfully."))
                    st.rerun()
                except api_client.APIError as exc:
                    _handle_api_error(exc)
                except Exception as exc:
                    if api_client.is_connection_error(exc):
                        st.error(_backend_unreachable_message())
                    else:
                        st.error(str(exc))


def _render_pdf_list(headers: dict):
    st.subheader("Your PDFs")

    try:
        pdfs = api_client.get_my_pdfs(headers)
    except api_client.APIError as exc:
        _handle_api_error(exc)
        return
    except Exception as exc:
        if api_client.is_connection_error(exc):
            st.error(_backend_unreachable_message())
        else:
            st.error(str(exc))
        return

    if not pdfs:
        st.info("No PDFs yet. Upload your first study material above.")
        return

    st.caption(f"{len(pdfs)} PDF(s) in your library")

    for pdf in pdfs:
        pdf_id, title, uploaded_at = pdf[0], pdf[1], pdf[2]
        _render_pdf_card(pdf_id, title, uploaded_at, headers)


def _render_pdf_card(pdf_id: int, title: str, uploaded_at, headers: dict):
    is_active = st.session_state.pdf_id == pdf_id
    label = f"{'📌 ' if is_active else '📄 '}{title}"

    with st.expander(label, expanded=is_active):
        st.write(f"**ID:** {pdf_id}")
        st.write(f"**Uploaded:** {uploaded_at}")

        col_open, col_details = st.columns(2)

        with col_open:
            if st.button("Set as active PDF", key=f"open_{pdf_id}", use_container_width=True):
                st.session_state.pdf_id = pdf_id
                st.toast(f"Active PDF: {title}")
                st.rerun()

        with col_details:
            if st.button("View details", key=f"details_{pdf_id}", use_container_width=True):
                st.session_state[f"show_details_{pdf_id}"] = True

        if st.session_state.get(f"show_details_{pdf_id}"):
            try:
                details = api_client.get_pdf(pdf_id, headers)
                if details:
                    st.json(
                        {
                            "id": details[0],
                            "title": details[1],
                            "file_path": details[2],
                            "uploaded_at": str(details[3]),
                        }
                    )
                else:
                    st.warning("PDF details not found.")
            except api_client.APIError as exc:
                _handle_api_error(exc)

        st.markdown("**Rename**")
        new_title = st.text_input(
            "New title",
            value=title,
            key=f"rename_input_{pdf_id}",
            label_visibility="collapsed",
        )
        if st.button("Save rename", key=f"rename_{pdf_id}", use_container_width=True):
            if not new_title.strip():
                st.warning("Title cannot be empty.")
            elif new_title.strip() == title:
                st.info("Title unchanged.")
            else:
                try:
                    result = api_client.rename_pdf(pdf_id, new_title.strip(), headers)
                    st.success(result.get("message", "PDF renamed."))
                    st.rerun()
                except api_client.APIError as exc:
                    _handle_api_error(exc)

        if st.button(
            "Delete PDF",
            key=f"delete_{pdf_id}",
            type="secondary",
            use_container_width=True,
        ):
            st.session_state[f"confirm_delete_{pdf_id}"] = True

        if st.session_state.get(f"confirm_delete_{pdf_id}"):
            st.warning(f"Delete **{title}**? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete", key=f"confirm_yes_{pdf_id}", type="primary"):
                    try:
                        api_client.delete_pdf(pdf_id, headers)
                        if st.session_state.pdf_id == pdf_id:
                            st.session_state.pdf_id = None
                        st.session_state.pop(f"confirm_delete_{pdf_id}", None)
                        st.success("PDF deleted.")
                        st.rerun()
                    except api_client.APIError as exc:
                        _handle_api_error(exc)
            with c2:
                if st.button("Cancel", key=f"confirm_no_{pdf_id}"):
                    st.session_state.pop(f"confirm_delete_{pdf_id}", None)
                    st.rerun()


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
