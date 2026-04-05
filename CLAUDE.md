# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install uv
uv pip install --system -r requirements.txt

# Run all tests
pytest tests -v -s

# Run a single test file
pytest tests/test_portfolio_ops.py -v -s

# Run a single test function
pytest tests/test_portfolio_ops.py::test_function_name -v -s

# Lint/format (dev dependencies)
pip install -e ".[dev]"
black algorithmic_trading_utilities/
flake8 algorithmic_trading_utilities/
mypy algorithmic_trading_utilities/
```

## Environment Variables

Required in `.env` (see `.env.example`): `PAPER_KEY`, `PAPER_SECRET` (Alpaca paper trading API credentials). Optional: `web_app_email`, `web_app_email_password`, `recipient_email` for email notifications.

## Architecture

This is a Python library for algorithmic trading, structured into three domains:

- **`brokers/alpaca/`** - Alpaca API integration: account info, order placement (with retry/backoff), position management, portfolio history, strategy performance snapshots. All broker modules depend on `common/config.py` for the `TradingClient` instance.
- **`common/`** - Shared utilities: `PerformanceMetrics` class (Sharpe, Sortino, alpha/beta, drawdown, VaR/CVaR), ATR-based position sizing (`position_sizing.py`), portfolio risk constraints (`portfolio_constraints.py`), adaptive trailing stops (`trailing_stop_config.py`), sentiment analysis (DistilRoBERTa via HuggingFace), email notifications, web scraping, visualization.
- **`data/`** - Market data retrieval from Alpaca (`get_data.py`) and Yahoo Finance (`yfinance_ops.py`).

### Key patterns

**Dual import convention**: All internal imports use a try/except pattern to support both direct execution and package installation:
```python
try:
    from common.config import trading_client
except ImportError:
    from algorithmic_trading_utilities.common.config import trading_client
```
Follow this pattern when adding new cross-module imports.

**`PerformanceMetrics`** (`common/portfolio_ops.py`) is the central analytics class. It takes portfolio and optional benchmark equity series and provides all risk/return metrics. Tests use a `sample_data` fixture from `conftest.py` that generates deterministic random data (seed 42).

**`performance_ops.py`** (`brokers/alpaca/performance_ops.py`) exports strategy snapshots as JSON and generates Markdown/JSON reports to `strategy_snapshots/`. Key entry points: `save_strategy_snapshot()` for capturing broker state, `generate_strategy_report()` for rendering reports from snapshots. It serializes Alpaca SDK objects by converting `RawData` dicts, enums, and recursive structures to plain types via `_to_serializable()`.

## Generating Strategy Snapshots

`test.py` is a dev entrypoint that creates a strategy snapshot (JSON) and report (Markdown) in `strategy_snapshots/`:

```bash
python test.py <strategy_name>                          # defaults: 1D timeframe, md report
python test.py sentiment_analysis_v1 --timeframe 1H     # custom timeframe
python test.py my_strat --include-benchmark              # include benchmark-relative metrics
```

## CI

GitHub Actions runs `pytest tests -v -s` on Python 3.10 against `main` for pushes and PRs. API keys are injected via repository secrets. A separate `tag-release.yml` workflow automatically creates a git tag from `VERSION` on every push to `main` (skips if the tag already exists).
