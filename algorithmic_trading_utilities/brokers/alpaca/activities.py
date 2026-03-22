"""Alpaca account activities helpers."""


# Keep import style consistent with the rest of this package.
try:
    from brokers.alpaca.alpaca_ops import api
except ImportError:  # pragma: no cover
    from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import api


def get_activities(
    activity_types=None,
    until=None,
    after=None,
    direction=None,
    date=None,
    page_size=None,
    page_token=None,
):
    """Retrieve account activities from Alpaca.

    Wraps the Alpaca account activities endpoint.

    Args:
        activity_types: Activity type filter. Can be a string (e.g. "FILL") or a
            list of strings.
        until: ISO-8601 timestamp string to filter activities up to.
        after: ISO-8601 timestamp string to filter activities after.
        direction: Sort direction ("asc" or "desc").
        date: Date filter (YYYY-MM-DD). Cannot be used with `until`/`after`.
        page_size: Page size for pagination.
        page_token: Pagination token.

    Returns:
        list: A list of account activity objects.
    """

    return api.get_activities(
        activity_types=activity_types,
        until=until,
        after=after,
        direction=direction,
        date=date,
        page_size=page_size,
        page_token=page_token,
    )
