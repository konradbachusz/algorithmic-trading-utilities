"""Alpaca strategy performance helpers.

This module provides utility functions to gather broker-side state (positions,
orders, activities, balances, equity curve), persist a snapshot, and generate
manager-facing reports from snapshot files.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# Keep import style consistent with the rest of this package.
try:
    from common.config import trading_client
except ImportError:  # pragma: no cover
    from algorithmic_trading_utilities.common.config import trading_client

try:
    from brokers.alpaca.alpaca_ops import api
except ImportError:  # pragma: no cover
    from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import api

try:
    from brokers.alpaca.activities import get_activities
    from brokers.alpaca.account import get_balances
except ImportError:  # pragma: no cover
    from algorithmic_trading_utilities.brokers.alpaca.activities import get_activities
    from algorithmic_trading_utilities.brokers.alpaca.account import get_balances


def _to_serializable(value: Any, _seen: Optional[set] = None) -> Any:
    """Convert common Alpaca SDK objects into JSON-serializable structures.

    Args:
            value: Any value, possibly an Alpaca SDK model.

    Returns:
            Any: A JSON-serializable representation.
    """

    if _seen is None:
        _seen = set()

    if value is None:
        return None

    # Common scalar-ish types
    try:
        from enum import Enum
        from uuid import UUID
    except Exception:  # pragma: no cover
        Enum = None  # type: ignore[assignment]
        UUID = None  # type: ignore[assignment]

    if UUID is not None and isinstance(value, UUID):
        return str(value)
    if Enum is not None and isinstance(value, Enum):
        return _to_serializable(value.value, _seen=_seen)
    if hasattr(value, "isoformat") and callable(value.isoformat):
        try:
            return value.isoformat()
        except Exception:
            pass

    # Avoid infinite recursion on self-referential objects.
    value_id = id(value)
    if value_id in _seen:
        return str(value)

    # Treat mocks as atomic values (their internals are highly recursive).
    try:  # pragma: no cover
        import unittest.mock

        if isinstance(value, unittest.mock.Base):
            return str(value)
    except Exception:
        pass

    _seen.add(value_id)

    # alpaca-trade-api entities typically store their real data in `_raw`.
    if hasattr(value, "_raw"):
        try:
            raw = getattr(value, "_raw")
            if isinstance(raw, (dict, list)):
                return _to_serializable(raw, _seen=_seen)
        except Exception:
            pass
    if hasattr(value, "raw"):
        try:
            raw = getattr(value, "raw")
            if isinstance(raw, (dict, list)):
                return _to_serializable(raw, _seen=_seen)
        except Exception:
            pass

    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _to_serializable(v, _seen=_seen) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_serializable(v, _seen=_seen) for v in value]

    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _to_serializable(value.model_dump(), _seen=_seen)
    if hasattr(value, "dict") and callable(value.dict):
        return _to_serializable(value.dict(), _seen=_seen)

    if hasattr(value, "__dict__"):
        result = {}
        for key, val in vars(value).items():
            if key.startswith("_"):
                continue
            if callable(val):
                continue
            result[key] = _to_serializable(val, _seen=_seen)
        return result

    return str(value)


def save_strategy_snapshot(
    strategy_name: str,
    output_dir: Optional[Path] = None,
    timeframe: str = "1D",
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
) -> Path:
    """Retrieve and save broker state for a given strategy.

    The snapshot includes all positions, equity performance, orders, account
    activities, and balances.

    Args:
            strategy_name: Strategy identifier to embed in the snapshot filename and JSON.
            output_dir: Directory to write the JSON file to. Defaults to
                    `strategy_snapshots` in the current working directory.
            timeframe: Portfolio history timeframe (e.g. "1D").
            date_start: Optional start date (YYYY-MM-DD) for equity performance.
            date_end: Optional end date (YYYY-MM-DD) for equity performance.

    Returns:
            Path: Path to the saved JSON file.
    """

    output_dir = (
        Path(output_dir) if output_dir is not None else Path("strategy_snapshots")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{strategy_name}_snapshot_{timestamp}.json"

    positions = trading_client.get_all_positions()
    orders = api.list_orders(status="all")
    activities = get_activities()
    balances = get_balances()

    portfolio_kwargs: Dict[str, Any] = {"timeframe": timeframe}
    if date_start is not None:
        portfolio_kwargs["date_start"] = date_start
    if date_end is not None:
        portfolio_kwargs["date_end"] = date_end
    equity_performance = api.get_portfolio_history(**portfolio_kwargs)

    snapshot = {
        "strategy": strategy_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "positions": _to_serializable(positions),
        "equity_performance": _to_serializable(equity_performance),
        "orders": _to_serializable(orders),
        "activities": _to_serializable(activities),
        "balances": _to_serializable(balances),
    }

    output_path.write_text(
        json.dumps(snapshot, indent=2, default=str), encoding="utf-8"
    )
    return output_path


def load_strategy_snapshot(path: Path) -> Dict[str, Any]:
    """Load a saved strategy snapshot JSON file.

    Args:
            path: Path to a snapshot JSON file.

    Returns:
            dict: Snapshot dictionary.
    """

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _parse_maybe_literal(value: Any) -> Any:
    """Parse a string that may contain serialized Python/JSON literals.

    Attempts JSON parsing first, then falls back to `ast.literal_eval`.

    Args:
            value: Any input value.

    Returns:
            Any: Parsed value if parsing succeeded, otherwise the original value.
    """

    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not (
        (stripped.startswith("{") and stripped.endswith("}"))
        or (stripped.startswith("[") and stripped.endswith("]"))
    ):
        return value

    try:
        return json.loads(stripped)
    except Exception:
        pass

    try:
        return ast.literal_eval(stripped)
    except Exception:
        return value


def normalize_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a strategy snapshot into predictable structures.

    Args:
            snapshot: Raw snapshot dictionary.

    Returns:
            dict: Normalized snapshot with `_report_meta` warnings.
    """

    normalized = dict(snapshot or {})
    warnings = []
    unparsed_items = 0

    for key in ("positions", "orders", "activities"):
        items = normalized.get(key, [])
        if not isinstance(items, list):
            items = [items] if items is not None else []

        parsed_items = []
        for item in items:
            parsed = _parse_maybe_literal(item)
            if isinstance(parsed, dict):
                parsed_items.append(parsed)
            elif isinstance(parsed, list):
                parsed_items.extend([x for x in parsed if isinstance(x, dict)])
            else:
                parsed_items.append({"raw": str(item), "unparsed": True})
                unparsed_items += 1

        normalized[key] = parsed_items

    if not isinstance(normalized.get("balances"), dict):
        normalized["balances"] = {}
        warnings.append("balances was not a dict and was reset to empty dict")

    if not isinstance(normalized.get("equity_performance"), dict):
        normalized["equity_performance"] = {}
        warnings.append("equity_performance was not a dict and was reset to empty dict")

    # Heuristic warnings for common API defaults.
    if len(normalized.get("orders", [])) >= 50:
        warnings.append("orders may be truncated by API pagination/default limit")
    if len(normalized.get("activities", [])) >= 100:
        warnings.append(
            "activities may be truncated by API pagination/default page size"
        )

    normalized["_report_meta"] = {
        "warnings": warnings,
        "unparsed_items": unparsed_items,
    }
    return normalized


