import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(1, "algorithmic_trading_utilities")
import pytest
from unittest.mock import patch, MagicMock
from common.email_ops import send_email_notification
import os


class TestSendEmailNotification:

    # Successfully sends an email notification
    def test_send_email_notification_success(self, mocker):
        # Arrange
        mock_smtp = mocker.patch("common.email_ops.smtplib.SMTP_SSL")
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Mock environment variables
        mocker.patch.dict(
            os.environ,
            {
                "web_app_email": "test_email@example.com",
                "web_app_email_password": "test_password",
                "recipient_email": "recipient@example.com",
            },
        )

        notification = "Test notification"
        type = "SUCCESS"
        subject = "Placed Trades"

        # Act
        send_email_notification(subject, notification, type)

        # Assert
        mock_server.login.assert_called_once_with(
            os.environ["web_app_email"], os.environ["web_app_email_password"]
        )
        mock_server.sendmail.assert_called_once_with(
            os.environ["web_app_email"],
            os.environ["recipient_email"],
            f"""Subject: {subject} {type} Notification {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} BST

    {notification}

    Details: https://app.alpaca.markets/dashboard/overview
    
    """,
        )

    # Handles case where email sending fails
    def test_send_email_notification_failure(self, mocker):
        # Arrange
        mock_smtp = mocker.patch("common.email_ops.smtplib.SMTP_SSL")
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.sendmail.side_effect = Exception("SMTP error")

        # Mock environment variables
        mocker.patch.dict(
            os.environ,
            {
                "web_app_email": "test_email@example.com",
                "web_app_email_password": "test_password",
                "recipient_email": "recipient@example.com",
            },
        )

        notification = "Test notification"
        type = "FAILURE"
        subject = "Placed Trades"

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            send_email_notification(subject, notification, type)
        # Fix: Check the actual exception message for "SMTP error"
        assert "SMTP error" in str(excinfo.value)

        mock_server.login.assert_called_once_with(
            os.environ["web_app_email"], os.environ["web_app_email_password"]
        )
        mock_server.sendmail.assert_called_once()
