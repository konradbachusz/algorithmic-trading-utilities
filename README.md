# Algorithmic Trading Utilities

A comprehensive Python library for algorithmic trading with Alpaca API and Yahoo Finance integration. This repository provides utilities for portfolio analytics, data retrieval, order management, position handling, visualization, and automated notifications.

## Features

- **Portfolio Analytics**: Calculate performance metrics including Sharpe ratio, Sortino ratio, alpha, beta, and maximum drawdown
- **Order Management**: Place market, limit, and trailing stop orders with comprehensive error handling
- **Position Management**: Monitor positions, manage trailing stops, and close positions based on thresholds
- **Data Management**: Historical and real-time data from Alpaca and Yahoo Finance APIs
- **Quantitative Tools**: Correlation analysis and data preprocessing utilities
- **Email Notifications**: Automated alerts for trade execution and system events
- **Yahoo Finance Integration**: Access to market screeners and S&P 500 benchmark data
- **Visualization Tools**: Time series plotting and portfolio comparison charts
- **Broker Integration**: Seamless integration with Alpaca trading platform

## Installation

### For Local Development

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/algorithmic-trading-utilities.git
   cd algorithmic-trading-utilities
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

### Using as a Dependency in Your Project

#### Method 1: Install directly via pip

```bash
pip install git+https://github.com/your-username/algorithmic-trading-utilities.git
```

#### Method 2: Add to requirements.txt

Add this line to your project's `requirements.txt`:

```bash
git+https://github.com/your-username/algorithmic-trading-utilities.git
```

Then install with:

```bash
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in your project root:

```bash
PAPER_KEY="your_alpaca_paper_api_key"
PAPER_SECRET="your_alpaca_paper_secret_key"
web_app_email="your_sender_email@gmail.com"
web_app_email_password="your_gmail_app_password"
recipient_email="your_recipient_email@gmail.com"
```

## Usage Examples

### Portfolio Performance Analysis

```python
from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics

# Initialize PerformanceMetrics with portfolio and optional benchmark
pm = PerformanceMetrics(portfolio_equity=portfolio_series, benchmark_equity=benchmark_series)

# Get comprehensive performance metrics
metrics = pm.report()
```

### Order Management

```python
from algorithmic_trading_utilities.brokers.alpaca.orders import (
    place_order,
    get_orders,
    cancel_orders,
    place_trailing_stop_order,
    cancel_order_by_symbol
)

# Place a market order
market_order = place_order(
    symbol="AAPL",
    quantity=10,
    side="buy",
    type="MarketOrderRequest",
    time_in_force="gtc"
)

# Place a limit order
limit_order = place_order(
    symbol="AAPL",
    quantity=10,
    side="buy", 
    type="LimitOrderRequest",
    time_in_force="day",
    limit_price=150.00
)

# Place a trailing stop order
trailing_stop = place_trailing_stop_order(
    symbol="AAPL",
    quantity=10,
    side="buy",
    trail_percent="5"
)

# Get all open orders
open_orders = get_orders()
print(f"Found {len(open_orders)} open orders")

# Cancel all orders
canceled_count = cancel_orders()
print(f"Canceled {canceled_count} orders")

# Cancel orders for specific symbol
cancel_order_by_symbol("AAPL")
```

### Position Management

```python
from algorithmic_trading_utilities.brokers.alpaca.positions import (
    get_open_positions,
    get_positions_without_trailing_stop_loss,
    close_positions_below_threshold
)
from algorithmic_trading_utilities.common.config import loss_threshold

# Get all open positions
positions = get_open_positions()
for pos in positions:
    print(f"Symbol: {pos['symbol']}, Qty: {pos['quantity']}, Side: {pos['side']}")

# Find positions without trailing stop protection
unprotected = get_positions_without_trailing_stop_loss()
print(f"Found {len(unprotected)} positions without trailing stops")

# Close losing positions (uses loss_threshold from config)
closed_count = close_positions_below_threshold(loss_threshold)
print(f"Closed {closed_count} positions below threshold")
```

### Data Retrieval

```python
from algorithmic_trading_utilities.data.get_data import (
    get_assets, 
    get_historical_data, 
    get_last_price,
    get_asset_list
)
from algorithmic_trading_utilities.data.yfinance_ops import (
    get_sp500_prices,
    get_stock_gainers_table
)
from algorithmic_trading_utilities.common.config import trading_client
from alpaca.data.historical.stock import StockHistoricalDataClient

