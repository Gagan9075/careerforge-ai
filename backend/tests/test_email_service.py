import pytest
from unittest.mock import MagicMock, patch

from app.notifications.email_service import EmailService


# --------------------------------------------------
# Initialization tests
# --------------------------------------------------

@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_email_service_initialization(mock_getenv, mock_resend):
    def getenv_side_effect(key, default=None):
        values = {
            "RESEND_API_KEY": "test_api_key",
            "EMAIL_FROM": "test@example.com",
        }
        return values.get(key, default)

    mock_getenv.side_effect = getenv_side_effect

    service = EmailService()

    assert service.sender == "test@example.com"
    assert mock_resend.api_key == "test_api_key"


@patch("app.notifications.email_service.os.getenv", return_value=None)
def test_email_service_raises_when_api_key_missing(mock_getenv):
    with pytest.raises(RuntimeError, match="RESEND_API_KEY is missing"):
        EmailService()


@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_email_service_uses_default_sender(mock_getenv, mock_resend):
    def getenv_side_effect(key, default=None):
        if key == "RESEND_API_KEY":
            return "test_api_key"
        return default

    mock_getenv.side_effect = getenv_side_effect

    service = EmailService()

    assert service.sender == "onboarding@resend.dev"


# --------------------------------------------------
# Email sending tests
# --------------------------------------------------

@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_send_email_with_html_and_text(
    mock_getenv,
    mock_resend,
):
    mock_getenv.side_effect = lambda key, default=None: {
        "RESEND_API_KEY": "test_api_key",
        "EMAIL_FROM": "test@example.com",
    }.get(key, default)

    mock_resend.Emails.send.return_value = {
        "id": "test-email-123"
    }

    service = EmailService()

    result = service.send_email(
        to_email="recipient@example.com",
        subject="CareerForge AI Test",
        html_content="<h1>Hello</h1>",
        text_content="Hello",
    )

    assert result == "test-email-123"

    mock_resend.Emails.send.assert_called_once_with(
        {
            "from": "test@example.com",
            "to": ["recipient@example.com"],
            "subject": "CareerForge AI Test",
            "html": "<h1>Hello</h1>",
            "text": "Hello",
        }
    )


@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_send_email_without_optional_text(
    mock_getenv,
    mock_resend,
):
    mock_getenv.side_effect = lambda key, default=None: {
        "RESEND_API_KEY": "test_api_key",
        "EMAIL_FROM": "test@example.com",
    }.get(key, default)

    mock_resend.Emails.send.return_value = {
        "id": "test-email-456"
    }

    service = EmailService()

    result = service.send_email(
        to_email="recipient@example.com",
        subject="HTML-only email",
        html_content="<p>Hello</p>",
    )

    assert result == "test-email-456"

    sent_params = mock_resend.Emails.send.call_args.args[0]

    assert "text" not in sent_params


@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_send_email_accepts_object_response(
    mock_getenv,
    mock_resend,
):
    mock_getenv.side_effect = lambda key, default=None: {
        "RESEND_API_KEY": "test_api_key",
        "EMAIL_FROM": "test@example.com",
    }.get(key, default)

    mock_resend.Emails.send.return_value = MagicMock(
        id="test-email-789"
    )

    service = EmailService()

    result = service.send_email(
        to_email="recipient@example.com",
        subject="Object response test",
        html_content="<p>Hello</p>",
    )

    assert result == "test-email-789"


@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_send_email_raises_when_provider_returns_no_id(
    mock_getenv,
    mock_resend,
):
    mock_getenv.side_effect = lambda key, default=None: {
        "RESEND_API_KEY": "test_api_key",
        "EMAIL_FROM": "test@example.com",
    }.get(key, default)

    mock_resend.Emails.send.return_value = {}

    service = EmailService()

    with pytest.raises(
        RuntimeError,
        match="Resend did not return an email ID",
    ):
        service.send_email(
            to_email="recipient@example.com",
            subject="Missing ID test",
            html_content="<p>Hello</p>",
        )


@patch("app.notifications.email_service.resend")
@patch("app.notifications.email_service.os.getenv")
def test_send_email_propagates_provider_errors(
    mock_getenv,
    mock_resend,
):
    mock_getenv.side_effect = lambda key, default=None: {
        "RESEND_API_KEY": "test_api_key",
        "EMAIL_FROM": "test@example.com",
    }.get(key, default)

    mock_resend.Emails.send.side_effect = RuntimeError(
        "Simulated provider failure"
    )

    service = EmailService()

    with pytest.raises(
        RuntimeError,
        match="Simulated provider failure",
    ):
        service.send_email(
            to_email="recipient@example.com",
            subject="Provider error test",
            html_content="<p>Hello</p>",
        )