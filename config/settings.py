"""
InfraVision AI — Centralized Configuration
==========================================
Reads all settings from environment variables (via .env file).
Uses pydantic-settings for validation and type safety.

Usage:
    from config.settings import settings
    print(settings.sender_email)
"""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment variables.
    Defaults are provided for non-sensitive configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Email ──────────────────────────────────────────────────────────────
    sender_email: str = Field(
        default="your_email@gmail.com",
        description="Gmail address used to send automated reports.",
    )
    sender_password: str = Field(
        default="",
        description="Gmail App Password (not your regular password).",
    )
    road_dept_email: str = Field(
        default="authority@example.com",
        description="Recipient email — road department or authority.",
    )

    # ── Detection ──────────────────────────────────────────────────────────
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="YOLO detection confidence threshold.",
    )
    critical_area_ratio: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Pothole-to-frame area ratio to flag as critical.",
    )
    model_path: str = Field(
        default="models/best.pt",
        description="Path to the YOLO model weights file.",
    )

    # ── Database ───────────────────────────────────────────────────────────
    database_path: str = Field(
        default="data/users.db",
        description="SQLite database file path.",
    )

    # ── GPS ───────────────────────────────────────────────────────────────
    default_latitude: float = Field(
        default=17.3913,
        description="Fallback latitude when device GPS is unavailable.",
    )
    default_longitude: float = Field(
        default=78.3206,
        description="Fallback longitude when device GPS is unavailable.",
    )

    # ── App ───────────────────────────────────────────────────────────────
    app_name: str = "InfraVision AI"
    app_version: str = "2.0.0"
    debug: bool = False

    @field_validator("model_path")
    @classmethod
    def model_must_exist(cls, v: str) -> str:
        """Warn if model file is missing — do not crash at import time."""
        if not Path(v).exists():
            import warnings

            warnings.warn(
                f"Model file not found at '{v}'. "
                "Download best.pt and place it in the models/ directory.",
                UserWarning,
                stacklevel=2,
            )
        return v


# Singleton instance — import this throughout the app
settings = Settings()
