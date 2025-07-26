"""
Email notification utilities for algorithmic trading.

This module provides broker-agnostic email notification functionality
for trading alerts and system notifications.
"""

import smtplib
import ssl
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()


def send_email_notification(subject, notification, type):
    """
    Send an email notification with a specified type and message.

    Parameters:
        subject (str): The subject line of the email.
        notification (str): The message body of the email.
        type (str): The type of notification (e.g., 'SUCCESS', 'FAILURE').

    The email includes:
        - A subject line with the type and timestamp.
        - A message body with the notification details and a link to the Alpaca dashboard.

    Returns:
        None
    """
    email = os.environ["recipient_email"]  # Recipient's email address

    # Get current timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format the email message
    message = """Subject: {subject} {type} Notification {now} BST

    {notification}

    Details: https://app.alpaca.markets/dashboard/overview
    
    """
    from_address = os.environ["web_app_email"]  # Sender's email address
    password = os.environ["web_app_email_password"]  # Sender's email password

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        # Log in to the email server
        server.login(from_address, password)

        # Send the email
        server.sendmail(
            from_address,
            email,
            message.format(
                now=now, subject=subject, type=type, notification=notification
            ),
        )

    # Log the notification status
    print(f"{subject} {type} Notification sent {now} BST")
    return None
