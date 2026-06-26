import smtplib
from email.message import EmailMessage

# --- FILL THESE IN ---
SENDER_EMAIL = "mandaltanisha3@gmail.com"
SENDER_PASSWORD = "jypuhewigmhvmyaf" 
ROAD_DEPT_EMAIL = "mandaltanisha3@gmail.com" # Send to yourself to test!

msg = EmailMessage()
msg['Subject'] = "InfraVision Email Test"
msg['From'] = SENDER_EMAIL
msg['To'] = ROAD_DEPT_EMAIL
msg.set_content("If you receive this, your Python SMTP is working perfectly!")

try:
    print("Attempting to connect to Gmail...")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
    print("✅ SUCCESS! Check your inbox.")
except Exception as e:
    print(f"❌ FAILED! Here is the exact error: {e}")