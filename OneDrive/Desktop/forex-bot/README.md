# Forex Trading Bot

A comprehensive, customizable forex and futures trading bot that integrates with OANDA and TradingView. Built with Python, this bot provides automated trading capabilities with robust risk management and position sizing.

## Features

- **OANDA Integration**: Full API integration with OANDA for forex and CFD trading
- **TradingView Webhooks**: Receive and execute trading signals from TradingView alerts
- **Futures Support**: Trade futures contracts alongside forex pairs
- **Risk Management**: Comprehensive risk controls including:
  - Configurable risk per trade
  - Daily and weekly loss limits
  - Maximum position limits
  - Automatic trading suspension on limit breach
- **Position Sizing**: Intelligent position sizing based on:
  - Account balance
  - Risk percentage
  - Stop loss distance
  - Instrument-specific parameters
- **Multi-Instrument Support**: Trade multiple forex pairs and futures contracts
- **Customizable Preferences**: Extensive configuration system for tailoring to your trading style
- **Logging**: Comprehensive logging with separate trade logs and error tracking
- **Real-time Monitoring**: Account info, position tracking, and risk status

## Project Structure

```
forex-bot/
├── config/
│   ├── config.example.yaml    # Example configuration file
│   └── .env.example           # Example environment variables
├── src/
│   ├── __init__.py
│   ├── config_loader.py       # Configuration management
│   ├── oanda_client.py        # OANDA API client
│   ├── tradingview_webhook.py # TradingView webhook receiver
│   ├── instrument_manager.py  # Instrument/symbol management
│   ├── risk_manager.py        # Risk management and position sizing
│   ├── trade_executor.py      # Trade execution logic
│   └── logger_config.py       # Logging configuration
├── data/                      # Database and data files
├── logs/                      # Log files
├── tests/                     # Unit tests
├── main.py                    # Main application entry point
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OANDA trading account (practice or live)
- TradingView account (for webhook signals)

### Setup Steps

1. **Clone or navigate to the repository**

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**

   a. Copy the example configuration files:
   ```bash
   # On Windows
   copy config\config.example.yaml config\config.yaml
   copy config\.env.example .env

   # On macOS/Linux
   cp config/config.example.yaml config/config.yaml
   cp config/.env.example .env
   ```

   b. Edit `.env` and add your OANDA credentials:
   ```
   OANDA_ACCOUNT_ID=your_account_id_here
   OANDA_API_KEY=your_api_key_here
   OANDA_ENVIRONMENT=practice
   TRADINGVIEW_WEBHOOK_SECRET=your_secret_key_here
   ```

   c. Edit `config/config.yaml` to customize your trading preferences

## Configuration

### OANDA Setup

1. Sign up for OANDA account at [oanda.com](https://www.oanda.com)
2. Get your API credentials:
   - Practice: [fxtrade-practice.oanda.com/account](https://fxtrade-practice.oanda.com/account)
   - Live: [fxtrade.oanda.com/account](https://fxtrade.oanda.com/account)
3. Generate an API token
4. Add credentials to `.env` file

### Trading Preferences

The `config.yaml` file allows you to customize:

- **Risk Management**:
  - Risk per trade (e.g., 2% of account)
  - Maximum concurrent positions
  - Daily/weekly loss limits
  - Position sizing method

- **Instruments**:
  - Enable/disable specific forex pairs
  - Enable/disable futures contracts
  - Set maximum spreads
  - Custom risk per instrument

- **Trading Hours** (optional):
  - Limit trading to specific hours
  - Set timezone preferences

- **Stop Loss & Take Profit**:
  - Default SL/TP in pips
  - Trailing stop configuration

### TradingView Integration

To receive signals from TradingView:

1. Set up your webhook in `config.yaml` or `.env`
2. Create alerts in TradingView
3. Use this JSON format for TradingView alerts:

```json
{
    "action": "buy",
    "instrument": "EUR_USD",
    "price": {{close}},
    "sl": 1.0850,
    "tp": 1.0950,
    "strategy": "My Strategy Name",
    "timestamp": {{timenow}}
}
```

**Webhook URL**: `http://your-server-ip:5000/webhook`

