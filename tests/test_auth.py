"""
Tests — Authentication Module
===============================
Unit tests for password hashing, verification, and user management.
All database operations are run against a temporary in-memory SQLite DB.
"""


import pytest

from app.auth import hash_password, signup, verify_password
from app.database import add_user, get_user, init_db

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    """
    Redirect all database operations to a temporary file for each test.
    Automatically used by all tests in this module.
    """
    db_file = str(tmp_path / "test_users.db")

    # Patch settings to use the temp DB path
    import config.settings as cfg_module

    monkeypatch.setattr(cfg_module.settings, "database_path", db_file)

    # Bootstrap the schema
    init_db(db_file)
    yield db_file


# =============================================================================
# Password Hashing Tests
# =============================================================================


class TestPasswordHashing:

    def test_hash_password_returns_string(self):
        hashed = hash_password("MySecurePass123")
        assert isinstance(hashed, str)

    def test_hash_is_not_plaintext(self):
        password = "MySecurePass123"
        hashed = hash_password(password)
        assert hashed != password

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt uses a random salt — hashes must not be equal."""
        h1 = hash_password("SamePassword")
        h2 = hash_password("SamePassword")
        assert h1 != h2

    def test_verify_correct_password(self):
        hashed = hash_password("CorrectHorseBattery")
        assert verify_password("CorrectHorseBattery", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("CorrectHorseBattery")
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password("SomePassword")
        assert verify_password("", hashed) is False


# =============================================================================
# Signup Tests
# =============================================================================


class TestSignup:

    def test_signup_success(self):
        success, msg = signup("testuser", "password123")
        assert success is True
        assert "testuser" in msg

    def test_signup_duplicate_username(self):
        signup("duplicateuser", "pass1234")
        success, msg = signup("duplicateuser", "otherpass")
        assert success is False
        assert "taken" in msg.lower() or "already" in msg.lower()

    def test_signup_short_username(self):
        success, msg = signup("ab", "password123")
        assert success is False
        assert "3 characters" in msg

    def test_signup_short_password(self):
        success, msg = signup("validuser", "12345")
        assert success is False
        assert "6 characters" in msg

    def test_signup_with_email(self):
        success, msg = signup("emailuser", "password123", email="test@example.com")
        assert success is True
        row = get_user("emailuser")
        assert row["email"] == "test@example.com"


# =============================================================================
# Database Tests
# =============================================================================


class TestDatabase:

    def test_get_nonexistent_user_returns_none(self):
        assert get_user("ghost_user") is None

    def test_add_and_retrieve_user(self):
        hashed = hash_password("TestPass")
        add_user("newuser", hashed, "new@example.com")
        row = get_user("newuser")
        assert row is not None
        assert row["username"] == "newuser"
        assert row["role"] == "user"
        assert row["report_count"] == 0

    def test_user_role_defaults_to_user(self):
        hashed = hash_password("TestPass")
        add_user("roleuser", hashed)
        row = get_user("roleuser")
        assert row["role"] == "user"