def _to_float(value: Any) -> Optional[float]:
    """Safely cast a value to float.

    Args:
            value: Input value.

    Returns:
            Optional[float]: Parsed float or None when conversion fails.
    """

    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _to_datetime(value: Any) -> Optional[datetime]:
    """Safely parse supported timestamp inputs into timezone-aware datetime.

    Accepted forms include datetime objects, numeric unix timestamps, and
    ISO-8601 strings.

    Args:
            value: Input timestamp-like value.

    Returns:
            Optional[datetime]: Parsed datetime or None if parsing fails.
    """

    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    # Numeric timestamp-like values
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            pd_obj = _get_pandas()
            if pd_obj is None:
                return None
            try:
                return pd_obj.to_datetime(value, utc=True).to_pydatetime()
            except Exception:
                return None

    return None


def _get_pandas():
    """Import and return the pandas module lazily.

    Returns:
            module | None: The pandas module when available, otherwise None.
    """

    try:
        return __import__("pandas")
    except Exception:
        return None


def _build_equity_series(equity_performance: Dict[str, Any]) -> Any:
    """Build a pandas equity series from snapshot equity performance data.

    Args:
            equity_performance: Equity performance payload from snapshot JSON.

    Returns:
            Any: A pandas Series indexed by DatetimeIndex, or None if data is
            insufficient/unavailable.
    """

    pd_obj = _get_pandas()
    if pd_obj is None:
        return None

    timestamps = equity_performance.get("timestamp", [])
    equity = equity_performance.get("equity", [])

    if not isinstance(timestamps, list) or not isinstance(equity, list):
        return None
    if len(timestamps) < 2 or len(timestamps) != len(equity):
        return None

    index = []
    values = []
    for ts, eq in zip(timestamps, equity):
        dt = _to_datetime(ts)
        val = _to_float(eq)
        if dt is None or val is None:
            continue
        index.append(dt)
        values.append(val)

    if len(values) < 2:
        return None

    series = pd_obj.Series(values, index=pd_obj.DatetimeIndex(index)).sort_index()
    return series[~series.index.duplicated(keep="last")]


