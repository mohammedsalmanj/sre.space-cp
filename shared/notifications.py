import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_sre_alert(subject, body, to_email="mohammedsalmanj@outlook.com"):
    """
    Utility to send SRE alerts. 
    Note: Requires SMTP configuration in .env for production.
    Currently defaults to logging for safety unless SMTP is configured.
    """
    print(f"📧 [EMAIL ALERT] To: {to_email} | Subject: {subject}")
    
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Failed to send real email: {e}")
            return False
    else:
        print("ℹ️ SMTP settings not found in .env. Falling back to log-only notification.")
        return True
