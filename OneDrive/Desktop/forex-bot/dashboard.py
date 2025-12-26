"""
Personal Trading Dashboard for Forex Bot
"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src import (
    get_config,
    OandaClient,
    RiskManager,
    TradeExecutor,
    TradingViewWebhook,
    setup_logger,
    get_instrument_manager
)

app = Flask(__name__)
CORS(app)

# Global bot instance
bot = None


class TradingBotDashboard:
    """Trading bot with dashboard interface."""

    def __init__(self, config_path: str = None):
        """Initialize the trading bot and dashboard."""
        # Load configuration
        self.config = get_config(config_path)

        # Setup logging
        log_config = self.config.get('logging', {})
        self.logger = setup_logger(
            level=log_config.get('level', 'INFO'),
            log_to_file=log_config.get('log_to_file', True),
            log_dir=log_config.get('log_dir', 'logs')
        )

        self.logger.info("Trading Bot Dashboard Starting...")

        # Initialize components
        self._init_components()

        # Trade history
        self.trade_history = []
        self.recent_signals = []

    def _init_components(self):
        """Initialize all bot components."""
        oanda_config = self.config.get_oanda_config()

        if not oanda_config.get('account_id') or not oanda_config.get('api_key'):
            self.logger.error("OANDA credentials not configured!")
            sys.exit(1)

        # Initialize OANDA client
        self.oanda_client = OandaClient(
            account_id=oanda_config['account_id'],
            api_key=oanda_config['api_key'],
            environment=oanda_config.get('environment', 'practice')
        )

        # Initialize other components
        self.instrument_manager = get_instrument_manager()
        self.risk_manager = RiskManager(self.config.config)
        self.trade_executor = TradeExecutor(
            oanda_client=self.oanda_client,
            risk_manager=self.risk_manager,
            instrument_manager=self.instrument_manager
        )

        # Initialize webhook if enabled
        tv_config = self.config.get('tradingview', {})
        if tv_config.get('enabled', True):
            self.webhook = TradingViewWebhook(
                port=tv_config.get('webhook_port', 5000),
                webhook_secret=tv_config.get('webhook_secret'),
                allowed_ips=tv_config.get('allowed_ips', [])
            )
            self.webhook.register_signal_handler(self._handle_trading_signal)
            # Start webhook in background
            threading.Thread(target=self.webhook.run, daemon=True).start()
            self.logger.info("TradingView webhook started")

    def _handle_trading_signal(self, signal: dict) -> dict:
        """Handle incoming trading signals."""
        self.logger.info(f"Processing signal: {signal['action']} {signal['instrument']}")

        # Add to recent signals
        signal['timestamp'] = datetime.now().isoformat()
        self.recent_signals.insert(0, signal)
        if len(self.recent_signals) > 20:
            self.recent_signals.pop()

        try:
            result = self.trade_executor.execute_signal(signal)

            # Add to trade history
            if result['status'] == 'success':
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'action': result['action'],
                    'instrument': result['instrument'],
                    'units': result.get('units'),
                    'entry_price': result.get('entry_price'),
                    'stop_loss': result.get('stop_loss'),
                    'take_profit': result.get('take_profit'),
                    'status': 'open'
                }
                self.trade_history.insert(0, trade_record)

            return result
        except Exception as e:
            self.logger.error(f"Error handling signal: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def get_dashboard_data(self):
        """Get all dashboard data."""
        try:
            # Account info
            account_summary = self.oanda_client.get_account_summary()
            balance = float(account_summary.get('balance', 0))

            # Positions
            positions = self.oanda_client.get_current_positions()
            open_positions = []
            total_unrealized_pl = 0

            for pos in positions:
                long_units = float(pos.get('long', {}).get('units', 0))
                short_units = float(pos.get('short', {}).get('units', 0))
                long_pl = float(pos.get('long', {}).get('unrealizedPL', 0))
                short_pl = float(pos.get('short', {}).get('unrealizedPL', 0))

                if long_units != 0:
                    open_positions.append({
                        'instrument': pos['instrument'],
                        'side': 'LONG',
                        'units': long_units,
                        'pl': long_pl,
                        'avg_price': float(pos.get('long', {}).get('averagePrice', 0))
                    })
                    total_unrealized_pl += long_pl

                if short_units != 0:
                    open_positions.append({
                        'instrument': pos['instrument'],
                        'side': 'SHORT',
                        'units': abs(short_units),
                        'pl': short_pl,
                        'avg_price': float(pos.get('short', {}).get('averagePrice', 0))
                    })
                    total_unrealized_pl += short_pl

            # Risk status
            risk_status = self.risk_manager.get_risk_status(balance)

            # Open trades
            open_trades = self.oanda_client.get_open_trades()

            return {
                'account': {
                    'balance': balance,
                    'nav': float(account_summary.get('NAV', 0)),
                    'unrealized_pl': total_unrealized_pl,
                    'margin_used': float(account_summary.get('marginUsed', 0)),
                    'margin_available': float(account_summary.get('marginAvailable', 0)),
                    'environment': self.config.get('oanda', {}).get('environment', 'practice')
                },
                'positions': open_positions,
                'risk': {
                    'trading_enabled': risk_status['trading_enabled'],
                    'daily_pnl': risk_status['daily_pnl'],
                    'weekly_pnl': risk_status['weekly_pnl'],
                    'daily_loss_percent': risk_status['daily_loss_percent'] * 100,
                    'weekly_loss_percent': risk_status['weekly_loss_percent'] * 100,
                    'daily_limit': risk_status['daily_limit'] * 100,
                    'weekly_limit': risk_status['weekly_limit'] * 100,
                    'max_positions': self.config.get('trading', {}).get('max_positions', 5),
                    'current_positions': len(open_positions),
                    'risk_per_trade': self.config.get('trading', {}).get('risk_per_trade', 0.02) * 100
                },
                'recent_signals': self.recent_signals[:10],
                'trade_history': self.trade_history[:10],
                'open_trades_count': len(open_trades),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}", exc_info=True)
            return {'error': str(e)}


# Flask routes
@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/dashboard')
def dashboard_data():
    """Get dashboard data API."""
    if bot:
        data = bot.get_dashboard_data()
        return jsonify(data)
    return jsonify({'error': 'Bot not initialized'}), 500


@app.route('/api/close-position', methods=['POST'])
def close_position():
    """Close a position."""
    if not bot:
        return jsonify({'error': 'Bot not initialized'}), 500

    data = request.get_json()
    instrument = data.get('instrument')

    if not instrument:
        return jsonify({'error': 'Instrument required'}), 400

    try:
        result = bot.trade_executor._execute_close({'instrument': instrument})
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/enable-trading', methods=['POST'])
def enable_trading():
    """Enable trading."""
    if bot:
        bot.risk_manager.enable_trading()
        return jsonify({'status': 'success', 'trading_enabled': True})
    return jsonify({'error': 'Bot not initialized'}), 500


@app.route('/api/disable-trading', methods=['POST'])
def disable_trading():
    """Disable trading."""
    if bot:
        bot.risk_manager.disable_trading()
        return jsonify({'status': 'success', 'trading_enabled': False})
    return jsonify({'error': 'Bot not initialized'}), 500


@app.route('/api/manual-trade', methods=['POST'])
def manual_trade():
    """Execute a manual trade."""
    if not bot:
        return jsonify({'error': 'Bot not initialized'}), 500

    data = request.get_json()
    try:
        result = bot.trade_executor.execute_signal(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Forex Trading Bot Dashboard')
    parser.add_argument('--config', type=str, default=None, help='Path to configuration file')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 8080)), help='Dashboard port (default: 8080)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Dashboard host (default: 127.0.0.1)')

    args = parser.parse_args()

    # Initialize bot
    global bot
    bot = TradingBotDashboard(config_path=args.config)

    print("\n" + "=" * 60)
    print("FOREX TRADING BOT DASHBOARD")
    print("=" * 60)
    print(f"Dashboard URL: http://{args.host}:{args.port}")
    print(f"Environment: {bot.config.get('oanda', {}).get('environment', 'practice').upper()}")
    print("=" * 60 + "\n")

    # Run Flask app
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == '__main__':
    main()
