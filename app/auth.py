"""
InfraVision AI — Authentication Module
=======================================
Handles user registration, login, session management, and logout.
Uses bcrypt for secure password hashing (replaces plain SHA-256).

Session State Keys:
    logged_in (bool)   — whether the user is authenticated
    username  (str)    — the logged-in username
    user_role (str)    — 'user' or 'admin'
"""

import logging

import bcrypt
import streamlit as st

from app.database import add_user, get_user

logger = logging.getLogger(__name__)


# =============================================================================
# Password Utilities
# =============================================================================


def hash_password(password: str) -> str:
    """
    Hash a plaintext password with bcrypt.

    Args:
        password: Plaintext password string.

    Returns:
        UTF-8 decoded bcrypt hash string.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        password: Plaintext password to verify.
        hashed:   Stored bcrypt hash string.

    Returns:
        True if the password matches; False otherwise.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# =============================================================================
# Session Management
# =============================================================================


def init_session() -> None:
    """Initialize Streamlit session state keys with safe defaults."""
    defaults = {
        "logged_in": False,
        "username": "",
        "user_role": "user",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login(username: str, password: str) -> bool:
    """
    Authenticate a user against the database.

    Args:
        username: Username string.
        password: Plaintext password string.

    Returns:
        True if authentication succeeds; False otherwise.
    """
    row = get_user(username)
    if row is None:
        logger.warning("Login attempt for unknown user '%s'.", username)
        return False

    if verify_password(password, row["password"]):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_role"] = row["role"]
        logger.info("User '%s' logged in successfully.", username)
        return True

    logger.warning("Failed login attempt for user '%s'.", username)
    return False


def logout() -> None:
    """Clear session state and log the user out."""
    username = st.session_state.get("username", "unknown")
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["user_role"] = "user"
    logger.info("User '%s' logged out.", username)
    st.rerun()


def signup(username: str, password: str, email: str = "") -> tuple[bool, str]:
    """
    Register a new user.

    Args:
        username: Desired username (must be unique).
        password: Plaintext password.
        email:    Optional email address.

    Returns:
        (success: bool, message: str)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    hashed = hash_password(password)
    success = add_user(username, hashed, email)
    if success:
        logger.info("New user registered: '%s'.", username)
        return True, f"Account created for **{username}**! Please log in."
    return False, f"Username **{username}** is already taken. Choose another."


# =============================================================================
# Auth UI Renderers
# =============================================================================


def render_login_page() -> None:
    """Render the Login form and handle submission."""
    st.markdown(
        "<h2 style='text-align:center;'>🔐 Sign In</h2>",
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.warning("Please fill in both fields.")
            return
        if login(username, password):
            st.success(f"Welcome back, **{username}**! 🎉")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")


def render_signup_page() -> None:
    """Render the Sign Up form and handle submission."""
    st.markdown(
        "<h2 style='text-align:center;'>📝 Create Account</h2>",
        unsafe_allow_html=True,
    )

    with st.form("signup_form", clear_on_submit=True):
        new_username = st.text_input("Username", placeholder="Choose a username (min 3 chars)")
        new_email = st.text_input("Email (optional)", placeholder="your@email.com")
        new_password = st.text_input(
            "Password", type="password", placeholder="At least 6 characters"
        )
        confirm_password = st.text_input(
            "Confirm Password", type="password", placeholder="Repeat your password"
        )
        submitted = st.form_submit_button("Create Account", use_container_width=True)

    if submitted:
        if new_password != confirm_password:
            st.error("❌ Passwords do not match.")
            return
        success, message = signup(new_username, new_password, new_email)
        if success:
            st.success(message)
        else:
            st.error(message)
