"""
File: packages/shared/notifications.py
Layer: Shared / Integration / Communication
Purpose: Outbound alerting via SMTP for critical human-in-the-loop triggers.
Problem Solved: Ensures immediate attention for high-priority incidents that the autonomous loop cannot resolve.
Interaction: Used by the Human agent to notify on-call SREs.
Dependencies: smtplib, email.mime
Inputs: Subject line, email body, and destination
Outputs: Boolean status of the delivery effort
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_sre_alert(subject: str, body: str, to_email: str = "mohammedsalmanj@outlook.com") -> bool:
    """
    Utility to send SRE alerts via standard SMTP protocols. 
    Fallbacks to logging if credentials are missing to ensure no total failure in silent environments.
    
    Args:
        subject (str): The email subject line.
        body (str): The email content (plain text).
        to_email (str): Destination address (default: mohammedsalmanj@outlook.com).
    Returns:
        bool: True if sent or successfully logged; False on SMTP failure.
    """
    print(f"📧 [EMAIL ALERT] To: {to_email} | Subject: {subject}")
    
    # 1. Credential Retrieval from Environment
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    # 2. Production SMTP Flow
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
            print(f"❌ Failed to deliver real-time SRE email: {e}")
            return False
    else:
        # 3. Development/Disconnected Fallback
        print("ℹ️ SMTP settings not found in .env. Falling back to log-only notification.")
        return True
