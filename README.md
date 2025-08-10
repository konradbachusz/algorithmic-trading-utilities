# Algorithmic Trading Utilities

A comprehensive Python library for algorithmic trading with the Alpaca API. This repository provides a collection of utilities for placing trades, managing positions, and analyzing portfolio performance.

## Features

- **Position Management**: Automated stop loss placement, trailing stops, and position liquidation
- **Order Management**: Complete order lifecycle management including cancellation and monitoring
- **Portfolio Analytics**: Calculate performance metrics including Sharpe ratio, Sortino ratio, alpha, beta, and drawdown
- **Risk Management**: Configurable loss thresholds and position sizing
- **Email Notifications**: Automated alerts for trade execution and system events
- **Yahoo Finance Integration**: Access to 300+ market screeners for stock discovery
- **Quantitative Tools**: Correlation analysis and data processing utilities

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
from algorithmic_trading_utilities.brokers.alpaca.portfolio_ops import calculate_performance_metrics
from algorithmic_trading_utilities.data.yahoo_finance import get_stock_gainers_table
from algorithmic_trading_utilities.brokers.alpaca.positions import close_positions_below_threshold

# Use the utilities in your trading strategy
metrics = calculate_performance_metrics()
gainers = get_stock_gainers_table()
```

### Portfolio Performance Analysis

```python
from algorithmic_trading_utilities.brokers.alpaca.portfolio_ops import calculate_performance_metrics, get_portfolio_and_benchmark_returns

# Get comprehensive performance metrics
metrics = calculate_performance_metrics()
print(f"Sharpe Ratio: {metrics['annual_sharpe_ratio']:.2f}")
print(f"Total Return: {metrics['total_return']:.2f}%")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}")

# Compare portfolio vs S&P 500
comparison_df = get_portfolio_and_benchmark_returns()
print(comparison_df.tail())
```

### Yahoo Finance Market Screening

```python
from algorithmic_trading_utilities.data.yahoo_finance import get_stock_gainers_table

# Get today's top large-cap gainers
gainers_df = get_stock_gainers_table()
print(gainers_df.head())

# Available screeners include:
# - day_gainers, day_losers
# - most_actives, small_cap_gainers
# - undervalued_large_caps, fair_value_screener
# - And 300+ more market screeners
```

### Risk Management

```python
from algorithmic_trading_utilities.brokers.alpaca.stop_loss_ops import place_trailing_stop_losses_funct
from algorithmic_trading_utilities.brokers.alpaca.positions import close_positions_below_threshold

# Place trailing stop losses for all positions
stop_losses_placed = place_trailing_stop_losses_funct(threshold=0.1)  # 10%

# Close positions with >5% loss
positions_closed = close_positions_below_threshold(threshold=0.05)
```

## Library Structure

The library is organized into distinct modules for clean separation of concerns:

### Broker Integrations (`algorithmic_trading_utilities.brokers`)

#### Alpaca (`algorithmic_trading_utilities.brokers.alpaca`)
- **`client.py`** - API client configuration and setup
- **`orders.py`** - Order placement, cancellation, and management
- **`positions.py`** - Position tracking and management
- **`portfolio_ops.py`** - Portfolio analytics and performance metrics
- **`stop_loss_ops.py`** - Stop loss and trailing stop management
- **`data.py`** - Historical and real-time market data

#### Future Broker Support
- **`coinbase`** - Cryptocurrency trading via Coinbase (planned)
- **`kraken`** - Multi-asset trading via Kraken (planned)

### Data Providers (`algorithmic_trading_utilities.data`)
- **`yahoo_finance.py`** - 300+ market screeners and data feeds

### Common Utilities (`algorithmic_trading_utilities.common`)
- **`quantitative_tools.py`** - Statistical analysis and correlation tools
- **`email_ops.py`** - Email notification system
- **`visualization.py`** - Plotting and charting utilities

## Core Modules

### Alpaca Integration (`algorithmic_trading_utilities.brokers.alpaca`)

#### Position Management (`positions.py`)
- Track open positions and P&L
- Automated position closure based on loss thresholds
- Integration with trailing stop loss orders

#### Order Management (`orders.py`)
- Place market, limit, and trailing stop orders
- Cancel orders with retry logic and rate limiting
- Monitor order status and execution

#### Portfolio Analytics (`portfolio_ops.py`)
- Calculate Sharpe ratio, Sortino ratio, alpha, beta
- Track drawdown and cumulative returns
- Benchmark comparison against S&P 500

#### Data Operations (`data.py`)
- Historical price data from Alpaca
- Real-time market data feeds
- Asset filtering and validation

### Yahoo Finance Integration (`algorithmic_trading_utilities.data.yahoo_finance`)
- Access to 300+ market screeners
- Real-time market data
- Sector and geographic filtering

### Common Utilities (`algorithmic_trading_utilities.common`)
- Broker-agnostic quantitative analysis tools
- Email notification system
- Visualization and plotting utilities

## Configuration

Key parameters in `algorithmic_trading_utilities.brokers.alpaca.client.py`:

```python
# Risk management
loss_threshold = 0.05  # 5% stop loss
trailing_stop_loss_threshold = 0.1  # 10% trailing stop

# API configuration (set via environment variables)
PAPER_KEY = "your_alpaca_paper_api_key"
PAPER_SECRET = "your_alpaca_paper_secret_key"
```

## Testing

Run the test suite:
```bash
pytest tests/ -v -s
```

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

- **Momentum**: `day_gainers`, `small_cap_gainers`, `most_actives`
- **Value**: `undervalued_large_caps`, `fair_value_screener`
- **Sector**: `ms_technology`, `ms_healthcare`, `ms_energy`
- **ETFs**: `top_etfs`, `top_etfs_us`
- **Bonds**: `high_yield_bond`
- **Geographic**: Regional screeners for US, EU, Asia markets

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

