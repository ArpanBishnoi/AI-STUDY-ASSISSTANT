import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_ask_page():
    st.title("Ask a Question")
    st.caption("Ask questions about your active PDF and review past Q&A.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    _render_ask_form(headers)
    st.divider()
    _render_chat_history(headers)


def _render_ask_form(headers: dict):
    st.subheader("Ask a new question")
    question = st.text_area(
        "Your question",
        placeholder="e.g. What is the main idea of chapter 2?",
        height=120,
    )

    if st.button("Ask", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Thinking... this may take a moment."):
            try:
                result = api_client.ask_question(
                    st.session_state.pdf_id, question.strip(), headers
                )
                answer = result.get("THE ANSWER OF YOUR QUESTION")
                if answer:
                    st.success("Answer:")
                    st.markdown(answer)
                else:
                    st.warning("No answer was returned.")
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))


def _render_chat_history(headers: dict):
    st.subheader("Chat history")

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
        st.info("No questions asked yet for this PDF.")
        return

    st.caption(f"{len(history)} question(s) asked")
    for entry in reversed(history):
        entry_id, user_id, pdf_id, question, answer = (
            entry[0],
            entry[1],
            entry[2],
            entry[3],
            entry[4],
        )
        with st.expander(f"Q: {question[:80]}{'…' if len(question) > 80 else ''}"):
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
