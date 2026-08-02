import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_chat_history_page():
    st.title("Chat History")
    st.caption("All questions and answers for your active PDF.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    try:
        history = api_client.get_chat_history(st.session_state.pdf_id, headers)
    except api_client.APIError as exc:
        _handle_api_error(exc)
        return
    except Exception as exc:
        if api_client.is_connection_error(exc):
            st.error(_backend_unreachable_message())
        else:
            st.error(str(exc))
        return

    if not history:
        st.info("No questions asked yet for this PDF. Use **Ask a Question** to start.")
        return

    st.caption(f"{len(history)} question(s) asked")

    col_search, col_sort = st.columns([3, 1])
    with col_search:
        search = st.text_input(
            "Search questions",
            placeholder="Filter by keyword...",
            key="chat_history_search",
            label_visibility="collapsed",
        )
    with col_sort:
        sort_order = st.selectbox(
            "Sort",
            ["Newest first", "Oldest first"],
            key="chat_history_sort",
            label_visibility="collapsed",
        )

    filtered = history
    if search.strip():
        filtered = [
            e for e in filtered
            if search.strip().lower() in (e[3] or "").lower()
            or search.strip().lower() in (e[4] or "").lower()
        ]

    if sort_order == "Newest first":
        filtered = list(reversed(filtered))

    if not filtered:
        st.warning("No questions match your search.")
        return

    st.caption(f"Showing {len(filtered)} of {len(history)}")

    for entry in filtered:
        entry_id, user_id, pdf_id, question, answer = (
            entry[0], entry[1], entry[2], entry[3], entry[4]
        )
        with st.expander(
            f"Q: {question[:80]}{'…' if len(question) > 80 else ''}"
        ):
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Answer:** {answer}")


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
