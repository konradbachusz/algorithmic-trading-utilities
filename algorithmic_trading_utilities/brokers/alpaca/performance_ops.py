"""Alpaca strategy performance helpers.

This module provides utility functions to gather broker-side state (positions,
orders, activities, balances, equity curve) and persist a snapshot for a named
strategy.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


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
		from uuid import UUID
		from enum import Enum
		from datetime import date
	except Exception:  # pragma: no cover
		UUID = None  # type: ignore[assignment]
		Enum = None  # type: ignore[assignment]
		date = None  # type: ignore[assignment]

	if UUID is not None and isinstance(value, UUID):
		return str(value)
	if Enum is not None and isinstance(value, Enum):
		# Prefer the underlying value (often a string) when possible.
		return _to_serializable(value.value, _seen=_seen)
	if hasattr(value, "isoformat") and callable(value.isoformat):
		# datetime/date-like
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
	# If we don't use it, serializing via __dict__ yields empty dicts.
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

	# Alpaca-py models often use pydantic v2
	if hasattr(value, "model_dump") and callable(value.model_dump):
		return _to_serializable(value.model_dump(), _seen=_seen)
	# pydantic v1 compatibility
	if hasattr(value, "dict") and callable(value.dict):
		return _to_serializable(value.dict(), _seen=_seen)

	if hasattr(value, "__dict__"):
		# Only serialize non-private, non-callable attributes.
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

	The snapshot includes:
	- All positions
	- Equity performance (portfolio history)
	- All orders
	- All account activities
	- Balances

	Args:
		strategy_name: Strategy identifier to embed in the snapshot filename and JSON.
		output_dir: Directory to write the JSON file to. Defaults to a folder named
			`strategy_snapshots` in the current working directory.
		timeframe: Portfolio history timeframe (e.g. "1D").
		date_start: Optional start date (YYYY-MM-DD) for equity performance.
		date_end: Optional end date (YYYY-MM-DD) for equity performance.

	Returns:
		pathlib.Path: Path to the saved JSON file.
	"""

	if output_dir is None:
		output_dir = Path("strategy_snapshots")
	else:
		output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
	output_path = output_dir / f"{strategy_name}_snapshot_{timestamp}.json"

	positions = trading_client.get_all_positions()

	# Use alpaca-trade-api REST client here to reliably retrieve *all* orders.
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

	output_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
	return output_path

