import os

import resend
from dotenv import load_dotenv


# Load environment variables from backend/.env
load_dotenv()


class EmailService:
    """Send transactional emails using Resend."""

    def __init__(self):
        api_key = os.getenv("RESEND_API_KEY")

        if not api_key:
            raise RuntimeError(
                "RESEND_API_KEY is missing. "
                "Configure it in your backend .env file."
            )

        self.sender = os.getenv(
            "EMAIL_FROM",
            "onboarding@resend.dev",
        )

        resend.api_key = api_key

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> str:
        """
        Send an email and return the provider's email ID.
        Raise an exception if sending fails.
        """

        params = {
            "from": self.sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        if text_content:
            params["text"] = text_content

        response = resend.Emails.send(params)

        # Resend returns the email ID in its response.
        if isinstance(response, dict):
            email_id = response.get("id")
        else:
            email_id = getattr(response, "id", None)

        if not email_id:
            raise RuntimeError(
                "Resend did not return an email ID."
            )

        return email_id