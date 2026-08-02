import streamlit as st

import api_client
from session import login, logout


def render_auth_page():
    st.title("AI Study Assistant")
    st.caption("Upload PDFs, ask questions, revise, and practice for exams.")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        _render_login_form()

    with tab_register:
        _render_register_form()

    st.divider()
    st.markdown(
        "<div style='text-align:center; opacity:0.5; font-size:0.75rem;'>"
        "PRODUCED BY #AV</div>",
        unsafe_allow_html=True,
    )


def _render_login_form():
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
            return

        try:
            data = api_client.login(email.strip(), password)
            token = data["access_token"]
            profile = api_client.get_profile({"Authorization": f"Bearer {token}"})
            login(token, str(profile["user_id"]))
            st.success("Logged in successfully.")
            st.rerun()
        except api_client.APIError as exc:
            if exc.status_code == 401:
                st.error("Invalid email or password.")
            else:
                st.error(str(exc))
        except Exception as exc:
            if api_client.is_connection_error(exc):
                st.error(_backend_unreachable_message())
            else:
                st.error(str(exc))


def _render_register_form():
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="student123")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

    if submitted:
        if not username or not email or not password:
            st.error("Please fill in all fields.")
            return

        try:
            api_client.register(username.strip(), email.strip(), password)
            st.success("Account created. Switch to the Login tab to sign in.")
        except api_client.APIError as exc:
            st.error(str(exc))
        except Exception as exc:
            if api_client.is_connection_error(exc):
                st.error(_backend_unreachable_message())
            else:
                st.error(str(exc))


def _backend_unreachable_message() -> str:
    return (
        "Could not reach the backend. Start FastAPI first:\n\n"
        "`uvicorn database:app --reload` from the `backend` folder."
    )