def _compute_performance_metrics(
    equity_series: Any, include_benchmark: bool = False
) -> Dict[str, Any]:
    """Compute performance metrics from an equity series.

    Uses `PerformanceMetrics` when available and returns a structured response
    that supports graceful degradation when dependencies are missing.

    Args:
            equity_series: pandas Series of portfolio equity values.
            include_benchmark: Whether benchmark-relative metrics should be enabled.

    Returns:
            dict: Dict with keys `available`, `reason`, and `metrics`.
    """

    if equity_series is None or len(equity_series) < 2:
        return {
            "available": False,
            "reason": "insufficient equity data",
            "metrics": {},
        }

    try:
        try:
            from common.portfolio_ops import PerformanceMetrics
        except ImportError:
            from algorithmic_trading_utilities.common.portfolio_ops import (
                PerformanceMetrics,
            )

        pd_obj = _get_pandas()
        if pd_obj is None:
            return {
                "available": False,
                "reason": "performance metrics unavailable: pandas is not installed",
                "metrics": {},
            }

        benchmark = None if include_benchmark else pd_obj.Series(dtype=float)
        pm = PerformanceMetrics(
            portfolio_equity=equity_series, benchmark_equity=benchmark
        )
        return {
            "available": True,
            "reason": None,
            "metrics": pm.calculate_all(),
        }
    except Exception as exc:
        return {
            "available": False,
            "reason": f"performance metrics unavailable: {exc}",
            "metrics": {},
        }


