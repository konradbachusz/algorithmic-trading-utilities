# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
