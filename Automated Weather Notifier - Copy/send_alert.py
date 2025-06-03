# Import required libraries
import smtplib                         # For sending emails
import re                              # For validating email format
import os                              # For loading environment variables
from twilio.rest import Client         # For sending SMS with Twilio
from email.mime.text import MIMEText   # For writing plain text email
from email.mime.multipart import MIMEMultipart  # For formatting the email
from dotenv import load_dotenv         # To load secrets from a .env file

# Load .env file
load_dotenv()


class AlertSender:
    """Communication System: Sends SMS using Twilio and falls back to Email if needed"""
    # Initialize with Twilio and Gmail credentials
    def __init__(self):
        self.twilio_client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')

    # Check if an email address has the correct format
    def is_valid_email(self, email):
        pattern = r"[^@]+@[^@]+\.[^@]+"
        return re.match(pattern, email) is not None

    # Send SMS using Twilio
    def send_sms(self, to_phone, message):
        try:
            if not self.twilio_number:
                #Checks if twilio number exists
                raise ValueError("Twilio 'from' number is not set. Check your .env file for TWILIO_PHONE_NUMBER.")
            sms = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_phone
            )
            print('SMS sent successfully.')
            return True, sms.sid #--> Message Id of the twilio message object
        except Exception as e:
            print(f'SMS sending failed: {e}')
            return False, str(e)
        
        
    # Send Email using Gmail SMTP
    def send_email(self, to_email, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            print('Email sent successfully.')
            return True, "Email sent"
        except Exception as e:
            print(f'Email sending failed: {e}')
            return False, str(e)

    # Unified function: try SMS first, then fallback to email if SMS fails
    def send_alert(self, phone, email, message):
        sms_success, sms_response = self.send_sms(phone, message)
        if sms_success:
            return 'SMS', sms_response

        # SMS failed, so fallback to email
        if self.is_valid_email(email):
            email_success, email_response = self.send_email(
                email,
                'Severe Weather Alert',
                message
            )
            if email_success:
                return 'Email', email_response
            else:
                return 'Failed', email_response
        else:
            return 'Failed', 'Invalid email address'