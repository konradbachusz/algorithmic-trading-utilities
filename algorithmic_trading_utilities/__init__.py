"""
Algorithmic Trading Utilities

A comprehensive Python library for algorithmic trading with multiple broker integrations.
Provides utilities for position management, order execution, portfolio analytics, and risk management.
"""

__version__ = "0.1.0"
__author__ = "Konrad Bachusz"

# Import main modules for easy access
try:
    from .common import quantitative_tools, email_ops, visualization
    from .data import yahoo_finance
    from .brokers.alpaca import client, orders, positions, portfolio_ops, stop_loss_ops
except ImportError:
    # Allow package to be imported even if some dependencies are missing
    pass

__all__ = [
    "quantitative_tools",
    "email_ops",
    "visualization",
    "yahoo_finance",
    "client",
    "orders",
    "positions",
    "portfolio_ops",
    "stop_loss_ops",
]