# Initialize data client
data_client = StockHistoricalDataClient("your_key", "your_secret")

# Get available assets
assets = get_assets(trading_client)
asset_symbols = get_asset_list(assets)
print(f"Found {len(asset_symbols)} tradeable assets")

# Get historical data for a specific stock
historical_data = get_historical_data("AAPL", data_client)
print(historical_data.head())

# Get current price
current_price = get_last_price("AAPL", data_client)
print(f"AAPL current price: ${current_price}")

# Get S&P 500 benchmark data
sp500_data = get_sp500_prices("2024-01-01")
print(sp500_data.tail())

# Get today's top gainers (with retry logic for rate limits)
gainers_df = get_stock_gainers_table()
print(f"Found {len(gainers_df)} large-cap gainers today")
print(gainers_df[['symbol', 'shortName', 'regularMarketChangePercent']].head())
```

### Quantitative Analysis

```python
from algorithmic_trading_utilities.common.quantitative_tools import (
    remove_highly_correlated_columns
)
import pandas as pd

# Remove highly correlated features
data = {'A': [1, 2, 3, 4, 5], 'B': [2, 3, 4, 5, 6], 'C': [0, 5, 1, 3, 6]}
df = pd.DataFrame(data)

# Remove columns with correlation > 0.9
cleaned_df = remove_highly_correlated_columns(df, threshold=0.9)
print(f"Reduced from {len(df.columns)} to {len(cleaned_df.columns)} columns")
```

### Visualization

```python
from algorithmic_trading_utilities.common.viz_ops import (
    plot_time_series, 
    compare_portfolio_and_benchmark,
    plot_portfolio
)

# Plot portfolio vs benchmark comparison
comparison_df = get_portfolio_and_benchmark_values()
compare_portfolio_and_benchmark(comparison_df, "Portfolio vs S&P 500")

# Plot portfolio returns (handles both Series and DataFrame)
returns_df = get_portfolio_and_benchmark_returns()
plot_portfolio(returns_df["Portfolio"])

# Plot any time series data
plot_time_series(comparison_df)
```

### Email Notifications

```python
from algorithmic_trading_utilities.common.email_ops import send_email_notification

# Send success notification
send_email_notification(
    subject="Trade Execution",
    notification="Successfully placed buy order for AAPL at $150.25",
    type="SUCCESS"
)

# Send failure notification
send_email_notification(
    subject="System Alert",
    notification="Failed to connect to market data API",
    type="FAILURE"
)
```

## Example Usage

### Performance Metrics

```python
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from algorithmic_trading_utilities.common.portfolio_ops import PerformanceMetrics
from algorithmic_trading_utilities.common.viz_ops import PerformanceViz
from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import get_portfolio_history
from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices


# Get actual portfolio history
portfolio_history = get_portfolio_history()
portfolio_equity = pd.Series(
    data=portfolio_history.equity,
    index=pd.to_datetime(portfolio_history.timestamp, unit='s'),
    name="portfolio_equity"
)

# Get S&P 500 benchmark data
benchmark_data = get_sp500_prices("2025-04-08")
benchmark_equity = pd.Series(
    data=benchmark_data.iloc[:, 0].values,
    index=pd.to_datetime(benchmark_data.index),
    name="benchmark_equity"
)

# Align indices to common dates
common_dates = portfolio_equity.index.intersection(benchmark_equity.index)
portfolio_equity = portfolio_equity.loc[common_dates]
benchmark_equity = benchmark_equity.loc[common_dates]

# Normalize benchmark to start at same value as portfolio
benchmark_equity = benchmark_equity / benchmark_equity.iloc[0] * portfolio_equity.iloc[0]

pm = PerformanceMetrics(portfolio_equity, benchmark_equity)
metrics = pm.calculate_all()

viz = PerformanceViz(pm=pm, benchmark_equity=benchmark_equity)
fig_equity = viz.create_all_plots(True)

print("Performance Metrics:")
for key, value in metrics.items():
    print(f"{key}: {value}")
