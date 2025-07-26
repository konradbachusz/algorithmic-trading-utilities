"""
Alpaca broker integration package.
"""

from .client import trading_client, get_trading_client
from .orders import place_order, cancel_all_orders, get_open_orders
from .positions import get_all_positions, close_positions_below_threshold
from .portfolio_ops import (
    calculate_performance_metrics,
    get_portfolio_and_benchmark_returns,
)
from .stop_loss_ops import place_trailing_stop_losses_funct
from .data import get_historical_bars

__all__ = [
    "trading_client",
    "get_trading_client",
    "place_order",
    "cancel_all_orders",
    "get_open_orders",
    "get_all_positions",
    "close_positions_below_threshold",
    "calculate_performance_metrics",
    "get_portfolio_and_benchmark_returns",
    "place_trailing_stop_losses_funct",
    "get_historical_bars",
]
