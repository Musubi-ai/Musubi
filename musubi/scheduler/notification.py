import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class Notify:
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

