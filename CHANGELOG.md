# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.5.0] - 2026-04-26

### Added
- Reusable performance report helpers: `fetch_normalized_benchmark()` aligns and rescales the S&P 500 to a portfolio's start value (`common.portfolio_ops`).
- Plot orchestration: `build_performance_figures()` builds all `PerformanceViz` plots and hides the benchmark line on dollar-scale plots (cumulative returns, equity curve) where the unit comparison is meaningless (`common.viz_ops`).
- New module `common.report_ops` with `write_performance_pdf()` — writes a multi-page PDF report (cover page with title, period, and metrics block, plus one figure per page).
- End-to-end performance reporting: `generate_performance_report()` saves a strategy snapshot, computes metrics, renders plots, and writes a PDF in one call (`brokers.alpaca.performance_ops`).
- `get_portfolio_equity_series()` — converts Alpaca portfolio history into a date-indexed `pd.Series` (`brokers.alpaca.performance_ops`).
- Tests for the new helpers (`test_report_ops.py`, plus additions to `test_portfolio_ops.py`, `test_viz_ops.py`, `test_performance_ops.py`).

## [0.4.0] - 2026-04-05

### Added
- Entry order cancellation: `cancel_entry_orders()` cancels unfilled MARKET and LIMIT orders while preserving stop and trailing-stop orders (`brokers.alpaca.orders`).
- Market hours utility: `is_market_hours()` checks whether the current time falls within NYSE regular session hours, including open/close buffers (`common.market_hours`).
- Tests for `cancel_entry_orders` (order filtering, empty list, individual failure handling) and `is_market_hours` (session, boundaries, off-hours).

## [0.3.1] - 2026-04-05

### Changed
- `pyproject.toml` now reads version dynamically from `VERSION` via `[tool.setuptools.dynamic]` instead of a hardcoded string.
- `setup.py` now reads version from `VERSION` at build time, keeping both build configs in sync automatically.

## [0.3.0] - 2026-04-05

### Added
- Targeted order cancellation: `cancel_orders_for_symbols()` cancels orders only for specified symbols, preserving protective stops on other positions (`brokers.alpaca.cancel_orders_targeted`).
- Portfolio risk constraints: `check_sector_exposure()` and `check_gross_exposure()` enforce sector concentration and gross exposure limits before trade execution (`common.portfolio_constraints`).
- ATR-based position sizing: `get_atr()` and `calculate_position_size()` size positions so each risks the same dollar amount based on volatility (`common.position_sizing`).
- Adaptive trailing stops: `calculate_trailing_stop_pct()` derives per-stock trailing stop percentages from ATR instead of using a flat value (`common.trailing_stop_config`).
- Tests for all new modules (`test_cancel_orders_targeted.py`, `test_portfolio_constraints.py`, `test_position_sizing.py`, `test_trailing_stop_config.py`).

## [0.2.0] - 2026-04-05

### Added
- Alpaca account helpers: `get_account()` and `get_balances()` (`brokers.alpaca.account`).
- Alpaca activities helper: `get_activities()` (`brokers.alpaca.activities`).
- Strategy snapshot export: `save_strategy_snapshot()` persists positions, orders, activities, balances, and equity performance to JSON (`brokers.alpaca.performance_ops`).
- Strategy report generation: `generate_strategy_report()` and `generate_strategy_report_data()` produce Markdown or JSON reports from snapshot files.
- Snapshot normalization: `normalize_snapshot()` cleans raw snapshot data with data-quality warnings.
- `CLAUDE.md` project guidance file for Claude Code.
- `VERSION` file for tracking releases.
- Tests for account, activities, snapshot export, and report generation (`test_account.py`, `test_activities.py`, `test_performance_ops.py`, `test_reporting.py`).
- GitHub Actions workflow `tag-release.yml` that automatically creates a git tag from `VERSION` when a branch is merged into `main`.

### Changed
- Improved snapshot serialization to handle recursive and self-referential Alpaca SDK objects safely.
- Test setup (`conftest.py`) now gracefully skips when SciPy/PerformanceMetrics cannot be imported.

## [0.1.2] - 2026-01-04
- Added place_trailing_stop_losses_funct

## [0.1.1] - 2025-11-09

### Updates
- Added the `plot_cumulative_returns_timeseries` and updated documentation of getting metrics

### Additions

- Initial release of `PerformanceMetrics` class for portfolio analysis.
- Metrics included: Sharpe, Sortino, Alpha/Beta, Max/Avg Drawdown, Drawdown Duration, VaR/CVaR, Skewness, Kurtosis, Calmar Ratio.
- `report()` method added for console summary comparing strategy vs benchmark.
- Unit tests for core metrics included.
- Modular benchmark parameterization; SP500 can now be used as default if benchmark data is not provided.
- Added `Benchmark_Interpretation.md` with clear, concise explanations for all metrics.
- Added a visualization module for portfolio performance, including rolling alpha & beta plots.

## [0.1.0] - 2025-09-09

### Additions

- Initial release of `PerformanceMetrics` class for portfolio analysis.
- Metrics included: Sharpe, Sortino, Alpha/Beta, Max/Avg Drawdown, Drawdown Duration, VaR/CVaR, Skewness, Kurtosis, Calmar Ratio.
- `report()` method added for console summary comparing strategy vs benchmark.
- Unit tests for core metrics included.
- Modular benchmark parameterization; SP500 can now be used as default if benchmark data is not provided.
- Added `Benchmark_Interpretation.md` with clear, concise explanations for all metrics.
- Added a visualization module for portfolio performance, including rolling alpha & beta plots.

### Updates

- Initial library structure and setup.
- Improved `PerformanceMetrics` class with Google-style docstrings for all functions.
- `drawdown_duration` rewritten for performance using NumPy operations.

### Deprecations

- Older version of `portfolio_ops.py`.
- Old version of `viz_ops.py`.

### Contributors to this release

- Yosri Ben Halima
