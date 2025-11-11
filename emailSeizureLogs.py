# emailSeizureLogs.py
import smtplib
from email.message import EmailMessage
import os
from config import GMAIL_PASSCODE_FOR_AUTOMATION

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

USERNAME = "tristanshomeoperationalrepo@gmail.com"
PASSWORD = GMAIL_PASSCODE_FOR_AUTOMATION
TO = "kkhoots1@gmail.com"

def send_seizure_email(file_path="seizures.csv"):
    # Create email
    msg = EmailMessage()
    msg["Subject"] = "Seizures Data File"
    msg["From"] = USERNAME
    msg["To"] = TO
    msg.set_content(
        "Hey my love,\n\n"
        "I’m so sorry you had an episode. Don’t worry — it’s been logged safely, "
        "and I’ve attached the file here for you.\n\n"
        "Always here for you 💖\n\n"
        "- THOR (Tristan's Home Operational Repository 🤖)"
    )

    # Attach the CSV
    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="csv",
            filename=os.path.basename(file_path)
        )

    # Send email
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(USERNAME, PASSWORD)
        smtp.send_message(msg)
