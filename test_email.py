import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os

# Add the app directory to sys.path to import settings
sys.path.append(os.getcwd())

from app.core.config import settings

def test_smtp():
    print(f"Testing SMTP with Host: {settings.SMTP_HOST}, User: {settings.SMTP_USER}")
    
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print("Error: SMTP_HOST or SMTP_USER not configured.")
        return

    # Check if password is set (either from config or .env)
    # Since I can't read the user's secret password, I'll ask the user to provide it or verify it's in .env
    password = settings.SMTP_PASSWORD
    if not password:
        print("Error: SMTP_PASSWORD is empty. Please ensure it's set in your .env file.")
        return

    msg = MIMEMultipart()
    msg["Subject"] = "Licencia - Test SMTP"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = settings.SMTP_USER # Send to self for testing

    body = "Ceci est un test de la configuration SMTP pour Licencia."
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(settings.SMTP_USER, password)
            server.sendmail(settings.SMTP_FROM, [settings.SMTP_USER], msg.as_string())
        print("Success: Email sent successfully!")
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    test_smtp()
