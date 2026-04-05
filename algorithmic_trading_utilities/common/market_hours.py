"""Market hours utilities for US equity exchanges."""

from datetime import datetime, timezone, time as dtime


def is_market_hours() -> bool:
    """Return True if current UTC time is within NYSE regular session.

    Covers 09:25-16:05 ET (13:25-20:05 UTC) to include the opening
    auction and a small buffer after close.

    Returns:
        True if within market hours, False otherwise.
    """
    now_utc = datetime.now(timezone.utc).time()
    return dtime(13, 25) <= now_utc <= dtime(20, 5)
