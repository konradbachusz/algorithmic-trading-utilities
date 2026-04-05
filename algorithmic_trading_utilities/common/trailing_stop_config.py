"""
Adaptive trailing stop calculation based on stock volatility.

Instead of a flat 10% trailing stop for all positions, the stop percentage
is derived from each stock's ATR, clamped between configurable bounds.
"""


def calculate_trailing_stop_pct(
    atr,
    last_price,
    min_pct=0.05,
    max_pct=0.20,
    atr_multiplier=2.5,
):
    """Calculate trailing stop percentage based on ATR.

    The trailing stop is set at atr_multiplier x ATR as a percentage of price,
    clamped between min_pct and max_pct.

    Args:
        atr: Average True Range in dollars. If None or <= 0, returns the
            default fallback of 10%.
        last_price: Current price of the stock. If <= 0, returns the default
            fallback of 10%.
        min_pct: Minimum trailing stop percentage (default 5%).
        max_pct: Maximum trailing stop percentage (default 20%).
        atr_multiplier: Multiple of ATR to use (default 2.5).

    Returns:
        Trailing stop percentage as a decimal (e.g., 0.08 for 8%).
    """
    if not atr or atr <= 0 or last_price <= 0:
        return 0.10  # Default fallback to 10%

    atr_pct = (atr * atr_multiplier) / last_price
    clamped = max(min_pct, min(atr_pct, max_pct))
    return round(clamped, 4)
