import smtplib
from email.message import EmailMessage

from notify import config


class BaseSender:
    """Интерфейс отправителя. Реализации: EmailSender."""

    def send(self, to, subject, body):
        raise NotImplementedError


class EmailSender(BaseSender):
    def send(self, to, subject, body):
        msg = EmailMessage()
        msg["From"] = config.FROM_ADDR
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
            smtp.send_message(msg)


def make_sender(kind="email"):
    return {"email": EmailSender}[kind]()