```

## Library Structure

```bash
algorithmic_trading_utilities/
├── data/
│   ├── get_data.py          # Alpaca data operations
│   └── yfinance_ops.py      # Yahoo Finance integration
├── brokers/
│   └── alpaca/
│       ├── alpaca_ops.py    # Portfolio history operations
│       ├── orders.py        # Order management
│       └── positions.py     # Position management
├── common/
│   ├── portfolio_ops.py     # Portfolio analytics
│   ├── quantitative_tools.py # Data analysis utilities
│   ├── email_ops.py         # Email notifications
│   ├── viz_ops.py           # Visualization utilities
│   └── config.py            # Configuration and API setup
└── tests/                   # Comprehensive test suite
```

## Core Modules

### Portfolio Analytics (`common.portfolio_ops`)

**Performance Metrics Methods:**

- `average_return()` – Daily average return
- `total_return()` – Total portfolio return from start to end
- `std_dev()` – Standard deviation of returns
- `max_drawdown()` – Maximum drawdown (fraction)
- `average_drawdown()` – Average drawdown (fraction)
- `drawdown_duration()` – Longest duration of continuous drawdown

**Risk-Adjusted Metrics:**

- `sharpe_ratio()` – Daily Sharpe ratio
- `annualised_sharpe()` – Annualized Sharpe ratio
- `sortino_ratio()` – Daily Sortino ratio
- `annualised_sortino()` – Annualized Sortino ratio
- `calmar_ratio()` – Annual return divided by max drawdown
- `alpha_beta()` – CAPM alpha and beta vs benchmark
- `rolling_alpha_beta(window=252)` – Rolling alpha and beta over a specified window

**Return Distribution Metrics:**

- `return_distribution_stats(alpha=0.05)` – Skewness, kurtosis, VaR, and CVaR

**Comprehensive Analysis:**

- `calculate_all()` – Returns all performance metrics as a dictionary
- `calculate_benchmark_metrics()` – Returns benchmark metrics (alpha=0, beta=1 if benchmark provided)
- `report()` – Prints a formatted comparison of strategy vs benchmark metrics

### Order Management (`brokers.alpaca.orders`)

**Order Placement:**

- `place_order(symbol, quantity, side, type, time_in_force, **kwargs)` - Place various order types
- `place_trailing_stop_order(symbol, quantity, side, trail_percent)` - Trailing stops

**Order Retrieval:**

- `get_orders()` - Get all open orders
- `get_current_trailing_stop_orders()` - Get active trailing stop orders
- `get_orders_symbol_list(orders)` - Extract symbols from orders
- `get_orders_to_cancel()` - Identify non-trailing stop orders

**Order Cancellation:**

- `cancel_orders()` - Cancel all orders with retry logic
- `cancel_order_by_symbol(symbol)` - Cancel orders for specific symbol

### Position Management (`brokers.alpaca.positions`)

**Position Retrieval:**

- `get_open_positions()` - Get all open positions with formatted data
- `get_positions_without_trailing_stop_loss()` - Find unprotected positions
- `get_positions_symbol_list(positions)` - Extract symbols from positions

**Position Management:**

- `close_positions_below_threshold(threshold)` - Close losing positions

### Data Operations (`data/`)

#### Alpaca Data (`get_data.py`)

- `get_assets(trading_client)` - Retrieve tradeable assets
- `get_asset_list(assets)` - Extract asset symbols from assets
- `get_historical_data(symbol, client)` - Historical price data (365 days)
- `get_last_price(symbol, client)` - Most recent closing price
- `get_asset_df(assets)` - Convert asset data to DataFrame

#### Yahoo Finance (`yfinance_ops.py`)

- `get_sp500_prices(start_date)` - S&P 500 benchmark data
- `get_stock_gainers_table()` - Daily large-cap gainers with retry logic

### Quantitative Tools (`common.quantitative_tools`)

- `remove_highly_correlated_columns(df, threshold)` - Remove correlated features

### Visualization (`common.viz_ops`)

- `plot_time_series(df)` - General time series plotting
- `compare_portfolio_and_benchmark(df, title)` - Portfolio vs benchmark charts
- `plot_portfolio(df)` - Portfolio-specific plotting (handles Series/DataFrame)

### Email Notifications (`common.email_ops`)

- `send_email_notification(subject, message, type)` - Gmail SMTP notifications with timestamps

### Configuration (`common.config`)

- Trading client setup with paper trading configuration
- Threshold settings (`loss_threshold`, `trailing_stop_loss_threshold`)
- API key management with environment variables

## Configuration Variables

**Default Thresholds (from `config.py`):**

```python
loss_threshold = 0.05  # 5% loss threshold for closing positions
trailing_stop_loss_threshold = 0.1  # 10% trailing stop threshold
```

**Environment Variables Required:**

```bash
# Alpaca API (Paper Trading)
PAPER_KEY="your_alpaca_paper_api_key"
PAPER_SECRET="your_alpaca_paper_secret_key"

