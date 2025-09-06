import sys

sys.path.insert(1, "algorithmic_trading_utilities")
import numpy as np
import pandas as pd

# Try different import approaches for data modules
try:
    from data.yfinance_ops import get_sp500_prices
except ImportError:
    from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices  # noqa: F401


# Try different import approaches for broker modules
try:
    from brokers.alpaca.alpaca_ops import get_portfolio_history
except ImportError:
    from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import (
        get_portfolio_history,  # noqa: F401
    )

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

        Parameters:
        -----------
        portfolio_equity : np.ndarray
            Daily portfolio equity values.
        benchmark_equity : np.ndarray, optional
            Daily benchmark equity values (for alpha/beta), default None.
        risk_free_rate : float
            Daily risk-free rate.
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
        if equity is None or len(equity) < 2:
            return np.array([])
        return np.diff(equity) / equity[:-1]

    # region - Basic Metrics & Ratios

    def average_return(self) -> float:
        return np.mean(self.returns)

    def total_return(self) -> float:
        return self.portfolio[-1] / self.portfolio[0] - 1

    def std_dev(self) -> float:
        return np.std(self.returns)

    def sharpe_ratio(self) -> float:
        return (self.average_return() - self.risk_free_rate) / self.std_dev()

    def annualised_sharpe(self) -> float:
        return self.sharpe_ratio() * np.sqrt(252)

    def downside_std(self) -> float:
        downside = self.returns[self.returns < 0]
        return np.std(downside) if len(downside) > 0 else 0.0

    def sortino_ratio(self) -> float:
        dr = self.downside_std()
        return (self.average_return() - self.risk_free_rate) / dr if dr > 0 else np.nan

    def annualised_sortino(self) -> float:
        return self.sortino_ratio() * np.sqrt(252)

    def calmar_ratio(self) -> float:
        dd = self.max_drawdown()
        return self.average_return() * 252 / dd if dd > 0 else np.nan

    # end region

    # region - Drawdowns
    def drawdown_series(self) -> np.ndarray:
        cum_max = np.maximum.accumulate(self.portfolio)
        return (cum_max - self.portfolio) / cum_max

    def max_drawdown(self) -> float:
        return np.max(self.drawdown_series())

    def average_drawdown(self) -> float:
        return np.mean(self.drawdown_series())

    def drawdown_duration(self) -> int:
        dd = self.drawdown_series()
        duration = 0
        max_duration = 0
        for d in dd:
            if d > 0:
                duration += 1
                max_duration = max(max_duration, duration)
            else:
                duration = 0
        return max_duration

    # end region

    # region - Return distribution
    def return_distribution_stats(self, alpha=0.05) -> dict:
        r = self.returns
        return {
            "skewness": skew(r),
            "kurtosis": kurtosis(r),
            "VaR": np.percentile(r, 100 * alpha),
            "CVaR": np.mean(r[r <= np.percentile(r, 100 * alpha)]),
        }

    # end region

    # region - Alpha & Beta
    def alpha_beta(self) -> dict:
        if self.benchmark_returns is None or len(self.benchmark_returns) != len(
            self.returns
        ):
            return {"alpha": np.nan, "beta": np.nan}

        y = self.returns - self.risk_free_rate
        X = self.benchmark_returns - self.risk_free_rate
        model = LinearRegression().fit(X.reshape(-1, 1), y.reshape(-1, 1))
        return {"alpha": model.intercept_[0], "beta": model.coef_[0][0]}

    def rolling_alpha_beta(self, window=252) -> pd.DataFrame:
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

    # end region

    # region - Aggregate all metrics for Strategy & Benchmark
    def calculate_all(self) -> dict:
        """
        Aggregate all performance metrics into a single dictionary.
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
        Requires benchmark equity to be provided.
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

    # end region

    # region - Report Strategy metrics & benchmarking

    def report(self):
        """
        Print a formatted table comparing strategy vs benchmark metrics.
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

        print()
        span = 54
        len_title = len("Strategy vs Benchmark Performance Comparison")
        remainder = span - len_title
        print("=" * span)
        print(
            " " * ((remainder) // 2)
            + "Strategy vs Benchmark Performance Comparison"
            + " " * (remainder // 2)
        )
        print("=" * span)

        label_width, value_width, market_width = 25, 12, 12
        print(
            f"{'':{label_width}} {'Strategy':>{value_width}} {'Benchmark':>{market_width}}"
        )
        print("-" * span)

        # List of metrics to display
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

    # end region


# region - Use Example

# metrics = PerformanceMetrics(portfolio_equity, benchmark_equity)
# strategy_metrics = metrics.calculate_all()
# benchmark_metrics = metrics.calculate_benchmark_metrics()  # new method for benchmark
# metrics.report()

# end region
