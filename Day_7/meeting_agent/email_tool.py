import os
import smtplib
from email.message import EmailMessage
from typing import Optional


class EmailSender:
    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() in {"true", "1", "yes"}

        if not self.host or not self.username or not self.password:
            raise ValueError(
                "SMTP_HOST, SMTP_USERNAME, and SMTP_PASSWORD must be configured in the environment."
            )

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        sender: Optional[str] = None,
    ) -> None:
        if not sender:
            sender = os.getenv("EMAIL_DEFAULT_SENDER")

        if not sender:
            raise ValueError("Sender email address must be provided or EMAIL_DEFAULT_SENDER must be configured.")

        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            if self.use_tls:
                smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)