**Supported Actions**:
- `buy` - Open long position
- `sell` - Open short position
- `close` - Close existing position

## Usage

### Running the Bot

**Basic usage**:
```bash
python main.py
```

**With custom config**:
```bash
python main.py --config /path/to/config.yaml
```

**Check account info**:
```bash
python main.py --account-info
```

**View current positions**:
```bash
python main.py --positions
```

**Check risk status**:
```bash
python main.py --risk-status
```

### Command Line Options

- `--config PATH` - Specify custom configuration file
- `--account-info` - Display account information and exit
- `--positions` - Display current positions and exit
- `--risk-status` - Display risk management status and exit

## Supported Instruments

### Forex Pairs
- EUR_USD, GBP_USD, USD_JPY, USD_CHF
- AUD_USD, USD_CAD, NZD_USD
- EUR_GBP, EUR_JPY, GBP_JPY
- And more...

### Futures Contracts
- ES - E-mini S&P 500 Futures
- NQ - E-mini NASDAQ-100 Futures
- YM - E-mini Dow Futures
- RTY - E-mini Russell 2000 Futures
- CL - Crude Oil Futures
- GC - Gold Futures
- SI - Silver Futures
- And more...

## Risk Management Features

The bot includes comprehensive risk management:

1. **Position Sizing**: Automatically calculates position size based on:
   - Account balance
   - Risk percentage
   - Stop loss distance

2. **Loss Limits**:
   - Daily loss limit (auto-reset at midnight)
   - Weekly loss limit (auto-reset on Monday)
   - Automatic trading suspension when limits hit

3. **Position Limits**:
   - Maximum concurrent positions
   - Maximum total risk across all positions

4. **Trade Validation**:
   - Spread checks
   - Risk/reward ratio validation
   - Instrument enablement checks

## Logging

The bot creates multiple log files in the `logs/` directory:

- `forex_bot.log` - General application log
- `forex_bot_errors.log` - Error-only log
- `trades.log` - Trade execution log

Logs are automatically rotated when they reach 10MB.

## Safety Features

- **Practice Mode Default**: Bot defaults to OANDA practice environment
- **Configurable Limits**: All risk limits are configurable
- **Auto-Disable**: Trading automatically stops if limits are breached
- **Validation**: All trades are validated before execution
- **Comprehensive Logging**: All actions are logged for review

## Example: Customizing Your Trading Preferences

Edit `config/config.yaml`:

```yaml
# Trade more conservatively
trading:
  risk_per_trade: 0.01  # 1% per trade instead of 2%
  max_positions: 3      # Only 3 positions at once

# Enable only your favorite pairs
instruments:
  EUR_USD:
    enabled: true
    max_spread: 2

  GBP_USD:
    enabled: true
    max_spread: 3
    custom_risk: 0.015  # Use 1.5% risk for GBP_USD only

  # Disable others
  USD_JPY:
    enabled: false
```

## Troubleshooting

**Bot won't start**:
- Check that OANDA credentials are set in `.env`
- Verify `config.yaml` exists and is valid YAML

**Trades not executing**:
- Check risk limits haven't been hit
- Verify instrument is enabled in config
- Check spread isn't too high
- Review logs for error messages

**Webhook not receiving signals**:
- Ensure webhook server is running
- Check firewall allows traffic on port 5000
- Verify TradingView alert JSON format
- Check webhook URL is correct

## Development

### Running Tests
```bash
pytest tests/
```

### Adding Custom Strategies

You can extend the bot by adding custom strategy modules in the `src/` directory.

## Disclaimer

**IMPORTANT**: This trading bot is provided for educational purposes. Trading forex and futures involves substantial risk of loss. Always test thoroughly with a practice account before using real money. The authors are not responsible for any financial losses incurred while using this software.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Happy Trading!** Remember to always practice proper risk management and never risk more than you can afford to lose.
