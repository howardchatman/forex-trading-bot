"""
Main application for the Forex Trading Bot.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src import (
    get_config,
    OandaClient,
    TradingViewWebhook,
    RiskManager,
    TradeExecutor,
    setup_logger,
    get_instrument_manager
)


class ForexTradingBot:
    """Main trading bot application."""

    def __init__(self, config_path: str = None):
        """
        Initialize the trading bot.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = get_config(config_path)

        # Setup logging
        log_config = self.config.get('logging', {})
        self.logger = setup_logger(
            level=log_config.get('level', 'INFO'),
            log_to_file=log_config.get('log_to_file', True),
            log_dir=log_config.get('log_dir', 'logs')
        )

        self.logger.info("=" * 60)
        self.logger.info("Forex Trading Bot Starting...")
        self.logger.info("=" * 60)

        # Initialize components
        self._init_components()

        self.logger.info("Trading bot initialized successfully")

    def _init_components(self):
        """Initialize all bot components."""
        # Get OANDA configuration
        oanda_config = self.config.get_oanda_config()

        if not oanda_config.get('account_id') or not oanda_config.get('api_key'):
            self.logger.error("OANDA credentials not configured!")
            self.logger.error("Please set OANDA_ACCOUNT_ID and OANDA_API_KEY in .env file")
            sys.exit(1)

        # Initialize OANDA client
        self.oanda_client = OandaClient(
            account_id=oanda_config['account_id'],
            api_key=oanda_config['api_key'],
            environment=oanda_config.get('environment', 'practice')
        )

        # Initialize instrument manager
        self.instrument_manager = get_instrument_manager()

        # Initialize risk manager
        self.risk_manager = RiskManager(self.config.config)

        # Initialize trade executor
        self.trade_executor = TradeExecutor(
            oanda_client=self.oanda_client,
            risk_manager=self.risk_manager,
            instrument_manager=self.instrument_manager
        )

        # Initialize TradingView webhook if enabled
        tv_config = self.config.get('tradingview', {})
        if tv_config.get('enabled', True):
            self.webhook = TradingViewWebhook(
                port=tv_config.get('webhook_port', 5000),
                webhook_secret=tv_config.get('webhook_secret'),
                allowed_ips=tv_config.get('allowed_ips', [])
            )
            # Register signal handler
            self.webhook.register_signal_handler(self._handle_trading_signal)
        else:
            self.webhook = None
            self.logger.info("TradingView webhook disabled")

    def _handle_trading_signal(self, signal: dict) -> dict:
        """
        Handle incoming trading signals.

        Args:
            signal: Trading signal data

        Returns:
            Execution result
        """
        self.logger.info(f"Processing signal: {signal['action']} {signal['instrument']}")

        try:
            # Execute the signal
            result = self.trade_executor.execute_signal(signal)

            # Log the result
            if result['status'] == 'success':
                self.logger.info(f"Signal executed successfully: {result}")
            else:
                self.logger.warning(f"Signal execution failed: {result}")

            return result

        except Exception as e:
            self.logger.error(f"Error handling signal: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def get_account_info(self):
        """Display account information."""
        try:
            summary = self.oanda_client.get_account_summary()
            balance = float(summary.get('balance', 0))
            nav = float(summary.get('NAV', 0))
            unrealized_pl = float(summary.get('unrealizedPL', 0))
            margin_used = float(summary.get('marginUsed', 0))
            margin_available = float(summary.get('marginAvailable', 0))

            self.logger.info("\n" + "=" * 60)
            self.logger.info("ACCOUNT INFORMATION")
            self.logger.info("=" * 60)
            self.logger.info(f"Balance:           ${balance:,.2f}")
            self.logger.info(f"NAV:               ${nav:,.2f}")
            self.logger.info(f"Unrealized P/L:    ${unrealized_pl:,.2f}")
            self.logger.info(f"Margin Used:       ${margin_used:,.2f}")
            self.logger.info(f"Margin Available:  ${margin_available:,.2f}")
            self.logger.info("=" * 60 + "\n")

            return summary
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return None

    def get_positions(self):
        """Display current positions."""
        try:
            positions = self.trade_executor.get_open_positions()

            self.logger.info("\n" + "=" * 60)
            self.logger.info("OPEN POSITIONS")
            self.logger.info("=" * 60)

            if not positions:
                self.logger.info("No open positions")
            else:
                for pos in positions:
                    instrument = pos.get('instrument')
                    long_units = float(pos.get('long', {}).get('units', 0))
                    short_units = float(pos.get('short', {}).get('units', 0))
                    long_pl = float(pos.get('long', {}).get('unrealizedPL', 0))
                    short_pl = float(pos.get('short', {}).get('unrealizedPL', 0))

                    if long_units != 0:
                        self.logger.info(f"{instrument}: LONG {long_units} units | P/L: ${long_pl:.2f}")
                    if short_units != 0:
                        self.logger.info(f"{instrument}: SHORT {short_units} units | P/L: ${short_pl:.2f}")

            self.logger.info("=" * 60 + "\n")
            return positions
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []

    def get_risk_status(self):
        """Display risk management status."""
        try:
            balance = self.oanda_client.get_account_balance()
            status = self.risk_manager.get_risk_status(balance)

            self.logger.info("\n" + "=" * 60)
            self.logger.info("RISK MANAGEMENT STATUS")
            self.logger.info("=" * 60)
            self.logger.info(f"Trading Enabled:        {status['trading_enabled']}")
            self.logger.info(f"Daily P/L:              ${status['daily_pnl']:.2f}")
            self.logger.info(f"Weekly P/L:             ${status['weekly_pnl']:.2f}")
            self.logger.info(f"Daily Loss %:           {status['daily_loss_percent']*100:.2f}%")
            self.logger.info(f"Weekly Loss %:          {status['weekly_loss_percent']*100:.2f}%")
            self.logger.info(f"Daily Limit Remaining:  {status['daily_limit_remaining']*100:.2f}%")
            self.logger.info(f"Weekly Limit Remaining: {status['weekly_limit_remaining']*100:.2f}%")
            self.logger.info("=" * 60 + "\n")

            return status
        except Exception as e:
            self.logger.error(f"Error getting risk status: {e}")
            return None

    def run(self):
        """Run the trading bot."""
        try:
            # Display initial information
            self.get_account_info()
            self.get_positions()
            self.get_risk_status()

            # Start webhook server if enabled
            if self.webhook:
                self.logger.info("Starting TradingView webhook server...")
                self.logger.info("Send trading signals to: http://your-server:5000/webhook")
                self.webhook.run()
            else:
                self.logger.info("Running in manual mode (webhook disabled)")
                self.logger.info("Press Ctrl+C to exit")
                # Keep the bot running
                import time
                while True:
                    time.sleep(60)
                    # Optionally refresh account info periodically
                    # self.get_account_info()

        except KeyboardInterrupt:
            self.logger.info("\nShutting down trading bot...")
        except Exception as e:
            self.logger.error(f"Error running bot: {e}", exc_info=True)
        finally:
            self.logger.info("Trading bot stopped")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Forex Trading Bot')
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--account-info',
        action='store_true',
        help='Show account information and exit'
    )
    parser.add_argument(
        '--positions',
        action='store_true',
        help='Show current positions and exit'
    )
    parser.add_argument(
        '--risk-status',
        action='store_true',
        help='Show risk management status and exit'
    )

    args = parser.parse_args()

    # Create bot instance
    bot = ForexTradingBot(config_path=args.config)

    # Handle command line options
    if args.account_info:
        bot.get_account_info()
        return

    if args.positions:
        bot.get_positions()
        return

    if args.risk_status:
        bot.get_risk_status()
        return

    # Run the bot
    bot.run()


if __name__ == '__main__':
    main()