def generate_strategy_report_data(
    snapshot: Dict[str, Any], include_benchmark: bool = False
) -> Dict[str, Any]:
    """Compute report aggregates from a snapshot dict.

    Args:
            snapshot: Raw snapshot dictionary.
            include_benchmark: Whether to compute benchmark-relative metrics.

    Returns:
            dict: Structured report data for rendering.
    """

    normalized = normalize_snapshot(snapshot)
    balances = normalized.get("balances", {})
    positions = normalized.get("positions", [])
    orders = normalized.get("orders", [])
    activities = normalized.get("activities", [])
    equity_performance = normalized.get("equity_performance", {})

    # Positions summary
    gross_exposure = 0.0
    net_exposure = 0.0
    long_mv = 0.0
    short_mv = 0.0
    total_unrealized = 0.0
    winners = 0
    losers = 0
    position_rows = []

    for pos in positions:
        symbol = pos.get("symbol")
        side = str(pos.get("side", "")).lower()
        qty = pos.get("qty") or pos.get("quantity")
        market_value = _to_float(pos.get("market_value"))
        unrealized = _to_float(pos.get("unrealized_pl"))
        unrealized_plpc = _to_float(pos.get("unrealized_plpc"))

        if market_value is not None:
            gross_exposure += abs(market_value)
            net_exposure += market_value
            if side == "long":
                long_mv += market_value
            elif side == "short":
                short_mv += market_value

        if unrealized is not None:
            total_unrealized += unrealized
            if unrealized > 0:
                winners += 1
            elif unrealized < 0:
                losers += 1

        position_rows.append(
            {
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "market_value": market_value,
                "unrealized_pl": unrealized,
                "unrealized_plpc": unrealized_plpc,
            }
        )

    top_positions = sorted(
        [p for p in position_rows if p["market_value"] is not None],
        key=lambda x: abs(x["market_value"]),
        reverse=True,
    )[:5]

    # Orders summary
    status_counts = Counter()
    type_counts = Counter()
    side_counts = Counter()
    symbol_counts = Counter()
    for order in orders:
        status_counts[
            str(order.get("status") or order.get("order_status") or "unknown")
        ] += 1
        type_counts[str(order.get("order_type") or order.get("type") or "unknown")] += 1
        side_counts[str(order.get("side") or "unknown")] += 1
        if order.get("symbol"):
            symbol_counts[str(order["symbol"])] += 1

    # Activities summary
    activity_type_counts = Counter()
    fills_buy = 0
    fills_sell = 0
    fill_qty = 0.0
    fill_turnover = 0.0
    fee_total = 0.0
    activity_timestamps = []
    activity_symbol_counts = Counter()

    for activity in activities:
        activity_type = str(activity.get("activity_type") or "unknown")
        activity_type_counts[activity_type] += 1

        ts = (
            activity.get("transaction_time")
            or activity.get("created_at")
            or activity.get("date")
        )
        dt = _to_datetime(ts)
        if dt is not None:
            activity_timestamps.append(dt)

        symbol = activity.get("symbol")
        if symbol:
            activity_symbol_counts[str(symbol)] += 1

        if activity_type == "FILL":
            qty = _to_float(activity.get("qty")) or 0.0
            price = _to_float(activity.get("price")) or 0.0
            side = str(activity.get("side") or "").lower()
            fill_qty += abs(qty)
            fill_turnover += abs(qty * price)
            if "buy" in side:
                fills_buy += 1
            elif "sell" in side:
                fills_sell += 1

        if activity_type == "FEE":
            fee_total += _to_float(activity.get("net_amount")) or 0.0

    # Equity metrics
    equity_series = _build_equity_series(equity_performance)
    performance = _compute_performance_metrics(
        equity_series, include_benchmark=include_benchmark
    )

    warnings = list(normalized.get("_report_meta", {}).get("warnings", []))
    if not performance["available"] and performance.get("reason"):
        warnings.append(performance["reason"])

    if equity_series is None:
        equity_window = None
    else:
        equity_window = {
            "start": equity_series.index.min().isoformat(),
            "end": equity_series.index.max().isoformat(),
            "points": int(len(equity_series)),
        }

    return {
        "strategy": normalized.get("strategy"),
        "snapshot_timestamp": normalized.get("timestamp"),
        "executive_summary": {
            "account_status": balances.get("status"),
            "currency": balances.get("currency"),
            "equity": _to_float(balances.get("equity")),
            "cash": _to_float(balances.get("cash")),
            "buying_power": _to_float(balances.get("buying_power")),
            "open_positions_count": len(positions),
            "gross_exposure": gross_exposure,
            "net_exposure": net_exposure,
            "long_market_value": _to_float(balances.get("long_market_value"))
            or long_mv,
            "short_market_value": _to_float(balances.get("short_market_value"))
            or short_mv,
            "unparsed_items": normalized.get("_report_meta", {}).get(
                "unparsed_items", 0
            ),
        },
        "positions": {
            "total_positions": len(positions),
            "total_unrealized_pl": total_unrealized,
            "winners": winners,
            "losers": losers,
            "top_positions": top_positions,
        },
        "balances": balances,
        "orders": {
            "total_orders": len(orders),
            "status_counts": dict(status_counts),
            "order_type_counts": dict(type_counts),
            "side_counts": dict(side_counts),
            "top_symbols": dict(symbol_counts.most_common(10)),
        },
        "activities": {
            "total_activities": len(activities),
            "activity_type_counts": dict(activity_type_counts),
            "fills_buy_count": fills_buy,
            "fills_sell_count": fills_sell,
            "fill_qty_total": fill_qty,
            "fill_turnover": fill_turnover,
            "fees_total": fee_total,
            "top_symbols": dict(activity_symbol_counts.most_common(10)),
            "start": (
                min(activity_timestamps).isoformat() if activity_timestamps else None
            ),
            "end": (
                max(activity_timestamps).isoformat() if activity_timestamps else None
            ),
        },
        "equity_performance": {
            "window": equity_window,
            "metrics_available": performance["available"],
            "metrics": performance["metrics"],
        },
        "warnings": warnings,
    }


