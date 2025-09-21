import sys
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
from sklearn.linear_model import LinearRegression

sys.path.insert(1, "algorithmic_trading_utilities")

# Try different import approaches for data modules
try:
    from data.yfinance_ops import get_sp500_prices
except ImportError:
    from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices

# Try different import approaches for broker modules
try:
    from brokers.alpaca.alpaca_ops import get_portfolio_history
except ImportError:
    from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import (
        get_portfolio_history,
    )


class PerformanceMetrics:
    """
    Performance Metrics Computation Module.

    Example:
        >>> from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics
        >>> pm = PerformanceMetrics(portfolio_equity=portfolio_series, benchmark_equity=benchmark_series)
        >>> metrics = pm.report()
    """

    def __init__(
        self,
        portfolio_equity: pd.Series = None,
        benchmark_equity: pd.Series = None,
        risk_free_rate: float = 0.02 / 252,
    ):
        """
        Initialize performance metrics calculator.

        Args:
            portfolio_equity (pd.Series, Optional): Daily portfolio equity values.
                Defaults to Alpaca portfolio equity.
            benchmark_equity (pd.Series, optional): Daily benchmark equity values.
                If provided, enables alpha/beta calculations. Defaults to None.
            risk_free_rate (float, optional): Daily risk-free rate. Defaults to 0.02/252.
        """
        if portfolio_equity is not None:
            self.portfolio = pd.Series(portfolio_equity)
        else:
            self.portfolio = get_portfolio_history()
        assert isinstance(self.portfolio.index, pd.DatetimeIndex), (
            "portfolio index must be a DatetimeIndex"
        )
        if benchmark_equity is not None:
            self.benchmark = pd.Series(benchmark_equity)
        else:
            self.benchmark = get_sp500_prices(
                start_date=self.portfolio.index[0].strftime("%Y-%m-%d"),
                end_date=self.portfolio.index[-1].strftime("%Y-%m-%d"),
            )

        self.risk_free_rate = risk_free_rate
        self.returns = self._daily_returns(self.portfolio)
        self.benchmark_returns = (
            self._daily_returns(self.benchmark) if self.benchmark is not None else None
        )

    @staticmethod
    def _daily_returns(equity: pd.Series) -> pd.Series:
        """
        Compute daily returns from equity curve.

        Args:
            equity (pd.Series): Series of equity values.

        Returns:
            pd.Series: Series of daily returns.
        """
        if equity is None or len(equity) < 2:
            return pd.Series(dtype=float)
        return equity.pct_change().dropna()

    def average_return(self) -> float:
        """Compute average daily return.

        Returns:
            float: Mean of daily returns.
        """
        return self.returns.mean()

    def total_return(self) -> float:
        """Compute cumulative portfolio return.

        Returns:
            float: Total return over the period.
        """
        return self.portfolio.iloc[-1] / self.portfolio.iloc[0] - 1

    def std_dev(self) -> float:
        """Compute standard deviation of daily returns.

        Returns:
            float: Standard deviation of daily returns.
        """
        return self.returns.std()

    def sharpe_ratio(self) -> float:
        """Compute daily Sharpe ratio.

        Returns:
            float: Daily Sharpe ratio (risk-adjusted return).
        """
        return (self.average_return() - self.risk_free_rate) / self.std_dev()

    def annualised_sharpe(self) -> float:
        """Compute annualised Sharpe ratio.

        Returns:
            float: Annualised Sharpe ratio.
        """
        return self.sharpe_ratio() * np.sqrt(252)

    def downside_std(self) -> float:
        """Compute downside deviation of returns.

        Returns:
            float: Standard deviation of negative returns.
        """
        downside = self.returns[self.returns < 0]
        return downside.std() if not downside.empty else 0.0

    def sortino_ratio(self) -> float:
        """Compute Sortino ratio.

        Returns:
            float: Sortino ratio based on downside deviation.
        """
        dr = self.downside_std()
        return (self.average_return() - self.risk_free_rate) / dr if dr > 0 else np.nan

    def annualised_sortino(self) -> float:
        """Compute annualised Sortino ratio.

        Returns:
            float: Annualised Sortino ratio.
        """
        return self.sortino_ratio() * np.sqrt(252)

    def drawdown_series(self) -> pd.Series:
        """Compute drawdown series.

        Returns:
            pd.Series: Series representing drawdown at each point in time.
        """
        cum_max = self.portfolio.cummax()
        return (cum_max - self.portfolio) / cum_max

    def max_drawdown(self) -> float:
        """Compute maximum drawdown.

        Returns:
            float: Maximum drawdown value.
        """
        return self.drawdown_series().max()

    def average_drawdown(self) -> float:
        """Compute average drawdown.

        Returns:
            float: Mean drawdown over the period.
        """
        return self.drawdown_series().mean()

    def drawdown_duration(self) -> int:
        """Compute maximum drawdown duration in days.

        Returns:
            int: Maximum consecutive days below previous peak.
        """
        dd = self.drawdown_series()
        if dd.empty:
            return 0
        is_dd = dd > 0
        boundaries = np.diff(np.concatenate(([0], is_dd.astype(int), [0])))
        run_starts, run_ends = (
            np.where(boundaries == 1)[0],
            np.where(boundaries == -1)[0],
        )
        if len(run_starts) == 0:
            return 0
        return (run_ends - run_starts).max()

    def return_distribution_stats(self, alpha=0.05) -> dict:
        """Compute return distribution statistics including skew, kurtosis, VaR, CVaR.

        Args:
            alpha (float, optional): Significance level for VaR/CVaR. Defaults to 0.05.

        Returns:
            dict: Dictionary containing skewness, kurtosis, VaR, and CVaR.
        """
        r = self.returns
        var = r.quantile(alpha)
        cvar = r[r <= var].mean()
        return {
            "skewness": skew(r),
            "kurtosis": kurtosis(r),
            "VaR": var,
            "CVaR": cvar,
        }

    def alpha_beta(self) -> dict:
        """Compute CAPM alpha and beta against benchmark.

        Returns:
            dict: Dictionary with keys 'alpha' and 'beta'.
        """
        if self.benchmark_returns is None or len(self.benchmark_returns) != len(
            self.returns
        ):
            return {"alpha": np.nan, "beta": np.nan}
        y = self.returns - self.risk_free_rate
        X = self.benchmark_returns - self.risk_free_rate
        model = LinearRegression().fit(X.values.reshape(-1, 1), y.values.reshape(-1, 1))
        return {"alpha": model.intercept_[0], "beta": model.coef_[0][0]}

    def rolling_alpha_beta(self, window: int = 252) -> pd.DataFrame:
        """Compute rolling alpha and beta over a specified window.

        Args:
            window (int, optional): Rolling window size in days. Defaults to 252.

        Returns:
            pd.DataFrame: DataFrame with columns 'alpha' and 'beta'.
        """
        if self.benchmark_returns is None or len(self.benchmark_returns) < window:
            return pd.DataFrame(columns=["alpha", "beta"])
        alphas, betas = [], []
        for i in range(len(self.returns) - window + 1):
            y = self.returns.iloc[i : i + window] - self.risk_free_rate
            X = self.benchmark_returns.iloc[i : i + window] - self.risk_free_rate
            model = LinearRegression().fit(
                X.values.reshape(-1, 1), y.values.reshape(-1, 1)
            )
            alphas.append(model.intercept_[0])
            betas.append(model.coef_[0][0])
        index = self.returns.index[window - 1 :]
        return pd.DataFrame({"alpha": alphas, "beta": betas}, index=index)

    def calmar_ratio(self) -> float:
        """Compute Calmar ratio (annual return / max drawdown).

        Returns:
            float: Calmar ratio value.
        """
        dd = self.max_drawdown()
        return self.average_return() * 252 / dd if dd > 0 else np.nan

    def calculate_all(self) -> dict:
        """Aggregate all performance metrics into a dictionary.

        Returns:
            dict: Dictionary of all portfolio performance metrics.
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
        """Compute benchmark performance metrics.

        Returns:
            dict: Dictionary of benchmark performance metrics.
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
        """Print a formatted performance comparison table between strategy and benchmark."""
        if self.benchmark is None:
            print("Benchmark equity not provided. Cannot generate comparison report.")
            return

        strategy_metrics = self.calculate_all()

        original_portfolio, original_returns = self.portfolio, self.returns
        self.portfolio, self.returns = self.benchmark, self.benchmark_returns
        benchmark_metrics = self.calculate_benchmark_metrics()
        self.portfolio, self.returns = original_portfolio, original_returns

        title = "Strategy vs Benchmark Performance Comparison"
        span = 54
        remainder = span - len(title)
        print("=" * span)
        print(" " * (remainder // 2) + title + " " * (remainder // 2))
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

            if (
                "Return" in label
                or "Drawdown" in label
                or "VaR" in label
                or "CVaR" in label
                or "Alpha" in label
            ):
                strat_val_fmt = f"{strat_val:.2%}" if pd.notna(strat_val) else "N/A"
                bench_val_fmt = f"{bench_val:.2%}" if pd.notna(bench_val) else "N/A"
            elif "Drawdown Duration" in label:
                strat_val_fmt = f"{strat_val}" if pd.notna(strat_val) else "N/A"
                bench_val_fmt = f"{bench_val}" if pd.notna(bench_val) else "N/A"
            else:
                strat_val_fmt = f"{strat_val:.2f}" if pd.notna(strat_val) else "N/A"
                bench_val_fmt = f"{bench_val:.2f}" if pd.notna(bench_val) else "N/A"

            print(
                f"\n{label:{label_width}} {strat_val_fmt:>{value_width}} {bench_val_fmt:>{market_width}}"
            )

        print("\n" + "=" * span)
