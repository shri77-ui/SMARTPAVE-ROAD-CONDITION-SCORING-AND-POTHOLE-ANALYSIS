import smtplib
from email.message import EmailMessage
import os

EMAIL = "shri97450@gmail.com"
PASSWORD = "nvvcrlgvyxtcravx"

def send_email(image_path):
    if not os.path.exists(image_path):
        print("❌ Image not found, email not sent")
        return

    msg = EmailMessage()
    msg["Subject"] = "🚨 Road Damage Detected"
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg.set_content("Pothole or crack detected. See attached image.")

    with open(image_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename="alert.jpg"
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
            print("✅ Email sent successfully")
    except Exception as e:
        print("❌ Email error:", e)


