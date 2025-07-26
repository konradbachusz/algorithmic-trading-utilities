from portfolio_ops import (
    calculate_performance_metrics,
    compare_portfolio_and_benchmark,
    get_portfolio_and_benchmark_returns,
)

"""
This script calculates and displays performance metrics for a portfolio, and compares the portfolio's returns to a benchmark (e.g., the S&P 500).
Functions used:
- `calculate_performance_metrics()`: Computes key performance metrics for the portfolio.
- `compare_portfolio_and_benchmark()`: Visualizes and compares the returns of the portfolio and the benchmark.
- `get_portfolio_and_benchmark_returns()`: Retrieves the returns data for both the portfolio and the benchmark.
The script prints each performance metric and generates a comparison plot between the portfolio and the benchmark.
"""


metrics = calculate_performance_metrics()
for key, value in metrics.items():
    print(f"{key}: {value}")


compare_portfolio_and_benchmark(
    get_portfolio_and_benchmark_returns(), "Portfolio vs S&P 500 Returns"
)
