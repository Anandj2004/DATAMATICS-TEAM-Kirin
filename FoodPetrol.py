import imaplib
import email
from email.header import decode_header
import os
import pytesseract
from PIL import Image
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration Setup
username = 'your-email@gmail.com' # username
password = 'your-password'# password for authentication
imap_url = 'imap.gmail.com' # https://imap.gmail.com
attachment_dir = 'path/to/save/attachments' # path to attachment

# Connect to the Gmail
mail = imaplib.IMAP4_SSL(imap_url)
mail.login(username, password) 
mail.select('inbox')

# Search for specific emails
type, data = mail.search(None, 'FROM', '"your-email@gmail.com"')
mail_ids = data[0].split()

# Fetch and process the emails
for mail_id in mail_ids:
    typ, data = mail.fetch(mail_id, '(RFC822)')
    raw_email = data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

# Download attachments
for part in email_message.walk():
    if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
        continue
    filename = part.get_filename()
    if filename:
        filepath = os.path.join(attachment_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))

            # Extract the data from attachments
            if filepath.endswith('.pdf'):
                # Implement the PDF extraction logic
                pass
            elif any(filepath.endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                text = pytesseract.image_to_string(Image.open(filepath))
                # Parse the text to extract the receipt details from the attachments
                # Example: Use regex or string methods to find the relevant data

# Insert data into Google Form
form_url = 'https://docs.google.com/forms/d/e/your-form-id/formResponse'
form_data = {
    'entry.field_id_for_data': 'extracted_date',
    'entry.field_id_for_number': 'extracted_number',
    # Add other fields
}
response = requests.post(form_url, data=form_data)

# Send email notification
sender_email = "your-email@gmail.com"
receiver_email = "your-email@gmail.com"
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Reciept Details"
body = "Here are the details of the processed receipts:..."
message.attach(MIMEText(body, "plain"))
text = message.as_string()

# SMTP server configuration
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(username, password)
server.sendmail(sender_email, receiver_email, text)
server.quit()



