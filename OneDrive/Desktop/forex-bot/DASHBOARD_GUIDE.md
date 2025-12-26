# Personal Trading Dashboard Guide

Your forex trading bot now includes a beautiful, real-time web dashboard for monitoring and controlling your trades.

## What You Can Do With the Dashboard

### Real-time Monitoring
- **Account Overview**: See your balance, NAV, unrealized P/L, and margin at a glance
- **Risk Management**: Track daily/weekly P/L against your limits with visual progress bars
- **Open Positions**: View all active trades with live P/L updates
- **Recent Signals**: See incoming TradingView signals as they arrive
- **Trade History**: Review your recent trading activity

### Active Trading Controls
- **Toggle Trading On/Off**: Instantly enable or disable automated trading
- **Manual Trade Execution**: Place trades directly from the dashboard
- **Close Positions**: Close any open position with one click
- **Live Updates**: Dashboard refreshes automatically every 3 seconds

## Starting the Dashboard

### Quick Start

1. **Activate your virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

2. **Run the dashboard:**
   ```bash
   python dashboard.py
   ```

3. **Open in your browser:**
   ```
   http://127.0.0.1:8080
   ```

### Custom Options

```bash
# Use custom port
python dashboard.py --port 9000

# Make accessible from other devices (use with caution)
python dashboard.py --host 0.0.0.0 --port 8080

# Use custom config file
python dashboard.py --config /path/to/config.yaml
```

## Dashboard Features Explained

### 1. Account Overview Section
Shows your key account metrics:
- **Balance**: Your current account balance
- **NAV**: Net Asset Value (balance + unrealized P/L)
- **Unrealized P/L**: Profit/loss from open positions (green = profit, red = loss)
- **Margin Used**: How much margin is currently locked in trades
- **Margin Available**: How much margin you have left for new trades

### 2. Risk Management Section
Visual representation of your risk limits:

**Daily P/L Progress Bar:**
- Shows current daily profit/loss
- Bar fills as you approach your daily loss limit
- Turns red when approaching limit (>75%)

**Weekly P/L Progress Bar:**
- Shows current weekly profit/loss
- Tracks against weekly loss limit
- Auto-resets every Monday

**Positions Counter:**
- Shows current positions vs. max allowed
- Displays your risk per trade percentage

### 3. Open Positions Table
Real-time view of all active trades:
- Instrument name
- Side (LONG/SHORT)
- Position size (units)
- Average entry price
- Current P/L (updates every 3 seconds)
- **Close button** - Click to instantly close any position

### 4. Recent Signals
Shows the last 10 signals received from TradingView:
- Action (BUY/SELL/CLOSE)
- Instrument
- Stop loss and take profit levels
- Timestamp

### 5. Manual Trade Panel
Execute trades directly from the dashboard:

**To Place a Trade:**
1. Select action: Buy, Sell, or Close
2. Enter instrument (e.g., EUR_USD)
3. Set stop loss in pips (e.g., 20)
4. Set take profit in pips (e.g., 40)
5. Click "Execute Trade"

**To Close a Position:**
1. Select "Close" from action dropdown
2. Enter instrument to close
3. Click "Execute Trade"

### 6. Trade History
Recent trade activity showing:
- Execution time
- Action taken
- Instrument
- Position size
- Entry price, SL, and TP
- Status

## Trading Controls

### Enable/Disable Trading Toggle
Located in the top-right corner:
- **Green (ON)**: Bot will execute signals and trades
- **Red (OFF)**: Bot will reject all trades
- Useful for temporarily pausing trading without stopping the bot

### Environment Indicator
Shows whether you're in PRACTICE or LIVE mode:
- **Orange badge**: Practice account (safe for testing)
- **Red badge**: Live account (real money)

## Dashboard Tips

### Best Practices
1. **Keep it open**: Leave dashboard open while bot is running to monitor activity
2. **Check before trading**: Always verify your account info before enabling trading
3. **Watch risk meters**: If progress bars are filling up, consider reducing position sizes
4. **Use manual trades carefully**: Manual trades bypass some risk checks, use responsibly

