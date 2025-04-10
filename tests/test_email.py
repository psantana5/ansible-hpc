#!/usr/bin/env python3
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "pausantanapi2@gmail.com"
smtp_password = os.environ.get('GMAIL_APP_PASSWORD')
sender = "pausantanapi2@gmail.com"
recipient = "pausantanapi2@gmail.com" 

# Create message
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = "Test Email from HPC Reporting System"

# Add body
body = """
This is a test email from the HPC cluster reporting system.
If you're receiving this, the SMTP configuration is working correctly.

Best regards,
HPC Admin
"""
msg.attach(MIMEText(body, 'plain'))

try:
    # Connect to server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    
    # Send email
    text = msg.as_string()
    server.sendmail(sender, recipient, text)
    print("Email sent successfully!")
    
    # Close connection
    server.quit()
except Exception as e:
    print(f"Error sending email: {e}")