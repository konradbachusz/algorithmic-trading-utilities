"""
Portfolio-level risk constraints.

Checks sector concentration and enforces exposure limits before trade execution.
Prevents the portfolio from becoming overly concentrated in a single sector
or exceeding a total gross exposure ceiling.

Sector lookups use yfinance with an in-memory cache so each symbol is only
fetched once per process lifetime.
"""

import yfinance as yf

# In-memory cache: symbol -> sector string
_sector_cache = {}


def get_sector(symbol):
    """Get GICS sector for a symbol via yfinance, with in-memory caching.

    Fetches the sector from Yahoo Finance on first call for each symbol,
    then caches the result for subsequent lookups within the same process.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL').

    Returns:
        The sector name as a string (e.g., 'Technology'), or 'Unknown'
        if the lookup fails or the symbol has no sector data (e.g., ETFs).
    """
    if symbol in _sector_cache:
        return _sector_cache[symbol]

    try:
        info = yf.Ticker(symbol).info
        sector = info.get("sector", "Unknown") or "Unknown"
    except Exception:
        sector = "Unknown"

    _sector_cache[symbol] = sector
    return sector


def check_sector_exposure(
    existing_positions,
    proposed_trade,
    equity,
    max_sector_pct=0.30,
):
    """Check if adding the proposed trade would breach sector exposure limits.

    Args:
        existing_positions: List of position dicts with 'symbol' and
            'market_value' keys.
        proposed_trade: Dict with 'symbol' and 'notional' keys representing
            the trade to evaluate.
        equity: Account equity in dollars.
        max_sector_pct: Maximum gross exposure per sector as a fraction of
            equity (default 0.30 = 30%).

    Returns:
        A tuple of (allowed, reason) where allowed is a bool indicating
        whether the trade is permitted, and reason is a human-readable
        string explaining the decision.
    """
    sector = get_sector(proposed_trade["symbol"])
    if sector == "Unknown":
        return True, "Sector unknown — allowing trade"

    # Calculate current sector exposure
    sector_exposure = 0.0
    for pos in existing_positions:
        if get_sector(pos.get("symbol", "")) == sector:
            sector_exposure += abs(float(pos.get("market_value", 0)))

    # Add proposed trade notional
    proposed_notional = proposed_trade.get("notional", 0)
    new_sector_exposure = sector_exposure + proposed_notional
    sector_pct = new_sector_exposure / equity if equity > 0 else 0

    if sector_pct > max_sector_pct:
        return False, (
            f"Sector '{sector}' exposure would be {sector_pct:.1%} "
            f"(limit: {max_sector_pct:.0%}). "
            f"Current: ${sector_exposure:.0f}, Proposed: +${proposed_notional:.0f}"
        )

    return True, f"Sector '{sector}' exposure OK: {sector_pct:.1%}"


def check_gross_exposure(
    existing_positions,
    proposed_notional,
    equity,
    max_gross_pct=0.80,
):
    """Check if gross exposure would exceed the limit.

    Args:
        existing_positions: List of position dicts with 'market_value' keys.
        proposed_notional: Notional value in dollars of the proposed trade.
        equity: Account equity in dollars.
        max_gross_pct: Maximum gross exposure as a fraction of equity
            (default 0.80 = 80%).

    Returns:
        A tuple of (allowed, reason) where allowed is a bool indicating
        whether the trade is permitted, and reason is a human-readable
        string explaining the decision.
    """
    current_gross = sum(
        abs(float(p.get("market_value", 0))) for p in existing_positions
    )
    new_gross = current_gross + proposed_notional
    gross_pct = new_gross / equity if equity > 0 else 0

    if gross_pct > max_gross_pct:
        return False, (
            f"Gross exposure would be {gross_pct:.1%} (limit: {max_gross_pct:.0%}). "
            f"Current: ${current_gross:.0f}, Proposed: +${proposed_notional:.0f}"
        )

    return True, f"Gross exposure OK: {gross_pct:.1%}"
