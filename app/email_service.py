"""
InfraVision AI — Email Reporting Service
==========================================
Sends rich HTML email reports to the road department with:
  - Styled HTML body (branded, not plain text)
  - Google Maps location link
  - Severity badge in the email
  - Photographic evidence attachment
  - Proper error handling and logging

Usage:
    from app.email_service import send_report
    success, msg = send_report(evidence_path, coordinates, severity)
"""

import logging
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from app.detection import SEVERITY_COLORS, SEVERITY_EMOJIS, Severity
from app.gps_service import Coordinates
from config.settings import settings

logger = logging.getLogger(__name__)


# =============================================================================
# HTML Email Template
# =============================================================================


def _build_html_body(
    coordinates: Coordinates,
    severity: Severity,
    reported_by: str = "InfraVision AI",
) -> str:
    """Build a branded HTML email body for the road department report."""

    color = SEVERITY_COLORS.get(severity, "#607d8b")
    emoji = SEVERITY_EMOJIS.get(severity, "⚠️")
    maps_url = coordinates.to_google_maps_url()

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>InfraVision AI — Road Defect Report</title>
<style>
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f5f7fa;
    margin: 0; padding: 0;
    color: #2d3748;
  }}
  .container {{
    max-width: 600px;
    margin: 30px auto;
    background: #ffffff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }}
  .header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    padding: 32px 40px;
    text-align: center;
  }}
  .header h1 {{
    color: #e2e8f0;
    font-size: 26px;
    margin: 0;
    letter-spacing: 1px;
  }}
  .header p {{
    color: #94a3b8;
    margin: 6px 0 0;
    font-size: 13px;
  }}
  .severity-badge {{
    display: inline-block;
    background: {color};
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    padding: 8px 24px;
    border-radius: 30px;
    margin: 24px auto;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}
  .body {{
    padding: 30px 40px;
  }}
  .info-block {{
    background: #f8fafc;
    border-left: 4px solid {color};
    border-radius: 6px;
    padding: 16px 20px;
    margin: 20px 0;
  }}
  .info-block p {{
    margin: 6px 0;
    font-size: 14px;
  }}
  .info-block strong {{
    color: #1e293b;
  }}
  .map-btn {{
    display: inline-block;
    background: #2563eb;
    color: #ffffff !important;
    text-decoration: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    margin: 10px 0;
  }}
  .evidence-section {{
    margin: 24px 0;
    text-align: center;
  }}
  .evidence-section img {{
    max-width: 100%;
    border-radius: 8px;
    border: 2px solid #e2e8f0;
  }}
  .footer {{
    background: #f1f5f9;
    padding: 20px 40px;
    text-align: center;
    font-size: 12px;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🚧 InfraVision AI</h1>
    <p>Automated Road Defect Detection &amp; Reporting System</p>
  </div>

  <div class="body">
    <p>Dear Road Maintenance Department,</p>
    <p>
      Our AI-powered monitoring system has detected a road defect that requires your
      attention. Full details are provided below.
    </p>

    <div style="text-align:center;">
      <div class="severity-badge">{emoji} Severity: {severity.value}</div>
    </div>

    <div class="info-block">
      <p><strong>📍 GPS Coordinates:</strong> {coordinates}</p>
      <p><strong>🤖 Detected by:</strong> {reported_by}</p>
      <p><strong>✅ Status:</strong> AI-Verified — Action Required</p>
    </div>

    <div style="text-align:center; margin: 20px 0;">
      <a href="{maps_url}" class="map-btn">🗺️ View on Google Maps</a>
    </div>

    <div class="evidence-section">
      <p style="font-weight:600; color:#1e293b;">📸 Photographic Evidence</p>
      <p style="font-size:13px; color:#64748b;">
        See attached image for annotated bounding box evidence.
      </p>
    </div>

    <p style="margin-top:24px;">
      Please review the attached evidence and dispatch a maintenance team at the earliest.
    </p>

    <p>
      Regards,<br/>
      <strong>InfraVision AI Automated Reporting System</strong><br/>
      <span style="font-size:12px; color:#64748b;">v{settings.app_version}</span>
    </p>
  </div>

  <div class="footer">
    <p>This is an automated message. Do not reply to this email.</p>
    <p>InfraVision AI © 2024 — Department of CSE (AI &amp; ML), VJIT</p>
  </div>
</div>
</body>
</html>
"""


# =============================================================================
# Email Sending
# =============================================================================


def send_report(
    evidence_path: str,
    coordinates: Coordinates,
    severity: Severity,
    reported_by: str = "InfraVision AI",
) -> tuple[bool, str]:
    """
    Send an HTML email report with photographic evidence to the road department.

    Args:
        evidence_path:  Path to the JPEG evidence image.
        coordinates:    GPS Coordinates of the detected defect.
        severity:       Severity classification enum value.
        reported_by:    Username or system name for attribution.

    Returns:
        (success: bool, message: str)
    """
    # Validate evidence file exists
    if not Path(evidence_path).exists():
        msg = f"Evidence file not found: '{evidence_path}'"
        logger.error(msg)
        return False, msg

    # Build MIME message
    msg = MIMEMultipart("related")
    msg["Subject"] = (
        f"🚨 [{severity.value.upper()}] Road Defect Detected — {coordinates} | InfraVision AI"
    )
    msg["From"] = settings.sender_email
    msg["To"] = settings.road_dept_email

    # Attach HTML body
    html_body = _build_html_body(coordinates, severity, reported_by)
    msg.attach(MIMEText(html_body, "html"))

    # Attach evidence image
    try:
        with open(evidence_path, "rb") as img_file:
            image_data = img_file.read()
        mime_image = MIMEImage(image_data, _subtype="jpeg", name="pothole_evidence.jpg")
        mime_image.add_header("Content-Disposition", "attachment", filename="pothole_evidence.jpg")
        msg.attach(mime_image)
    except OSError as exc:
        logger.error("Failed to attach evidence image: %s", exc)
        return False, f"Could not attach evidence: {exc}"

    # Send via SMTP SSL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
            smtp.login(settings.sender_email, settings.sender_password)
            smtp.send_message(msg)
        logger.info(
            "Report sent successfully to '%s' [severity=%s, location=%s].",
            settings.road_dept_email,
            severity.value,
            coordinates,
        )
        return True, "Report sent successfully."
    except smtplib.SMTPAuthenticationError:
        msg_err = (
            "SMTP authentication failed. Check SENDER_EMAIL and SENDER_PASSWORD in your .env file."
        )
        logger.error(msg_err)
        return False, msg_err
    except smtplib.SMTPException as exc:
        logger.error("SMTP error: %s", exc)
        return False, f"SMTP error: {exc}"
    except Exception as exc:
        logger.error("Unexpected email error: %s", exc)
        return False, f"Unexpected error: {exc}"
