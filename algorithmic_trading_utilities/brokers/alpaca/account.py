"""Alpaca account/balance helpers."""


# Keep import style consistent with the rest of this package.
try:
    from common.config import trading_client
except ImportError:  # pragma: no cover
    from algorithmic_trading_utilities.common.config import trading_client


def get_account():
    """Retrieve the Alpaca trading account object.

    Returns:
        object: An Alpaca account object (model varies by client settings).
    """

    return trading_client.get_account()


def _get_field(obj, field):
    """Safely read a field from an object or dict.

    Args:
        obj: Object or mapping.
        field: Field name.

    Returns:
        object: The field value if present, otherwise None.
    """
    if hasattr(obj, field):
        return getattr(obj, field)
    try:
        return obj[field]
    except Exception:
        return None


def get_balances():
    """Return common account balance fields.

    Returns a small dict so callers don't need to know the exact account model
    used by the Alpaca client.

    Returns:
        dict: Account snapshot fields. Always includes `cash`, `buying_power`,
        `equity`, and `portfolio_value`, and may include additional fields if
        present on the account object (e.g. margin, market values, status).
    """

    account = get_account()

    fields = [
        # Core balances
        "cash",
        "buying_power",
        "equity",
        "portfolio_value",
        # Common account state
        "status",
        "currency",
        "pattern_day_trader",
        "daytrade_count",
        # Margin / risk-related
        "multiplier",
        "initial_margin",
        "maintenance_margin",
        "last_maintenance_margin",
        "regt_buying_power",
        # Exposure / valuation
        "long_market_value",
        "short_market_value",
        "gross_position_value",
        "last_equity",
        # Transfers / misc
        "accrued_fees",
        "pending_transfer_in",
    ]

    return {field: _get_field(account, field) for field in fields}
