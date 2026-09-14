"""
Authenticated ownership helpers for JobPilot.
"""
import streamlit as st

def current_user_id():
    # The authentication layer stores the logged-in user in jp_user.
    user = st.session_state.get("jp_user")
    if not user:
        raise RuntimeError("No authenticated user in session. Please log in again.")
    user_id = user.get("id") if isinstance(user, dict) else None
    if user_id is None:
        raise RuntimeError("Authenticated session is missing a user ID. Please log in again.")
    return int(user_id)
