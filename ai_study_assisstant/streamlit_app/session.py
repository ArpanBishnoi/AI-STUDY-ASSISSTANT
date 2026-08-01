import streamlit as st


def init_session():
    defaults = {
        "access_token": None,
        "user_id": None,
        "authenticated": False,
        "pdf_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login(token: str, user_id: str):
    st.session_state.access_token = token
    st.session_state.user_id = user_id
    st.session_state.authenticated = True


def logout():
    st.session_state.access_token = None
    st.session_state.user_id = None
    st.session_state.authenticated = False
    st.session_state.pdf_id = None


def get_auth_headers() -> dict:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}
