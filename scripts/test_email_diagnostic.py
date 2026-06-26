"""
InfraVision AI — Email Diagnostic Tool
Run this script to diagnose email configuration issues.
Usage: python scripts/test_email_diagnostic.py
"""

import os
import smtplib
import sys

# Load .env
try:
    from dotenv import load_dotenv

    load_dotenv()
    print("[OK]  python-dotenv loaded .env file")
except ImportError:
    print("[WARN] python-dotenv not installed. Reading raw env vars only.")

# ── Read config ────────────────────────────────────────────────────────────
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
ROAD_DEPT_EMAIL = os.getenv("ROAD_DEPT_EMAIL", "")

print("\n=== Environment Variable Status ===")
print(f"  SENDER_EMAIL    : {SENDER_EMAIL or 'NOT SET'}")
print(
    f"  SENDER_PASSWORD : {'*' * len(SENDER_PASSWORD) + f' ({len(SENDER_PASSWORD)} chars)' if SENDER_PASSWORD else 'NOT SET'}"
)
print(f"  ROAD_DEPT_EMAIL : {ROAD_DEPT_EMAIL or 'NOT SET'}")

# ── Validate ───────────────────────────────────────────────────────────────
errors = []
if not SENDER_EMAIL:
    errors.append("SENDER_EMAIL is empty")
if not SENDER_PASSWORD:
    errors.append("SENDER_PASSWORD is empty")
if len(SENDER_PASSWORD.replace(" ", "")) not in (16, 0):
    errors.append(
        f"SENDER_PASSWORD has {len(SENDER_PASSWORD.replace(' ', ''))} chars — expected 16"
    )
if not ROAD_DEPT_EMAIL:
    errors.append("ROAD_DEPT_EMAIL is empty")

if errors:
    print("\n[FAIL] Configuration errors found:")
    for e in errors:
        print(f"  - {e}")
    print("\nFix your .env file and re-run this script.")
    sys.exit(1)

print("\n[OK]  All environment variables are set.")

# ── Test SMTP connection ───────────────────────────────────────────────────
print("\n=== SMTP Connection Test ===")
print("  Connecting to smtp.gmail.com:465 ...")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        print("  [OK]  Connected to Gmail SMTP server")
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD.replace(" ", ""))
        print("  [OK]  Authentication successful")
except smtplib.SMTPAuthenticationError as e:
    print(f"  [FAIL] Authentication error: {e}")
    print("\n  Common causes:")
    print("  1. You used your normal Gmail password instead of an App Password")
    print("  2. The App Password has spaces — remove them in .env")
    print("  3. 2-Step Verification is NOT enabled on your Google account")
    print("  4. The App Password was revoked — generate a new one")
    print("  => Go to: https://myaccount.google.com/apppasswords")
    sys.exit(1)
except smtplib.SMTPConnectError as e:
    print(f"  [FAIL] Connection failed: {e}")
    print("  => Check your internet connection")
    sys.exit(1)
except Exception as e:
    print(f"  [FAIL] Unexpected error: {e}")
    sys.exit(1)

# ── Send test email ────────────────────────────────────────────────────────
print(f"\n=== Sending Test Email to: {ROAD_DEPT_EMAIL} ===")

from email.mime.multipart import MIMEMultipart  # noqa: E402
from email.mime.text import MIMEText  # noqa: E402

msg = MIMEMultipart("alternative")
msg["Subject"] = "InfraVision AI — Test Email (Diagnostic)"
msg["From"] = SENDER_EMAIL
msg["To"] = ROAD_DEPT_EMAIL

html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f5f7fa;padding:20px;">
  <div style="max-width:500px;margin:0 auto;background:#fff;border-radius:12px;
               padding:30px;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <h2 style="color:#1e3a5f;">&#x1F6A7; InfraVision AI — Email Test</h2>
    <p>This is a <strong>diagnostic test email</strong> from your InfraVision AI system.</p>
    <p>If you received this, your email configuration is working correctly!</p>
    <hr style="border:1px solid #e2e8f0;"/>
    <p style="color:#64748b;font-size:13px;">
      Sent from: <strong>{SENDER_EMAIL}</strong><br/>
      Recipient: <strong>{ROAD_DEPT_EMAIL}</strong>
    </p>
  </div>
</body></html>
"""
msg.attach(MIMEText(html, "html"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD.replace(" ", ""))
        smtp.send_message(msg)
    print("  [OK]  Test email sent successfully!")
    print(f"\n  Check inbox: {ROAD_DEPT_EMAIL}")
    print("  Also check Spam/Junk folder if not in inbox.")
except Exception as e:
    print(f"  [FAIL] Failed to send: {e}")
    sys.exit(1)

print("\n=== All checks passed! Your email setup is working. ===")
