import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from os import getenv

load_dotenv()


# Configure email settings
SMTP_SERVER = getenv("SMTP_SERVER")
SMTP_PORT = getenv("SMTP_PORT")
EMAIL_ADDRESS = getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")  

def send_email(subject, body, recipient):
    try:
        # Create email
        msg = EmailMessage()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.set_content(body)
        
        # Connect to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()  # Start TLS encryption
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Log in
            smtp.send_message(msg)  # Send email
            print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
if __name__ == "__main__":
    subject = "Hello from Python"
    body = "This is a test email sent using Python."
    recipient = "rmoridi30@gmail.com"  # Replace with recipient email
    send_email(subject, body, recipient)
