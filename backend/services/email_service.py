import os
import smtplib

from email.message import EmailMessage


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)

FRONTEND_BASE_URL = os.getenv(
    "FRONTEND_BASE_URL",
    "http://localhost:3000"
)


def send_verification_email(
    to_email: str,
    token: str
):
    verify_url = (
        f"{FRONTEND_BASE_URL}/verify-email?token={token}"
    )

    subject = "Verify your Pantry account"

    text_body = (
        f"Welcome to Pantry!\n\n"
        f"Please verify your email by clicking the link below:\n"
        f"{verify_url}\n\n"
        "If you did not create this account, you can ignore this message."
    )

    html_body = (
        f"<p>Welcome to Pantry!</p>"
        f"<p>Please verify your email by clicking the link below:</p>"
        f"<p><a href=\"{verify_url}\">Verify your email</a></p>"
        f"<p>If you did not create this account, you can ignore this message.</p>"
    )

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print(f"[email verification disabled] token for {to_email}: {token}")
        return

    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = FROM_EMAIL
    message["To"] = to_email

    message.set_content(text_body)

    message.add_alternative(
        html_body,
        subtype="html"
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()

        smtp.login(
            SMTP_USER,
            SMTP_PASS
        )

        smtp.send_message(message)