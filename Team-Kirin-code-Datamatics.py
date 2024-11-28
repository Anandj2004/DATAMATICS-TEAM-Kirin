import imaplib
import email
import os
import smtplib
from email.mime.text import MIMEText
from email.header import decode_header

def connect_to_email(email_user, email_pass):
    """Connect to the Gmail server and return the mail object."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        return mail
    except Exception as e:
        print(f"Failed to connect to email server: {e}")
        return None

def download_attachments(mail):
    """Download attachments from emails with 'Receipt' in the subject."""
    try:
        mail.select("inbox")
        status, messages = mail.search(None, '(SUBJECT "Receipt")')
        email_ids = messages[0].split()

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():
                        if part.get_content_maintype() == "multipart":
                            continue
                        if part.get("Content-Disposition") is None:
                            continue
                        filename = part.get_filename()
                        if filename:
                            with open(filename, "wb") as f:
                                f.write(part.get_payload(decode=True))
        print("Attachments downloaded successfully.")
    except Exception as e:
        print(f"Failed to download attachments: {e}")

def send_email_notification(to_email, subject, body):
    """Send an email notification with the specified subject and body."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.sendmail(os.getenv("EMAIL_USER"), to_email, msg.as_string())
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email notification: {e}")

# Example usage
if __name__ == "__main__":
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    mail = connect_to_email(email_user, email_pass)
    if mail:
        download_attachments(mail)
        send_email_notification(
            "finance-team@example.com",
            "Receipt Summary",
            "Vendor: ABC Store\nTotal Amount: $123.45"
        )
        mail.logout()
