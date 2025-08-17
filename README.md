# Algorithmic Trading Utilities

A comprehensive Python library for algorithmic trading with the Alpaca API. This repository provides a collection of utilities for placing trades, managing positions, and analyzing portfolio performance.

## Features

- **Portfolio Analytics**: Calculate performance metrics including Sharpe ratio, Sortino ratio, alpha, beta, and drawdown
- **Data Management**: Historical and real-time data from Alpaca and Yahoo Finance
- **Email Notifications**: Automated alerts for trade execution and system events
- **Yahoo Finance Integration**: Access to 300+ market screeners for stock discovery
- **Visualization Tools**: Time series plotting and portfolio comparison charts

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

#### Example requirements.txt for your trading project:
```
numpy>=1.21.0
pandas>=1.3.0
alpaca-trade-api>=2.3.0
yfinance>=0.1.87
yahooquery>=2.3.0
matplotlib>=3.5.0
python-dotenv>=0.19.0
git+https://github.com/your-username/algorithmic-trading-utilities.git
```

### Environment Setup

3. **Environment setup**:
   Create a `.env` file in your project root:
   ```bash
   PAPER_KEY="your_alpaca_paper_api_key"
   PAPER_SECRET="your_alpaca_paper_secret_key"
   web_app_email="your_sender_email@gmail.com"
   web_app_email_password="your_app_password"
   recipient_email="your_recipient_email@gmail.com"
   ```

## Usage Examples

### Importing in Your Project

```python
# Import specific modules
from algorithmic_trading_utilities.common.portfolio_ops import calculate_performance_metrics
from algorithmic_trading_utilities.data.yfinance_ops import get_stock_gainers_table, get_sp500_prices
from algorithmic_trading_utilities.data.get_data import get_assets, get_historical_data
from algorithmic_trading_utilities.common.email_ops import send_email_notification

# Use the utilities in your trading strategy
metrics = calculate_performance_metrics()
gainers = get_stock_gainers_table()
```

### Portfolio Performance Analysis

```python
from algorithmic_trading_utilities.common.portfolio_ops import (
    calculate_performance_metrics, 
    get_portfolio_and_benchmark_returns,
    get_alpha,
    get_beta
)

# Get comprehensive performance metrics
metrics = calculate_performance_metrics()
print(f"Annual Sharpe Ratio: {metrics['annual_sharpe_ratio']:.2f}")
print(f"Total Return: {metrics['total_return']:.2f}%")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}")
print(f"Alpha: {metrics['alpha']:.4f}")
print(f"Beta: {metrics['beta']:.4f}")

# Compare portfolio vs S&P 500
comparison_df = get_portfolio_and_benchmark_returns()
print(comparison_df.tail())
```

### Data Retrieval and Analysis

```python
from algorithmic_trading_utilities.data.get_data import (
    get_assets, 
    get_historical_data, 
    get_last_price
)
from algorithmic_trading_utilities.data.yfinance_ops import get_sp500_prices
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.client import TradingClient

# Initialize clients
trading_client = TradingClient("your_key", "your_secret")
data_client = StockHistoricalDataClient("your_key", "your_secret")

# Get available assets
assets = get_assets(trading_client)
print(f"Found {len(assets)} tradeable assets")

# Get historical data for a specific stock
historical_data = get_historical_data("AAPL", data_client)
print(historical_data.head())

# Get S&P 500 benchmark data
sp500_data = get_sp500_prices("2024-01-01")
print(sp500_data.tail())
```

### Yahoo Finance Market Screening

```python
from algorithmic_trading_utilities.data.yfinance_ops import get_stock_gainers_table

# Get today's top large-cap gainers (market cap >= $10B)
gainers_df = get_stock_gainers_table()
print(gainers_df.head())

# Columns include:
# - exchange, symbol, shortName
# - regularMarketChangePercent
# - fiftyDayAverageChangePercent
```

### Email Notifications

```python
from algorithmic_trading_utilities.common.email_ops import send_email_notification

# Send success notification
send_email_notification(
    subject="Trade Execution",
    notification="Successfully placed buy order for AAPL",
    type="SUCCESS"
)

# Send failure notification
send_email_notification(
    subject="System Alert",
    notification="Failed to connect to market data",
    type="FAILURE"
)
```

### Visualization

```python
from algorithmic_trading_utilities.common.viz_ops import (
    plot_time_series, 
    compare_portfolio_and_benchmark
)
from algorithmic_trading_utilities.common.portfolio_ops import get_portfolio_and_benchmark_values

# Plot portfolio vs benchmark comparison
comparison_df = get_portfolio_and_benchmark_values()
compare_portfolio_and_benchmark(comparison_df, "Portfolio vs S&P 500")

# Plot any time series data
plot_time_series(comparison_df)
```

