from positions import close_positions_below_threshold
from email_ops import send_email_notification

"""
Script liquidates all non-performing positions that have returns below 0. It's meant to be run once per day.
"""

if __name__ == "__main__":
    subject = "Liquidating non-performing positions"
    try:
        # Close positions below the loss threshold
        closed_positions_count = close_positions_below_threshold(0)

        # Send success notification
        notification = f"Closed positions: {closed_positions_count}"
        send_email_notification(subject, notification, type="SUCCESS")
        print(notification)
    except Exception as e:
        # Send failure notification
        notification = f"Error liquidating non-performing positions: {e}"
        send_email_notification(subject, notification, type="FAILURE")
        print(notification)
