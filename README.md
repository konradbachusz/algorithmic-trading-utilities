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
```
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
from algorithmic_trading_utilities.common.portfolio_ops import (
    calculate_performance_metrics, 
    get_portfolio_and_benchmark_returns,
    get_portfolio_and_benchmark_values
)

# Get comprehensive performance metrics
metrics = calculate_performance_metrics()
print(f"Annual Sharpe Ratio: {metrics['annual_sharpe_ratio']:.2f}")
print(f"Total Return: {metrics['total_return']:.2f}%")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}")
print(f"Alpha: {metrics['alpha']:.4f}")
print(f"Beta: {metrics['beta']:.4f}")

# Compare portfolio vs S&P 500 (percentage returns)
returns_df = get_portfolio_and_benchmark_returns()
print(returns_df.tail())

# Get absolute values for portfolio vs benchmark
values_df = get_portfolio_and_benchmark_values()
print(values_df.tail())
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

## Library Structure

```
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

**Performance Metrics Functions:**
- `get_average_return(equity)` - Daily average return
- `get_total_return(equity)` - Total portfolio return percentage
- `get_cumulative_return(equity)` - Cumulative return calculation
- `get_std_dev(equity)` - Standard deviation of returns
- `get_max_drawdown(equity)` - Maximum drawdown analysis

**Risk-Adjusted Metrics:**
- `get_sharpe_ratio(avg_return, std_dev, risk_free_rate)` - Sharpe ratio
- `get_annualised_sharpe_ratio(sharpe_ratio)` - Annualized Sharpe ratio
- `get_sortino_ratio(avg_return, downside_dev, risk_free_rate)` - Sortino ratio
- `get_annualised_sortino_ratio(sortino_ratio)` - Annualized Sortino ratio
- `get_alpha(portfolio_returns, benchmark_returns, risk_free_rate)` - Alpha vs benchmark
- `get_beta(portfolio_returns, benchmark_returns)` - Beta calculation

**Comprehensive Analysis:**
- `calculate_performance_metrics()` - Returns all metrics as dictionary
- `get_portfolio_and_benchmark_values()` - Portfolio vs S&P 500 values
- `get_portfolio_and_benchmark_returns()` - Portfolio vs S&P 500 percentage returns

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

`calculate_performance_metrics()` returns:

```python
{
    'average_return': float,        # Daily average return
    'total_return': float,          # Total return percentage
    'cumulative_return': float,     # Cumulative return percentage  
    'std_dev': float,              # Standard deviation of returns
    'sharpe_ratio': float,         # Daily Sharpe ratio
    'annual_sharpe_ratio': float,  # Annualized Sharpe ratio
    'sortino_ratio': float,        # Daily Sortino ratio
    'annual_sortino_ratio': float, # Annualized Sortino ratio
    'max_drawdown': float,         # Maximum drawdown
    'alpha': float,                # Alpha vs S&P 500
    'beta': float                  # Beta vs S&P 500
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

