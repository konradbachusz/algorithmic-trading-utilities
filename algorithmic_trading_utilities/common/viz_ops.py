from typing import Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics


class PerformanceViz:
    """
    Visualization helpers for portfolio performance and risk.

    Accepts raw equity Series or an existing PerformanceMetrics instance.

    Example:
        >>> viz = PerformanceViz(portfolio_equity=portfolio, benchmark_equity=benchmark)
        >>> viz.plot_equity_curve()
        >>> viz.plot_underwater()
    """

    def __init__(
        self,
        portfolio_equity: Optional[pd.Series] = None,
        benchmark_equity: Optional[pd.Series] = None,
        pm: Optional[PerformanceMetrics] = None,
    ):
        """Initialize PerformanceViz.

        Args:
            portfolio_equity (Optional[pd.Series]): Equity curve of the portfolio.
            benchmark_equity (Optional[pd.Series]): Equity curve of the benchmark.
            pm (Optional[PerformanceMetrics]): Pre-computed PerformanceMetrics instance.

        Raises:
            ValueError: If neither portfolio_equity nor pm is provided.
        """
        if pm is not None:
            self.pm = pm
            self.portfolio = self.pm.portfolio
            self.benchmark = self.pm.benchmark
        else:
            if portfolio_equity is None:
                raise ValueError("portfolio_equity or pm must be provided")
            self.portfolio = portfolio_equity
            self.benchmark = benchmark_equity
            self.pm = PerformanceMetrics(
                self.portfolio.values,
                self.benchmark.values if self.benchmark is not None else None,
            )

    @staticmethod
    def _make_fig(title: str, figsize: Tuple[int, int] = (10, 5)) -> plt.Figure:
        """Create a matplotlib Figure with a title.

        Args:
            title (str): Plot title.
            figsize (Tuple[int, int], optional): Figure size. Defaults to (10, 5).

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(title)
        return fig

    @staticmethod
    def format(value: float, currency: str = "$") -> str:
        """Format a numeric value into human-readable currency string.

        Args:
            value (float): Numeric value to format.
            currency (str, optional): Currency symbol. Defaults to "$".

        Returns:
            str: Formatted currency string.
        """
        abs_value = abs(value)
        sign = "-" if value < 0 else ""
        if abs_value >= 1_000_000_000:
            return f"{sign}{currency}{abs_value / 1_000_000_000:.2f}B"
        elif abs_value >= 1_000_000:
            return f"{sign}{currency}{abs_value / 1_000_000:.2f}M"
        elif abs_value >= 1_000:
            return f"{sign}{currency}{abs_value / 1_000:.2f}K"
        else:
            return f"{sign}{currency}{abs_value:.2f}"

    def plot_equity_curve(
        self, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot equity curve for portfolio and benchmark.

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Equity Curve")
        ax = fig.axes[0]
        ax.plot(self.portfolio.index, self.portfolio.values, label="Strategy")
        if self.benchmark is not None:
            ax.plot(self.benchmark.index, self.benchmark.values, label="Benchmark")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: self.format(y)))
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity")
        ax.legend()
        ax.grid(True)
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_equity_with_drawdowns(
        self, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot portfolio equity curve highlighting drawdown periods.

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Portfolio Equity with Drawdowns")
        ax = fig.axes[0]

        dd = self.pm.drawdown_series()
        x = self.portfolio.index

        ax.plot(x, self.portfolio.values, label="Portfolio")

        in_dd = dd > 0
        if in_dd.any():
            boundaries = np.diff(np.concatenate(([0], in_dd.astype(int), [0])))
            start_idx = np.where(boundaries == 1)[0]
            end_idx = np.where(boundaries == -1)[0]
            labeled = False
            for s, e in zip(start_idx, end_idx):
                top = self.portfolio.values[s - 1]
                bottom = self.portfolio.values[s:e]
                if not labeled:
                    ax.fill_between(
                        x[s:e],
                        bottom,
                        top,
                        alpha=0.3,
                        color="red",
                        label="Drawdown",
                    )
                    labeled = True
                else:
                    ax.fill_between(
                        x[s:e],
                        bottom,
                        top,
                        alpha=0.3,
                        color="red",
                    )
                ax.hlines(
                    y=top,
                    xmin=x[s - 1],
                    xmax=x[e - 1],
                    colors="red",
                    linewidth=1,
                )

        ax.set_xlabel("Date")
        ax.set_ylabel("Equity")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: self.format(y)))
        ax.grid(True)
        ax.legend()
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_drawdown_series(
        self, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot drawdown series with maximum drawdown highlighted.

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Drawdown Series")
        ax = fig.axes[0]
        dd = -1 * self.pm.drawdown_series()
        x = self.portfolio.index
        ax.plot(x, dd, label="Drawdown")
        ax.fill_between(x, dd, 0, alpha=0.3)
        max_dd_idx = np.argmin(dd)
        ax.plot(
            x[max_dd_idx],
            dd.iloc[max_dd_idx],
            marker="*",
            color="red",
            markersize=12,
            label="Max Drawdown",
        )
        ax.annotate(
            f"{dd.iloc[max_dd_idx]:.2%}",
            xy=(x[max_dd_idx], dd.iloc[max_dd_idx]),
            xytext=(7, -2),
            textcoords="offset points",
            color="red",
            fontsize=10,
        )
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        ax.set_xlabel("Date")
        ax.set_ylabel("Drawdown (fraction)")
        ax.grid(True)
        ax.legend()
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_cumulative_returns_timeseries(
        self, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot cumulative returns time series for portfolio and benchmark.

        Returns are calculated as: (Current Value - Starting Value) / Starting Value * 100

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Cumulative Returns Time Series")
        ax = fig.axes[0]

        # Calculate cumulative returns as percentage change from start
        portfolio_returns = (
            (self.portfolio - self.portfolio.iloc[0]) / self.portfolio.iloc[0] * 100
        )
        ax.plot(
            portfolio_returns.index,
            portfolio_returns.values,
            label="Portfolio Returns",
            alpha=0.7,
        )

        if self.benchmark is not None and len(self.benchmark) > 0:
            benchmark_returns = (
                (self.benchmark - self.benchmark.iloc[0]) / self.benchmark.iloc[0] * 100
            )
            ax.plot(
                benchmark_returns.index,
                benchmark_returns.values,
                label="Benchmark Returns",
                alpha=0.7,
            )

        ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Returns (%)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_rolling_volatility(
        self, window: int = 63, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot Rolling Volatility of daily returns for portfolio and benchmark.

        Args:
            window (int, optional): Rolling window length in days. Defaults to 63.
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig(f"Rolling Volatility ({window} days)")
        ax = fig.axes[0]
        vol = self.pm.returns.rolling(window).std()
        ax.plot(vol.index, vol, label="Portfolio Volatility")
        benchmark_vol = self.pm.benchmark_returns.rolling(window).std()
        ax.plot(benchmark_vol.index, benchmark_vol, label="Benchmark Volatility")
        ax.set_xlabel("Date")
        ax.set_ylabel("Volatility")
        ax.grid(True)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        ax.legend()
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_returns_distribution(
        self, bins: int = 50, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot distribution of daily returns for portfolio and benchmark.

        Args:
            bins (int, optional): Number of histogram bins. Defaults to 50.
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Daily Returns Distribution")
        ax = fig.axes[0]
        r = pd.Series(self.pm.returns)
        ax.hist(r.dropna(), bins=bins, alpha=0.7, label="Strategy", density=False)
        if self.pm.benchmark_returns is not None:
            b = pd.Series(self.pm.benchmark_returns)
            ax.hist(b.dropna(), bins=bins, alpha=0.4, label="Benchmark", density=False)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: "{:.0%}".format(y)))
        ax.set_xlabel("Daily Return")
        ax.set_ylabel("Frequency")
        ax.legend()
        ax.grid(True)
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_monthly_returns_heatmap(
        self, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot a heatmap of monthly returns (strategy) with blue color scale,
        squares, no colorbar, and light grey for missing months annotated with '-'.

        Args:
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig("Monthly Returns Heatmap")
        ax = fig.axes[0]
        monthly = self.portfolio.resample("M").last().pct_change()
        df = monthly.to_frame(name="Return")
        df["Year"] = df.index.year
        df["Month"] = df.index.month

        pivot = df.pivot(index="Year", columns="Month", values="Return")

        data = pivot.copy()
        data_filled = data.fillna(-999)

        cmap = sns.color_palette("Blues", as_cmap=True)
        data_filled == -999
        sns.heatmap(
            data_filled.replace(-999, np.nan),
            annot=True,
            fmt=".1%",
            cmap=cmap,
            linewidths=0.5,
            linecolor="white",
            square=True,
            cbar=False,
            ax=ax,
        )

        ax.set_ylabel("Year")
        ax.set_xlabel("Month")
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        ax.set_xticklabels(month_names)
        ax.set_yticklabels(data.index, rotation=0)
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_rolling_sharpe(
        self, window: int = 63, show: bool = True, savepath: Optional[str] = None
    ) -> plt.Figure:
        """Plot rolling Sharpe ratio over a specified window.

        Args:
            window (int, optional): Rolling window length in days. Defaults to 63.
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plot. Defaults to None.

        Returns:
            plt.Figure: Matplotlib Figure object.
        """
        fig = self._make_fig(f"Rolling Sharpe ({window} days)")
        ax = fig.axes[0]
        rolling_sharpe = self.pm.rolling_sharpe(window)

        ax.plot(
            rolling_sharpe.index,
            rolling_sharpe.values,
            label=f"Rolling Sharpe ({window})",
        )
        ax.axhline(0, linestyle="--")
        ax.set_xlabel("Date")
        ax.set_ylabel("Rolling Sharpe")
        ax.grid(True)
        ax.legend()
        if savepath:
            fig.savefig(savepath, bbox_inches="tight")
        if show:
            plt.show()
        return fig

    def plot_rolling_alpha_beta(
        self, window: int = 252, show: bool = True, savepath: Optional[str] = None
    ) -> Tuple[plt.Figure, plt.Figure]:
        """Plot rolling alpha and beta relative to benchmark.

        Args:
            window (int, optional): Rolling window length in days. Defaults to 252.
            show (bool, optional): Whether to display the plot. Defaults to True.
            savepath (Optional[str], optional): Path to save the plots. Defaults to None.

        Raises:
            ValueError: If benchmark returns are not available.

        Returns:
            Tuple[plt.Figure, plt.Figure]: Figures for alpha and beta plots.
        """
        if self.pm.benchmark_returns is None:
            raise ValueError("Benchmark returns required for rolling alpha/beta")

        df = self.pm.rolling_alpha_beta(window=window)

        # Alpha
        fig_a = self._make_fig(f"Rolling Alpha ({window} days)")
        ax_a = fig_a.axes[0]
        ax_a.plot(df.index, df["alpha"])
        ax_a.axhline(0, linestyle="--")
        ax_a.set_xlabel("Date")
        ax_a.set_ylabel("Alpha")
        ax_a.grid(True)
        ax_a.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        ax_a.legend([f"Rolling Alpha ({window})"])

        # Beta
        fig_b = self._make_fig(f"Rolling Beta ({window} days)")
        ax_b = fig_b.axes[0]
        ax_b.plot(df.index, df["beta"])
        ax_b.axhline(1, linestyle="--")
        ax_b.set_xlabel("Date")
        ax_b.set_ylabel("Beta")
        ax_b.grid(True)
        ax_b.legend([f"Rolling Beta ({window})"])

        if savepath:
            fig_a.savefig(savepath.replace(".png", "_alpha.png"), bbox_inches="tight")
            fig_b.savefig(savepath.replace(".png", "_beta.png"), bbox_inches="tight")
        if show:
            plt.show()
        return fig_a, fig_b

    def create_all_plots(
        self, show: bool = True, out_prefix: Optional[str] = None
    ) -> list:
        """Generate all performance plots and return the figures.

        Args:
            show (bool, optional): Whether to display plots. Defaults to True.
            out_prefix (Optional[str], optional): Prefix for saving plots. Defaults to None.

        Returns:
            list: List of Matplotlib Figures.
        """
        figs = []
        figs.append(
            self.plot_cumulative_returns_timeseries(
                show=show,
                savepath=(
                    (out_prefix + "_returns_timeseries.png") if out_prefix else None
                ),
            )
        )
        figs.append(
            self.plot_equity_curve(
                show=show, savepath=(out_prefix + "_equity.png") if out_prefix else None
            )
        )
        figs.append(
            self.plot_equity_with_drawdowns(
                show=show,
                savepath=(out_prefix + "_equity_dd.png") if out_prefix else None,
            )
        )
        figs.append(
            self.plot_drawdown_series(
                show=show,
                savepath=(out_prefix + "_drawdown.png") if out_prefix else None,
            )
        )
        figs.append(
            self.plot_rolling_volatility(
                show=show,
                savepath=(
                    (out_prefix + "_rolling_volatility.png") if out_prefix else None
                ),
            )
        )
        figs.append(
            self.plot_returns_distribution(
                show=show,
                savepath=(out_prefix + "_returns.png") if out_prefix else None,
            )
        )
        figs.append(
            self.plot_rolling_sharpe(
                show=show,
                savepath=(out_prefix + "_rolling_sharpe.png") if out_prefix else None,
            )
        )
        try:
            a, b = self.plot_rolling_alpha_beta(
                show=show,
                savepath=(out_prefix + "_rolling_ab.png") if out_prefix else None,
            )
            figs.extend([a, b])
        except ValueError:
            pass
        return figs
