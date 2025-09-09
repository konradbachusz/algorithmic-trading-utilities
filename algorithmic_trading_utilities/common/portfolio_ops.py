import sys

sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
import pandas as pd

# # Try different import approaches for data modules
# try:
#     from data.yfinance_ops import get_sp500_prices
# except ImportError:
#     from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices  # noqa: F401

# # Try different import approaches for broker modules
# try:
#     from brokers.alpaca.alpaca_ops import get_portfolio_history
# except ImportError:
#     from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import (
#         get_portfolio_history,  # noqa: F401
#     )

from scipy.stats import skew, kurtosis
from sklearn.linear_model import LinearRegression


class PerformanceMetrics:
    """Performance Metrics Computation Module."""

    def __init__(
        self,
        portfolio_equity: np.ndarray,
        benchmark_equity: np.ndarray = None,
        risk_free_rate=0.02 / 252,
    ):
        """
        Initialize performance metrics calculator.

        Args:
            portfolio_equity (np.ndarray): Daily portfolio equity values.
            benchmark_equity (np.ndarray, optional): Daily benchmark equity values.
                If provided, enables alpha/beta calculations. Defaults to None.
            risk_free_rate (float, optional): Daily risk-free rate. Defaults to 0.02/252.
        """
        self.portfolio = np.array(portfolio_equity)
        self.benchmark = (
            np.array(benchmark_equity) if benchmark_equity is not None else None
        )
        self.risk_free_rate = risk_free_rate
        self.returns = self._daily_returns(self.portfolio)
        self.benchmark_returns = (
            self._daily_returns(self.benchmark) if self.benchmark is not None else None
        )

    @staticmethod
    def _daily_returns(equity: np.ndarray) -> np.ndarray:
        """
        Compute daily returns from equity curve.

        Args:
            equity (np.ndarray): Array of equity values.

        Returns:
            np.ndarray: Array of daily returns.
        """
        if equity is None or len(equity) < 2:
            return np.array([])
        return np.diff(equity) / equity[:-1]

    def average_return(self) -> float:
        """
        Compute average daily return.

        Returns:
            float: Mean of daily returns.
        """
        return np.mean(self.returns)

    def total_return(self) -> float:
        """
        Compute cumulative portfolio return.

        Returns:
            float: Total return from start to end.
        """
        return self.portfolio[-1] / self.portfolio[0] - 1

    def std_dev(self) -> float:
        """
        Compute standard deviation of returns.

        Returns:
            float: Standard deviation of daily returns.
        """
        return np.std(self.returns)

    def sharpe_ratio(self) -> float:
        """
        Compute daily Sharpe ratio.

        Returns:
            float: Sharpe ratio value.
        """
        return (self.average_return() - self.risk_free_rate) / self.std_dev()

    def annualised_sharpe(self) -> float:
        """
        Compute annualised Sharpe ratio.

        Returns:
            float: Annualised Sharpe ratio.
        """
        return self.sharpe_ratio() * np.sqrt(252)

    def downside_std(self) -> float:
        """
        Compute downside deviation of returns.

        Returns:
            float: Standard deviation of negative returns.
        """
        downside = self.returns[self.returns < 0]
        return np.std(downside) if len(downside) > 0 else 0.0

    def sortino_ratio(self) -> float:
        """
        Compute Sortino ratio.

        Returns:
            float: Sortino ratio value.
        """
        dr = self.downside_std()
        return (self.average_return() - self.risk_free_rate) / dr if dr > 0 else np.nan

    def annualised_sortino(self) -> float:
        """
        Compute annualised Sortino ratio.

        Returns:
            float: Annualised Sortino ratio.
        """
        return self.sortino_ratio() * np.sqrt(252)

    def calmar_ratio(self) -> float:
        """
        Compute Calmar ratio.

        Returns:
            float: Calmar ratio (annual return / max drawdown).
        """
        dd = self.max_drawdown()
        return self.average_return() * 252 / dd if dd > 0 else np.nan

    def drawdown_series(self) -> np.ndarray:
        """
        Compute drawdown series.

        Returns:
            np.ndarray: Array of drawdown values (fractions).
        """
        cum_max = np.maximum.accumulate(self.portfolio)
        return (cum_max - self.portfolio) / cum_max

    def max_drawdown(self) -> float:
        """
        Compute maximum drawdown.

        Returns:
            float: Maximum drawdown (fraction).
        """
        return np.max(self.drawdown_series())

    def average_drawdown(self) -> float:
        """
        Compute average drawdown.

        Returns:
            float: Mean drawdown (fraction).
        """
        return np.mean(self.drawdown_series())

    def drawdown_duration(self) -> int:
        """
        Compute maximum drawdown duration in days using a vectorized approach.

        Returns:
            int: Longest duration of continuous drawdown.
        """
        dd = self.drawdown_series()

        if dd.size == 0:
            return 0
        
        is_drawdown = dd > 0
        boundaries = np.diff(np.concatenate(([False], is_drawdown, [False])))

        run_locations = np.where(boundaries)[0]

        
        drawdown_lengths = run_locations[1::2] - run_locations[0::2]

        return np.max(drawdown_lengths, initial=0)

    def return_distribution_stats(self, alpha=0.05) -> dict:
        """
        Compute return distribution statistics.

        Args:
            alpha (float, optional): Quantile for VaR/CVaR. Defaults to 0.05.

        Returns:
            dict: Dictionary with skewness, kurtosis, VaR, and CVaR.
        """
        r = self.returns
        return {
            "skewness": skew(r),
            "kurtosis": kurtosis(r),
            "VaR": np.percentile(r, 100 * alpha),
            "CVaR": np.mean(r[r <= np.percentile(r, 100 * alpha)]),
        }

    def alpha_beta(self) -> dict:
        """
        Compute CAPM alpha and beta against benchmark.

        Returns:
            dict: Dictionary with alpha and beta values.
        """
        if self.benchmark_returns is None or len(self.benchmark_returns) != len(
            self.returns
        ):
            return {"alpha": np.nan, "beta": np.nan}

        y = self.returns - self.risk_free_rate
        X = self.benchmark_returns - self.risk_free_rate
        model = LinearRegression().fit(X.reshape(-1, 1), y.reshape(-1, 1))
        return {"alpha": model.intercept_[0], "beta": model.coef_[0][0]}

    def rolling_alpha_beta(self, window=252) -> pd.DataFrame:
        """
        Compute rolling alpha and beta values.

        Args:
            window (int, optional): Rolling window size. Defaults to 252.

        Returns:
            pd.DataFrame: DataFrame with rolling alpha and beta.
        """
        if self.benchmark_returns is None or len(self.benchmark_returns) < window:
            return pd.DataFrame(columns=["alpha", "beta"])

        alphas, betas = [], []
        for i in range(len(self.returns) - window + 1):
            y = self.returns[i : i + window] - self.risk_free_rate
            X = self.benchmark_returns[i : i + window] - self.risk_free_rate
            model = LinearRegression().fit(X.reshape(-1, 1), y.reshape(-1, 1))
            alphas.append(model.intercept_[0])
            betas.append(model.coef_[0][0])

        index = np.arange(window - 1, len(self.returns))
        return pd.DataFrame({"alpha": alphas, "beta": betas}, index=index)

    def calculate_all(self) -> dict:
        """
        Aggregate all performance metrics.

        Returns:
            dict: Dictionary of performance metrics.
        """
        dist_stats = self.return_distribution_stats()
        metrics = {
            "average_return": self.average_return(),
            "total_return": self.total_return(),
            "std_dev": self.std_dev(),
            "sharpe_ratio": self.sharpe_ratio(),
            "annualised_sharpe": self.annualised_sharpe(),
            "sortino_ratio": self.sortino_ratio(),
            "annualised_sortino": self.annualised_sortino(),
            "max_drawdown": self.max_drawdown(),
            "average_drawdown": self.average_drawdown(),
            "drawdown_duration": self.drawdown_duration(),
            "skewness": dist_stats["skewness"],
            "kurtosis": dist_stats["kurtosis"],
            "VaR_5%": dist_stats["VaR"],
            "CVaR_5%": dist_stats["CVaR"],
            "calmar_ratio": self.calmar_ratio(),
        }
        metrics.update(self.alpha_beta())
        return metrics

    def calculate_benchmark_metrics(self) -> dict:
        """
        Compute performance metrics for the benchmark.

        Returns:
            dict: Benchmark metrics dictionary.
        """
        if self.benchmark is None:
            return {k: float("nan") for k in self.calculate_all().keys()}

        benchmark_pm = PerformanceMetrics(
            portfolio_equity=self.benchmark,
            benchmark_equity=None,
            risk_free_rate=self.risk_free_rate,
        )
        bm_metrics = benchmark_pm.calculate_all()
        bm_metrics.update({"alpha": 0, "beta": 1})
        return bm_metrics

    def report(self):
        """
        Print a formatted performance comparison table.

        Displays strategy vs benchmark metrics.
        """
        if self.benchmark is None:
            print("Benchmark equity not provided. Cannot generate comparison report.")
            return

        # Calculate metrics
        strategy_metrics = self.calculate_all()

        # Temporary swap portfolio with benchmark to calculate benchmark metrics
        original_portfolio = self.portfolio
        original_returns = self.returns
        self.portfolio = self.benchmark
        self.returns = self.benchmark_returns
        benchmark_metrics = self.calculate_benchmark_metrics()
        # Restore original portfolio
        self.portfolio = original_portfolio
        self.returns = original_returns

        title = "Strategy vs Benchmark Performance Comparison"
        span = 54
        len_title = len(title)
        remainder = span - len_title
        print("=" * span)
        print(" " * ((remainder) // 2) + title + " " * (remainder // 2))
        print("=" * span)

        label_width, value_width, market_width = 25, 12, 12
        print(
            f"{'':{label_width}} {'Strategy':>{value_width}} {'Benchmark':>{market_width}}"
        )
        print("-" * span)

        metrics_list = [
            ("Sharpe Ratio:", "sharpe_ratio"),
            ("Sortino Ratio:", "sortino_ratio"),
            ("Cumulative Return:", "total_return"),
            ("Max Drawdown:", "max_drawdown"),
            ("Average Drawdown:", "average_drawdown"),
            ("Drawdown Duration:", "drawdown_duration"),
            ("Skewness:", "skewness"),
            ("Kurtosis:", "kurtosis"),
            ("VaR 5%:", "VaR_5%"),
            ("CVaR 5%:", "CVaR_5%"),
            ("Calmar Ratio:", "calmar_ratio"),
            ("Alpha:", "alpha"),
            ("Beta:", "beta"),
        ]

        for label, key in metrics_list:
            strat_val = strategy_metrics.get(key, float("nan"))
            bench_val = benchmark_metrics.get(key, float("nan"))
            # Format percentages
            if (
                "Return" in label
                or " Drawdown" in label
                or "VaR" in label
                or "CVaR" in label
                or "Alpha" in label
            ):
                strat_val_fmt = f"{strat_val:.2%}" if strat_val is not None else "N/A"
                bench_val_fmt = f"{bench_val:.2%}" if bench_val is not None else "N/A"
            elif "Drawdown Duration" in label:
                strat_val_fmt = f"{strat_val}" if strat_val is not None else "N/A"
                bench_val_fmt = f"{bench_val}" if bench_val is not None else "N/A"
            else:
                strat_val_fmt = f"{strat_val:.2f}" if strat_val is not None else "N/A"
                bench_val_fmt = f"{bench_val:.2f}" if bench_val is not None else "N/A"

            print(
                f"\n{label:{label_width}} {strat_val_fmt:>{value_width}} {bench_val_fmt:>{market_width}}"
            )

        print("\n" + "=" * span)
