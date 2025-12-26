# Forex Trading Bot - Quick Setup Guide

This guide will walk you through setting up your forex trading bot step by step.

## Step 1: Install Python Dependencies

First, make sure you're in the project directory and have activated your virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

Then install the required packages:

```bash
pip install -r requirements.txt
```

## Step 2: Get OANDA Credentials

### For Practice Account (Recommended to start):

1. Go to [https://www.oanda.com/register/](https://www.oanda.com/register/)
2. Sign up for a free practice account
3. Once logged in, go to "Manage API Access" in your account settings
4. Generate a new API token
5. Note down your:
   - Account ID (looks like: 001-001-1234567-001)
   - API Key (long string of characters)

### For Live Account:

Same process, but use [https://fxtrade.oanda.com](https://fxtrade.oanda.com)

**WARNING**: Only use live account after thorough testing with practice account!

## Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
# On Windows
copy config\.env.example .env

# On macOS/Linux
cp config/.env.example .env
```

2. Edit the `.env` file with your credentials:
```
OANDA_ACCOUNT_ID=001-001-1234567-001
OANDA_API_KEY=your_actual_api_key_here
OANDA_ENVIRONMENT=practice
TRADINGVIEW_WEBHOOK_SECRET=choose_a_secret_password
```

## Step 4: Configure Trading Preferences

1. Copy the example config file:
```bash
# On Windows
copy config\config.example.yaml config\config.yaml

# On macOS/Linux
cp config/config.example.yaml config/config.yaml
```

2. Edit `config/config.yaml` to customize your preferences:

### Essential Settings to Review:

**Risk Management** (adjust to your comfort level):
```yaml
trading:
  risk_per_trade: 0.02  # 2% risk per trade (conservative: 0.01, aggressive: 0.03)
  max_positions: 5       # Maximum concurrent trades
  max_total_risk: 0.06   # Total risk across all trades

risk_management:
  daily_loss_limit: 0.05   # Stop trading if you lose 5% in a day
  weekly_loss_limit: 0.10  # Stop trading if you lose 10% in a week
```

**Instruments** (enable only pairs you want to trade):
```yaml
instruments:
  EUR_USD:
    enabled: true    # Set to false to disable
    max_spread: 2    # Maximum spread in pips

  GBP_USD:
    enabled: true

  # Add your preferred instruments...
```

## Step 5: Test Your Setup

Test that everything is working:

```bash
# Check account connection
python main.py --account-info
```

You should see your account information displayed. If you get an error, check:
- Your OANDA credentials in `.env`
- Your internet connection
- That you're using the correct environment (practice vs live)

## Step 6: Set Up TradingView (Optional)

If you want to use TradingView signals:

### 6.1: Configure Webhook Server

In `config/config.yaml`, ensure webhook is enabled:
```yaml
tradingview:
  enabled: true
  webhook_port: 5000
  webhook_secret: "your_secret_from_env_file"
```

### 6.2: Make Webhook Accessible

**For local testing**:
- Use ngrok or similar to expose port 5000
- `ngrok http 5000`
- Use the ngrok URL in TradingView

**For production**:
- Deploy to a server (VPS, cloud, etc.)
- Ensure port 5000 is open in firewall
- Use your server's public IP or domain

### 6.3: Create TradingView Alert

In TradingView:
1. Create an alert on your chart
2. Set the webhook URL: `http://your-server:5000/webhook`
3. Use this message format:

**For Buy Signal**:
```json
{
    "action": "buy",
    "instrument": "EUR_USD",
    "sl_pips": 20,
    "tp_pips": 40,
    "strategy": "My Strategy"
}
```

**For Sell Signal**:
```json
{
    "action": "sell",
    "instrument": "EUR_USD",
    "sl_pips": 20,
    "tp_pips": 40,
    "strategy": "My Strategy"
}
```

**For Close Signal**:
```json
{
    "action": "close",
    "instrument": "EUR_USD"
}
```

## Step 7: Run the Bot

Start the bot:

```bash
python main.py
```

You should see:
- Account information
- Current positions
- Risk status
- "Starting TradingView webhook server..." (if enabled)

The bot is now running and will:
- Listen for TradingView webhooks (if enabled)
- Execute trades based on signals
- Apply risk management rules
- Log all activity

## Common Customizations

### Conservative Trading Setup
```yaml
trading:
  risk_per_trade: 0.01  # Only risk 1% per trade
  max_positions: 2      # Only 2 trades at once

risk_management:
  daily_loss_limit: 0.03   # Stop at 3% daily loss
  weekly_loss_limit: 0.05  # Stop at 5% weekly loss
```

### Aggressive Trading Setup
```yaml
trading:
  risk_per_trade: 0.03  # Risk 3% per trade
  max_positions: 10     # Up to 10 trades

risk_management:
  daily_loss_limit: 0.10   # Allow 10% daily loss
  weekly_loss_limit: 0.20  # Allow 20% weekly loss
```

### Trade Only Specific Hours
```yaml
trading:
  trading_hours:
    enabled: true
    start: "08:00"
    end: "16:00"
    timezone: "America/New_York"
```

### Custom Risk Per Instrument
```yaml
instruments:
  EUR_USD:
    enabled: true
    max_spread: 2
    custom_risk: 0.015  # Use 1.5% risk only for EUR_USD

  GBP_USD:
    enabled: true
    max_spread: 3
    custom_risk: 0.025  # Use 2.5% risk for GBP_USD
```

## Monitoring Your Bot

### View Account Info
```bash
python main.py --account-info
```

### View Open Positions
```bash
python main.py --positions
```

### Check Risk Status
```bash
python main.py --risk-status
```

### Review Logs
Check the `logs/` directory:
- `forex_bot.log` - Everything
- `trades.log` - Just trades
- `forex_bot_errors.log` - Only errors

## Safety Checklist

Before running with real money:

- [ ] Tested thoroughly with practice account
- [ ] Understand all configuration options
- [ ] Risk per trade is comfortable (1-2% recommended)
- [ ] Daily/weekly loss limits are set
- [ ] Only enabled instruments you understand
- [ ] Tested TradingView webhooks (if using)
- [ ] Reviewed and understand all logs
- [ ] Have a plan to monitor the bot regularly
- [ ] Understand that losses can occur

## Troubleshooting

**"OANDA credentials not configured" error**:
- Check `.env` file exists in project root
- Verify OANDA_ACCOUNT_ID and OANDA_API_KEY are set
- Ensure no extra spaces in credentials

**Trades not executing**:
- Check `logs/forex_bot.log` for rejection reasons
- Verify instrument is enabled in config
- Check risk limits haven't been hit
- Verify sufficient account balance

**Webhook not working**:
- Ensure bot is running: `python main.py`
- Check firewall allows port 5000
- Verify webhook URL is correct
- Check TradingView alert JSON format
- Review `logs/forex_bot.log` for webhook messages

## Next Steps

1. **Start with small amounts**: Even in live trading, start small
2. **Monitor regularly**: Check logs and positions daily
3. **Adjust as needed**: Tune your config based on results
4. **Keep learning**: Study your trades and improve your strategy

## Getting Help

If you encounter issues:
1. Check the logs in `logs/` directory
2. Review this guide and README.md
3. Verify your configuration files
4. Test with practice account first

---

**Remember**: Trading carries risk. Never risk more than you can afford to lose. This bot is a tool - success depends on your strategy and risk management.
