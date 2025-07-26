from positions import close_positions_below_threshold
from stop_loss_ops import place_trailing_stop_losses_funct
from config import loss_threshold, trailing_stop_loss_threshold
from email_ops import send_email_notification

"""
Script to manage stop losses.

This script closes positions below a specified loss threshold and places trailing stop loss orders
for positions that do not already have them. Sends email notifications upon success or failure.
"""

##################################
###### Trailing Stop Losses ######
##################################
# Due to the current limitation of the Alpaca API trailing stop losses have to be placed separately after a position has been filled

# This script manages stop losses by closing positions below a threshold and placing trailing stop losses.
if __name__ == "__main__":
    subject = "Stop Losses"
    try:
        # Close positions below the loss threshold
        closed_positions_count = close_positions_below_threshold(loss_threshold)

        # Place trailing stop loss orders
        trailing_stop_count = place_trailing_stop_losses_funct(
            trailing_stop_loss_threshold
        )

        # Send success notification
        notification = f"Closed positions: {closed_positions_count}, Placed trailing stop losses: {trailing_stop_count}"
        send_email_notification(subject, notification, type="SUCCESS")
        print(notification)
    except Exception as e:
        # Send failure notification
        notification = f"Error managing stop losses: {e}"
        send_email_notification(subject, notification, type="FAILURE")
        print(notification)
