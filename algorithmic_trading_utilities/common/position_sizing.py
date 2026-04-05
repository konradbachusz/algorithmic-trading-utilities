"""
Volatility-adjusted position sizing using ATR.

The core principle: each position should risk the same dollar amount.
Risk per position = ATR-based stop distance x number of shares.
"""

from math import floor
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta


def get_atr(symbol, client, period=14):
    """Calculate the Average True Range for a symbol over the given period.

    Args:
        symbol: Stock ticker symbol.
        client: Alpaca StockHistoricalDataClient instance.
        period: Number of trading days for ATR calculation (default 14).

    Returns:
        ATR value in dollars as a float rounded to 4 decimal places,
        or None if insufficient data or on API failure.
    """
    end = datetime.now()
    # Fetch extra days to account for weekends/holidays
    start = end - timedelta(days=period * 2 + 10)

    try:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
            limit=period + 1,
        )
        bars = client.get_stock_bars(request)
        df = bars.df

        if len(df) < period + 1:
            return None

        # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
        df = df.reset_index()
        df["prev_close"] = df["close"].shift(1)
        df["tr"] = df.apply(
            lambda row: max(
                row["high"] - row["low"],
                abs(row["high"] - row["prev_close"]) if row["prev_close"] else 0,
                abs(row["low"] - row["prev_close"]) if row["prev_close"] else 0,
            ),
            axis=1,
        )
        atr = df["tr"].iloc[-period:].mean()
        return round(atr, 4)
    except Exception as e:
        print(f"Error calculating ATR for {symbol}: {e}")
        return None


def calculate_position_size(
    symbol,
    last_price,
    equity,
    risk_per_trade,
    client,
    atr_multiplier=2.0,
    max_position_pct=0.03,
    fallback_risk_pct=0.05,
):
    """Calculate position size based on ATR-adjusted risk.

    The position is sized so that a move of (ATR x atr_multiplier) against the
    position equals exactly (equity x risk_per_trade) in dollar loss.

    Args:
        symbol: Stock ticker.
        last_price: Current market price.
        equity: Total account equity.
        risk_per_trade: Fraction of equity to risk per trade (e.g., 0.01 = 1%).
        client: Alpaca data client for fetching historical bars.
        atr_multiplier: How many ATRs to use as the stop distance (default 2.0).
        max_position_pct: Maximum position size as fraction of equity (default 3%).
        fallback_risk_pct: If ATR unavailable, assume this % of price as risk
            (default 5%).

    Returns:
        A dict with keys: quantity, stop_distance, atr, risk_dollars, notional.
    """
    risk_dollars = equity * risk_per_trade
    atr = get_atr(symbol, client)

    if atr and atr > 0:
        stop_distance = atr * atr_multiplier
    else:
        # Fallback: assume 5% of price as stop distance
        stop_distance = last_price * fallback_risk_pct

    # Shares = risk_dollars / stop_distance
    raw_quantity = risk_dollars / stop_distance

    # Cap at max_position_pct of equity
    max_shares_by_notional = (equity * max_position_pct) / last_price
    quantity = int(floor(min(raw_quantity, max_shares_by_notional)))

    # Minimum 1 share (if the stock isn't too expensive)
    if quantity == 0 and last_price <= equity * max_position_pct:
        quantity = 1

    return {
        "quantity": quantity,
        "stop_distance": round(stop_distance, 4),
        "atr": atr,
        "risk_dollars": round(risk_dollars, 2),
        "notional": round(quantity * last_price, 2),
    }