def _render_markdown_report(report_data: Dict[str, Any]) -> str:
    """Render computed report data into a Markdown string.

    Args:
            report_data: Structured report dictionary generated by
                    `generate_strategy_report_data`.

    Returns:
            str: Markdown report content.
    """

    strategy = report_data.get("strategy") or "unknown_strategy"
    ts = report_data.get("snapshot_timestamp") or "unknown_timestamp"
    ex = report_data.get("executive_summary", {})
    pos = report_data.get("positions", {})
    ords = report_data.get("orders", {})
    acts = report_data.get("activities", {})
    eq = report_data.get("equity_performance", {})
    warnings = report_data.get("warnings", [])

    lines = []
    lines.append(f"# Strategy Report: {strategy}")
    lines.append("")
    lines.append(f"Snapshot timestamp: {ts}")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(f"- Account status: {ex.get('account_status')}")
    lines.append(f"- Currency: {ex.get('currency')}")
    lines.append(f"- Equity: {ex.get('equity')}")
    lines.append(f"- Cash: {ex.get('cash')}")
    lines.append(f"- Buying power: {ex.get('buying_power')}")
    lines.append(f"- Open positions: {ex.get('open_positions_count')}")
    lines.append(f"- Gross exposure: {ex.get('gross_exposure')}")
    lines.append(f"- Net exposure: {ex.get('net_exposure')}")
    lines.append("")

    lines.append("## Positions")
    lines.append(f"- Total positions: {pos.get('total_positions')}")
    lines.append(f"- Total unrealized P/L: {pos.get('total_unrealized_pl')}")
    lines.append(f"- Winners: {pos.get('winners')}, Losers: {pos.get('losers')}")
    lines.append("")
    lines.append("Top positions by absolute market value:")
    lines.append("")
    lines.append(
        "| Symbol | Side | Qty | Market Value | Unrealized P/L | Unrealized P/L % |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for item in pos.get("top_positions", []):
        lines.append(
            f"| {item.get('symbol')} | {item.get('side')} | {item.get('qty')} | "
            f"{item.get('market_value')} | {item.get('unrealized_pl')} | {item.get('unrealized_plpc')} |"
        )
    lines.append("")

    lines.append("## Orders Summary")
    lines.append(f"- Total orders: {ords.get('total_orders')}")
    lines.append(f"- Status counts: {ords.get('status_counts')}")
    lines.append(f"- Order type counts: {ords.get('order_type_counts')}")
    lines.append(f"- Side counts: {ords.get('side_counts')}")
    lines.append("")

    lines.append("## Activities Summary")
    lines.append(f"- Total activities: {acts.get('total_activities')}")
    lines.append(f"- Activity type counts: {acts.get('activity_type_counts')}")
    lines.append(f"- Fill turnover: {acts.get('fill_turnover')}")
    lines.append(f"- Total fill quantity: {acts.get('fill_qty_total')}")
    lines.append(f"- Fees total: {acts.get('fees_total')}")
    lines.append(f"- Activity window: {acts.get('start')} -> {acts.get('end')}")
    lines.append("")

    lines.append("## Equity Performance")
    lines.append(f"- Window: {eq.get('window')}")
    if eq.get("metrics_available"):
        lines.append("- Metrics:")
        metrics = eq.get("metrics", {})
        for key in sorted(metrics.keys()):
            lines.append(f"  - {key}: {metrics[key]}")
    else:
        lines.append(
            "- Metrics unavailable (insufficient data or environment limitations)"
        )
    lines.append("")

    lines.append("## Limitations and Data Quality")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No major data-quality warnings detected")

    return "\n".join(lines) + "\n"


def generate_strategy_report(
    snapshot_path: Path,
    output_path: Optional[Path] = None,
    format: str = "md",
    include_benchmark: bool = False,
) -> Path:
    """Generate a portfolio-manager report from a strategy snapshot file.

    Args:
            snapshot_path: Path to strategy snapshot JSON.
            output_path: Optional destination path. If omitted, saved next to snapshot.
            format: Output format, `md` or `json`.
            include_benchmark: Whether to attempt benchmark-relative performance metrics.

    Returns:
            Path: Output report file path.
    """

    snapshot_path = Path(snapshot_path)
    snapshot = load_strategy_snapshot(snapshot_path)
    report_data = generate_strategy_report_data(
        snapshot, include_benchmark=include_benchmark
    )

    fmt = format.lower().strip()
    if fmt not in {"md", "json"}:
        raise ValueError("format must be 'md' or 'json'")

    if output_path is None:
        suffix = ".md" if fmt == "md" else ".json"
        output_path = snapshot_path.with_name(f"{snapshot_path.stem}_report{suffix}")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "md":
        output_path.write_text(_render_markdown_report(report_data), encoding="utf-8")
    else:
        output_path.write_text(
            json.dumps(report_data, indent=2, default=str), encoding="utf-8"
        )

    return output_path
