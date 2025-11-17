import requests
from datetime import datetime
from bs4 import BeautifulSoup


def scrape_with_beautifulsoup(url):
    """
    Scrapes a website using requests and BeautifulSoup.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The text content of the website, or None if an error occurs.
    """
    try:
        # Send a GET request to the specified URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the text from the site
        text = soup.get_text()
        return text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None


def is_within_one_day(post_time_list: list) -> bool:
    """Checks if the post time is within one day."""
    if not post_time_list:
        return False

    # Find the relevant time string, e.g., "16 hours ago"
    time_string = next((s for s in post_time_list if "ago" in s), None)
    if not time_string:
        return False

    time_string = time_string.lower()

    # Always include if it's minutes or hours
    if "minute" in time_string or "hour" in time_string:
        return True
    # For days, only include if it's exactly "1 day ago" or "a day ago"
    if "day" in time_string and ("1 day" in time_string or "a day" in time_string):
        return True
    return False


def calculate_time_ago(pub_date_str):
    """
    Calculate relative time from a publication date string.

    Args:
        pub_date_str (str): ISO format timestamp string like "2025-10-11T19:27:39Z"

    Returns:
        str: Relative time format like "4h ago", "2d ago", etc.
    """
    if not pub_date_str:
        return ""

    try:
        # Parse the publication date
        pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))

        # Get current time (assuming UTC for consistency with Yahoo Finance)
        current_time = datetime.now(pub_date.tzinfo)

        # Calculate the difference
        time_diff = current_time - pub_date

        # Convert to appropriate units
        total_seconds = int(time_diff.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds}s ago" if total_seconds > 1 else "1s ago"
        elif total_seconds < 3600:  # Less than 1 hour
            minutes = total_seconds // 60
            return f"{minutes}m ago" if minutes > 1 else "1m ago"
        elif total_seconds < 86400:  # Less than 1 day
            hours = total_seconds // 3600
            return f"{hours}h ago" if hours > 1 else "1h ago"
        elif total_seconds < 604800:  # Less than 1 week
            days = total_seconds // 86400
            return f"{days}d ago" if days > 1 else "1d ago"
        else:  # More than a week
            weeks = total_seconds // 604800
            return f"{weeks}w ago" if weeks > 1 else "1w ago"

    except (ValueError, AttributeError):
        return ""