### Understanding the Colors
- **Green**: Positive P/L, buy actions, enabled status
- **Red**: Negative P/L, sell actions, warnings
- **Blue**: Information, close actions
- **Orange/Yellow**: Practice mode, warnings at 75% of limits

### Auto-Refresh
The dashboard automatically updates every 3 seconds:
- All account data refreshes
- Positions update with current P/L
- New signals appear automatically
- Risk meters update in real-time

You can see the last update time in the top-right corner.

## Accessing From Other Devices

### On Your Local Network
To access from phone/tablet on same WiFi:

1. Find your computer's IP address:
   ```bash
   # On Windows
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)

   # On macOS/Linux
   ifconfig
   ```

2. Start dashboard with:
   ```bash
   python dashboard.py --host 0.0.0.0 --port 8080
   ```

3. Access from other device:
   ```
   http://192.168.1.100:8080
   ```

**Security Note**: Only do this on trusted networks!

### Remote Access (VPS/Cloud)
If running on a VPS:

1. Ensure port 8080 is open in firewall
2. Use your server's public IP or domain
3. **Strongly recommended**: Set up HTTPS and authentication
4. Consider using a reverse proxy (nginx) for security

## Troubleshooting

### Dashboard Won't Load
- Check that `python dashboard.py` is running
- Verify the URL: `http://127.0.0.1:8080`
- Try a different port: `python dashboard.py --port 9000`
- Check firewall isn't blocking the port

### Data Not Updating
- Check console for errors
- Verify OANDA credentials in `.env`
- Ensure internet connection is stable
- Refresh the browser page

### Can't Execute Trades
- Verify trading toggle is ON (green)
- Check risk limits haven't been hit
- Ensure instrument is enabled in config
- Review browser console for error messages

### Real-time Updates Stopped
- Browser may have gone to sleep
- Refresh the page to restart updates
- Check if bot is still running

## Keyboard Shortcuts
- **Ctrl+R** / **Cmd+R**: Refresh dashboard
- **F5**: Hard refresh (clears cache)
- **F12**: Open developer console (for debugging)

## Mobile Experience
The dashboard is responsive and works on mobile devices:
- Optimized for phones and tablets
- Touch-friendly buttons
- Scrollable tables
- All features accessible

## Security Considerations

### Important Security Tips
1. **Don't expose publicly**: Only access on trusted networks
2. **Use strong credentials**: Keep OANDA API keys secure
3. **Practice first**: Test with practice account before live trading
4. **Monitor regularly**: Don't leave automated trading unattended for long
5. **Set limits**: Always configure risk limits in config file

### What Others Can Do If They Access Your Dashboard
If someone accesses your dashboard, they can:
- See your account balance and positions
- Execute trades on your account
- Enable/disable trading
- Close your positions

**Therefore**: Only allow access on secure, trusted networks!

## Advanced Features

### Webhook Integration
The dashboard works alongside TradingView webhooks:
- Webhook runs on port 5000 (configurable)
- Dashboard runs on port 8080 (configurable)
- Both can run simultaneously
- Signals from TradingView appear in "Recent Signals"

### Running Both Dashboard and Webhook
```bash
# Start the dashboard (includes webhook automatically)
python dashboard.py
```

The dashboard automatically starts the TradingView webhook in the background if it's enabled in your config!

## Dashboard vs Command Line

You have two ways to run your bot:

### Dashboard (dashboard.py)
- Web interface for monitoring
- Real-time visual updates
- Manual trading controls
- Better for active monitoring
- Includes webhook server

### Command Line (main.py)
- Terminal-based
- Simpler, lightweight
- Good for running in background
- Can run as service
- Includes webhook server

Choose based on your needs - both are fully functional!

---

**Enjoy your personal trading dashboard!** Monitor your trades in style with real-time updates and full control at your fingertips.
