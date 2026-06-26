"""
InfraVision AI — Database Module
=================================
Handles all SQLite database operations with a clean context-manager
interface, proper parameterized queries, and an extended user schema.

Schema:
    userstable(
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,          -- bcrypt hash
        email       TEXT,
        role        TEXT DEFAULT 'user',    -- 'user' | 'admin'
        report_count INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

logger = logging.getLogger(__name__)


def _get_db_path() -> str:
    """Return the DB path from settings (lazy import to avoid circular deps)."""
    from config.settings import settings

    return settings.database_path


@contextmanager
def get_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a SQLite connection and commits on exit,
    or rolls back on exception.

    Args:
        db_path: Optional override for the database file path.

    Yields:
        sqlite3.Connection: An open database connection.
    """
    path = db_path or _get_db_path()
    # Ensure parent directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # enable dict-like row access
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =============================================================================
# Schema Initialization
# =============================================================================


def init_db(db_path: Optional[str] = None) -> None:
    """
    Create the users table if it does not already exist.
    Safe to call on every app start.
    """
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS userstable (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                username     TEXT    UNIQUE NOT NULL,
                password     TEXT    NOT NULL,
                email        TEXT    DEFAULT '',
                role         TEXT    DEFAULT 'user',
                report_count INTEGER DEFAULT 0,
                created_at   TEXT    DEFAULT (datetime('now'))
            )
        """)
    logger.info("Database initialized at '%s'.", db_path or _get_db_path())


# =============================================================================
# User CRUD
# =============================================================================


def add_user(username: str, hashed_password: str, email: str = "") -> bool:
    """
    Insert a new user into the database.

    Args:
        username:        Unique username.
        hashed_password: bcrypt-hashed password string.
        email:           Optional email address.

    Returns:
        True if the user was created; False if the username already exists.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO userstable (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email),
            )
        logger.info("User '%s' registered.", username)
        return True
    except sqlite3.IntegrityError:
        logger.warning("Registration failed — username '%s' already exists.", username)
        return False


def get_user(username: str) -> Optional[sqlite3.Row]:
    """
    Fetch a single user row by username.

    Args:
        username: The username to look up.

    Returns:
        sqlite3.Row if found, None otherwise.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM userstable WHERE username = ?",
            (username,),
        )
        return cursor.fetchone()


def increment_report_count(username: str) -> None:
    """Increment the report counter for a user after a successful detection."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE userstable SET report_count = report_count + 1 WHERE username = ?",
            (username,),
        )
    logger.debug("Report count incremented for user '%s'.", username)


def get_all_users() -> list:
    """Return all users (for admin view). Excludes password hashes."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, username, email, role, report_count, created_at FROM userstable"
        )
        return cursor.fetchall()