## Library Structure

The library is organized into distinct modules for clean separation of concerns:

### Data Providers (`algorithmic_trading_utilities.data`)
- **`get_data.py`** - Alpaca data retrieval (assets, historical data, last prices)
- **`yfinance_ops.py`** - Yahoo Finance integration (S&P 500 data, market screeners)

### Broker Integrations (`algorithmic_trading_utilities.brokers`)
- **`alpaca/alpaca_ops.py`** - Alpaca API portfolio history integration

### Common Utilities (`algorithmic_trading_utilities.common`)
- **`portfolio_ops.py`** - Portfolio analytics and performance metrics
- **`email_ops.py`** - Email notification system  
- **`viz_ops.py`** - Plotting and charting utilities

## Core Modules

### Portfolio Analytics (`algorithmic_trading_utilities.common.portfolio_ops`)

Key functions:
- `calculate_performance_metrics()` - Comprehensive performance analysis
- `get_alpha()`, `get_beta()` - Risk-adjusted performance metrics
- `get_sharpe_ratio()`, `get_sortino_ratio()` - Risk-return ratios
- `get_max_drawdown()` - Risk assessment
- `get_portfolio_and_benchmark_returns()` - Comparative analysis

### Data Operations (`algorithmic_trading_utilities.data`)

#### Alpaca Data (`get_data.py`)
- `get_assets()` - Retrieve tradeable assets
- `get_historical_data()` - Historical price data
- `get_last_price()` - Current market prices
- `get_asset_df()` - Convert asset data to DataFrame

#### Yahoo Finance (`yfinance_ops.py`)
- `get_sp500_prices()` - S&P 500 benchmark data
- `get_stock_gainers_table()` - Daily market gainers with retry logic

### Email Notifications (`algorithmic_trading_utilities.common.email_ops`)
- `send_email_notification()` - Send formatted email alerts with timestamps

### Visualization (`algorithmic_trading_utilities.common.viz_ops`)
- `plot_time_series()` - General time series plotting
- `compare_portfolio_and_benchmark()` - Portfolio comparison charts

## Configuration

Key parameters can be configured via environment variables:

```python
# API configuration
PAPER_KEY = "your_alpaca_paper_api_key"
PAPER_SECRET = "your_alpaca_paper_secret_key"

# Email configuration
web_app_email = "your_sender_email@gmail.com"
web_app_email_password = "your_app_password"
recipient_email = "your_recipient_email@gmail.com"
```

## Testing

Run the test suite:
```bash
pytest tests/ -v -s
```

The test suite includes:
- Portfolio operations testing (`test_portfolio_ops.py`)
- Data retrieval testing (`test_get_data.py`) 
- Email functionality testing (`test_email_ops.py`)

## Development Workflow

Format code and run tests:
```bash
# Format with black
black .

# Run tests
pytest tests/ -v -s

# Lint with flake8
flake8 .
```

## Available Yahoo Finance Screeners

The library provides access to 300+ market screeners including:

- **Momentum**: `day_gainers`, `day_losers`, `small_cap_gainers`, `most_actives`
- **Value**: `undervalued_large_caps`, `fair_value_screener`, `undervalued_growth_stocks`
- **Sector**: `ms_technology`, `ms_healthcare`, `ms_energy`, `ms_financial_services`
- **ETFs**: `top_etfs`, `top_etfs_us`, `top_etfs_hk`
- **Bonds**: `high_yield_bond`
- **Geographic**: Regional screeners for Americas, Asia, Europe
- **Market Cap**: `aggressive_small_caps`, `mega_cap_hc`

## Performance Metrics Available

The library calculates comprehensive portfolio metrics:

### Return Metrics
- Average Return
- Total Return  
- Cumulative Return

### Risk Metrics
- Standard Deviation
- Maximum Drawdown
- Downside Deviation

### Risk-Adjusted Metrics
- Sharpe Ratio (daily and annualized)
- Sortino Ratio (daily and annualized)
- Alpha (vs S&P 500)
- Beta (vs S&P 500)

## Risk Disclaimer

This software is for educational and research purposes only. Algorithmic trading involves substantial risk of loss. Always test strategies thoroughly with paper trading before deploying real capital.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite and formatting
5. Submit a pull request

## Support

For issues and questions:
- Open a GitHub issue
- Check the documentation in each module
- Review the example usage patterns

