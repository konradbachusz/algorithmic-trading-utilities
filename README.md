# Algorithmic Trading Utilities

A comprehensive Python library for algorithmic trading with Alpaca API and Yahoo Finance integration. This repository provides utilities for portfolio analytics, data retrieval, visualization, and automated notifications.

## Features

- **Portfolio Analytics**: Calculate performance metrics including Sharpe ratio, Sortino ratio, alpha, beta, and maximum drawdown
- **Data Management**: Historical and real-time data from Alpaca and Yahoo Finance APIs
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
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.client import TradingClient

# Initialize clients
trading_client = TradingClient("your_key", "your_secret", paper=True)
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
```

### Yahoo Finance Market Screening

```python
from algorithmic_trading_utilities.data.yfinance_ops import get_stock_gainers_table

# Get today's top large-cap gainers (market cap >= $10B)
# Includes retry logic for rate limiting
gainers_df = get_stock_gainers_table()
print(f"Found {len(gainers_df)} large-cap gainers today")
print(gainers_df.head())

# Available columns:
# - exchange, symbol, shortName
# - regularMarketChangePercent
# - fiftyDayAverageChangePercent
```

### Visualization

```python
from algorithmic_trading_utilities.common.viz_ops import (
    plot_time_series, 
    compare_portfolio_and_benchmark,
    plot_portfolio
)
from algorithmic_trading_utilities.common.portfolio_ops import (
    get_portfolio_and_benchmark_values,
    get_portfolio_and_benchmark_returns
)

# Plot portfolio vs benchmark comparison
comparison_df = get_portfolio_and_benchmark_values()
compare_portfolio_and_benchmark(comparison_df, "Portfolio vs S&P 500")

# Plot portfolio returns (handles both Series and DataFrame)
returns_df = get_portfolio_and_benchmark_returns()
plot_portfolio(returns_df["Portfolio"])  # Handles Series input

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

### Broker Integration

```python
from algorithmic_trading_utilities.brokers.alpaca.alpaca_ops import get_portfolio_history

# Get portfolio history from Alpaca
portfolio_history = get_portfolio_history()
equity_values = portfolio_history.equity
print(f"Current portfolio value: ${equity_values[-1]}")
print(f"Portfolio equity history: {len(equity_values)} data points")
```

## Library Structure

```
algorithmic_trading_utilities/
├── data/
│   ├── get_data.py          # Alpaca data operations
│   └── yfinance_ops.py      # Yahoo Finance integration
├── brokers/
│   └── alpaca/
│       └── alpaca_ops.py    # Alpaca portfolio operations
├── common/
│   ├── portfolio_ops.py     # Portfolio analytics
│   ├── email_ops.py         # Email notifications
│   └── viz_ops.py           # Visualization utilities
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

### Visualization (`common.viz_ops`)
- `plot_time_series(df)` - General time series plotting
- `compare_portfolio_and_benchmark(df, title)` - Portfolio vs benchmark charts
- `plot_portfolio(df)` - Portfolio-specific plotting (handles Series/DataFrame)

### Email Notifications (`common.email_ops`)
- `send_email_notification(subject, message, type)` - Gmail SMTP notifications with timestamps

### Broker Integration (`brokers.alpaca.alpaca_ops`)
- `get_portfolio_history()` - Alpaca portfolio history retrieval

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

*Note: `get_stock_gainers_table()` currently uses `day_gainers` filtered for large-cap stocks (market cap >= $10B) with retry logic for rate limiting.*

## Configuration

**Required Environment Variables:**
```bash
# Alpaca API (Paper Trading)
PAPER_KEY="your_alpaca_paper_api_key"
PAPER_SECRET="your_alpaca_paper_secret_key"

# Email configuration
web_app_email = "your_sender_email@gmail.com"
web_app_email_password = "your_app_password"
recipient_email = "your_recipient_email@gmail.com"
```

**Default Configuration:**
- Portfolio history: From 2025-04-08 to present (configurable)
- Risk-free rate: 2% annual (0.02/252 daily)
- Historical data: 365 days lookback
- Email: Gmail SMTP with SSL on port 465

## Testing

Run the comprehensive test suite:
```bash
pytest tests/ -v -s
```

**Test Coverage:**
- `test_portfolio_ops.py` - Portfolio analytics and metrics
- `test_get_data.py` - Alpaca data retrieval
- `test_yfinance_ops.py` - Yahoo Finance operations
- `test_viz_ops.py` - Visualization functions
- `test_email_ops.py` - Email notification system

## Error Handling

The library includes robust error handling:

- **Rate Limiting**: Exponential backoff retry logic for Yahoo Finance API
- **Empty Data**: Graceful handling of empty DataFrames/Series
- **API Failures**: Defensive programming for network issues
- **Data Type Flexibility**: Functions handle both Series and DataFrame inputs
- **Missing Data**: Returns appropriate defaults (None, empty DataFrame)

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

- **Current Version**: Added visualization utilities, comprehensive portfolio analytics, and robust error handling
- **Yahoo Finance**: Market screener integration with rate limiting
- **Email System**: Gmail SMTP notifications with timestamps
- **Testing**: Comprehensive test suite with mocking