# Email configuration
web_app_email="your_sender_email@gmail.com"
web_app_email_password="your_app_password"
recipient_email="your_recipient_email@gmail.com"
```

## Performance Metrics Dictionary

`calculate_all()` returns:

```python
{
    'average_return': float,        # Daily average return
    'total_return': float,          # Total return from start to end
    'std_dev': float,               # Standard deviation of returns
    'sharpe_ratio': float,          # Daily Sharpe ratio
    'annualised_sharpe': float,     # Annualized Sharpe ratio
    'sortino_ratio': float,         # Daily Sortino ratio
    'annualised_sortino': float,    # Annualized Sortino ratio
    'max_drawdown': float,          # Maximum drawdown (fraction)
    'average_drawdown': float,      # Average drawdown (fraction)
    'drawdown_duration': int,       # Longest duration of continuous drawdown
    'skewness': float,              # Skewness of daily returns
    'kurtosis': float,              # Kurtosis of daily returns
    'VaR_5%': float,                # Value at Risk (5% quantile)
    'CVaR_5%': float,               # Conditional Value at Risk (average of worst 5%)
    'calmar_ratio': float,          # Annual return / max drawdown
    'alpha': float,                 # Alpha vs benchmark
    'beta': float                   # Beta vs benchmark
}
```

## Yahoo Finance Screeners

The library provides access to 200+ market screeners including popular ones like:

**Momentum Screeners:**

- `day_gainers` - Daily top gainers
- `day_losers` - Daily top losers  
- `small_cap_gainers` - Small cap momentum
- `most_actives` - Highest volume stocks

**Value Screeners:**

- `undervalued_large_caps` - Value large caps
- `fair_value_screener` - Undervalued with strong growth
- `undervalued_growth_stocks` - Growth at reasonable prices

**Sector Screeners:**

- `growth_technology_stocks` - Tech growth plays
- `ms_technology`, `ms_healthcare`, `ms_energy` - Sector-specific
- `top_energy_us` - Energy sector leaders

**Investment Vehicles:**

- `top_etfs` - Top performing ETFs
- `high_yield_bond` - High-yield bond funds

*Note: `get_stock_gainers_table()` currently uses `day_gainers` filtered for large-cap stocks (market cap >= $10B) with exponential backoff retry logic for rate limiting.*

## Testing

Run the comprehensive test suite:

```bash
pytest tests/ -v -s
```

**Test Coverage:**

- `test_portfolio_ops.py` - Portfolio analytics and metrics (including alpha/beta)
- `test_orders.py` - Order management functionality
- `test_positions.py` - Position management operations
- `test_get_data.py` - Alpaca data retrieval
- `test_yfinance_ops.py` - Yahoo Finance operations
- `test_quantitative_tools.py` - Quantitative analysis utilities
- `test_viz_ops.py` - Visualization functions
- `test_email_ops.py` - Email notification system

## Error Handling

The library includes robust error handling:

- **Rate Limiting**: Exponential backoff retry logic for Yahoo Finance API
- **Empty Data**: Graceful handling of empty DataFrames/Series
- **API Failures**: Defensive programming for network issues with APIError handling
- **Data Type Flexibility**: Functions handle both Series and DataFrame inputs
- **Missing Data**: Returns appropriate defaults (None, empty DataFrame)
- **Order Management**: Comprehensive error handling for trading operations
- **Email Notifications**: Built-in success/failure notification system

## Risk Disclaimer

**⚠️ Important Notice:** This software is for educational and research purposes only. Algorithmic trading involves substantial risk of loss and is not suitable for all investors. Always:

1. Test strategies thoroughly with paper trading
2. Never risk more than you can afford to lose
3. Understand the risks of automated trading systems
4. Consult with financial professionals before live trading

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Add comprehensive tests for new functionality
4. Run the test suite: `pytest tests/ -v -s`
5. Format code: `black .`
6. Submit a pull request with detailed description

## Support

For issues and questions:

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check docstrings in each module
- **Examples**: Review usage patterns in this README
- **Tests**: Examine test files for implementation examples

## Changelog

- **Current Version**: Added order and position management, quantitative tools, comprehensive error handling
- **Portfolio Analytics**: Full suite including alpha/beta calculations vs S&P 500
- **Yahoo Finance**: Market screener integration with rate limiting and retry logic
- **Email System**: Gmail SMTP notifications with timestamps for trading events
- **Testing**: Comprehensive test suite with mocking for all modules
- **Configuration**: Centralized config with environment variable management
