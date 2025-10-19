import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class Notify:
    """A helper class for sending notification emails via Gmail.

    This class provides simple email notification functionality using
    Gmail's SMTP server. It supports both single and multiple recipients
    and requires an app password for authentication.

    Args:
        app_password (str, optional): Gmail app password generated from your
            Google account. Required for authentication.
        sender_email (str, optional): The Gmail address used to send the email.
        recipient_email (str, optional): The recipient's email address. If not
            provided, defaults to the sender's email address.
    """
    def __init__(
        self,
        app_password: str = None,
        sender_email: str = None,
        recipient_email: Optional[str] = None,
    ):
        """
        Set up app_password in https://myaccount.google.com/apppasswords.
        """
        self.app_password = app_password
        self.sender_email = sender_email
        if recipient_email is not None:
            self.recipient_email = recipient_email
        else:
            self.recipient_email = self.sender_email

    def send_gmail(
        self,
        subject: str = None,
        body: str = None
    ):
        """Send an email via Gmail SMTP.

        This method creates a plain text email message and sends it using
        Gmail's secure SMTP connection.

        Args:
            subject (str, optional): Subject line of the email.
            body (str, optional): Plain text content of the email body.

        Returns:
            None: The method sends the email and does not return any value.

        Raises:
            smtplib.SMTPAuthenticationError: If authentication with Gmail fails.
            smtplib.SMTPConnectError: If the connection to Gmail SMTP cannot be established.
            Exception: For any other email-sending related errors.
        """
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()

