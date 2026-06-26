"""
Tests — Email Service Module
==============================
Unit tests for HTML body generation, report assembly, and error handling.
SMTP is mocked so no real emails are sent during testing.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from app.detection import Severity
from app.gps_service import Coordinates
from app.email_service import _build_html_body, send_report


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def coords():
    return Coordinates(latitude=17.3913, longitude=78.3206)


@pytest.fixture
def dummy_evidence(tmp_path):
    """Create a tiny dummy JPEG evidence file."""
    evidence = tmp_path / "evidence.jpg"
    evidence.write_bytes(b"\xff\xd8\xff" + b"\x00" * 100)  # minimal JPEG header
    return str(evidence)


# =============================================================================
# HTML Body Tests
# =============================================================================

class TestBuildHtmlBody:

    def test_contains_coordinates(self, coords):
        html = _build_html_body(coords, Severity.HIGH)
        assert "17.391300" in html or "17.3913" in html

    def test_contains_maps_link(self, coords):
        html = _build_html_body(coords, Severity.CRITICAL)
        assert "google.com/maps" in html

    def test_contains_severity_label(self, coords):
        for sev in (Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL):
            html = _build_html_body(coords, sev)
            assert sev.value in html

    def test_contains_reporter(self, coords):
        html = _build_html_body(coords, Severity.HIGH, reported_by="TestUser")
        assert "TestUser" in html

    def test_returns_string(self, coords):
        html = _build_html_body(coords, Severity.NONE)
        assert isinstance(html, str)
        assert len(html) > 100

    def test_is_valid_html(self, coords):
        """Basic check that the output starts and ends like HTML."""
        html = _build_html_body(coords, Severity.HIGH).strip()
        assert html.startswith("<!DOCTYPE html>") or html.startswith("<!")
        assert "</html>" in html


# =============================================================================
# send_report Tests
# =============================================================================

class TestSendReport:

    def test_missing_evidence_file_returns_false(self, coords):
        success, msg = send_report(
            evidence_path="/nonexistent/path/evidence.jpg",
            coordinates=coords,
            severity=Severity.HIGH,
        )
        assert success is False
        assert "not found" in msg.lower()

    @patch("app.email_service.smtplib.SMTP_SSL")
    def test_successful_send(self, mock_smtp_cls, coords, dummy_evidence):
        """Mock SMTP so no real email is sent."""
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp

        success, msg = send_report(
            evidence_path=dummy_evidence,
            coordinates=coords,
            severity=Severity.CRITICAL,
            reported_by="pytest",
        )

        assert success is True
        assert "successfully" in msg.lower()
        mock_smtp.login.assert_called_once()
        mock_smtp.send_message.assert_called_once()

    @patch("app.email_service.smtplib.SMTP_SSL")
    def test_smtp_auth_error_returns_false(self, mock_smtp_cls, coords, dummy_evidence):
        import smtplib
        mock_smtp_cls.return_value.__enter__.side_effect = smtplib.SMTPAuthenticationError(
            535, b"Bad credentials"
        )
        success, msg = send_report(
            evidence_path=dummy_evidence,
            coordinates=coords,
            severity=Severity.HIGH,
        )
        assert success is False
        assert "authentication" in msg.lower() or "smtp" in msg.lower()

    @patch("app.email_service.smtplib.SMTP_SSL")
    def test_generic_smtp_error_returns_false(self, mock_smtp_cls, coords, dummy_evidence):
        import smtplib
        mock_smtp_cls.return_value.__enter__.side_effect = smtplib.SMTPException("Connection refused")
        success, msg = send_report(
            evidence_path=dummy_evidence,
            coordinates=coords,
            severity=Severity.CRITICAL,
        )
        assert success is False


# =============================================================================
# Coordinates Tests
# =============================================================================

class TestCoordinates:

    def test_str_representation(self, coords):
        s = str(coords)
        assert "17.3913" in s
        assert "78.3206" in s

    def test_google_maps_url(self, coords):
        url = coords.to_google_maps_url()
        assert "google.com/maps" in url
        assert "17.3913" in url

    def test_to_dict(self, coords):
        d = coords.to_dict()
        assert d["latitude"] == 17.3913
        assert d["longitude"] == 78.3206
