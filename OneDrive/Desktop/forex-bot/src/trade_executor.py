"""
Trade execution and management system.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .oanda_client import OandaClient
from .risk_manager import RiskManager
from .instrument_manager import InstrumentManager, get_instrument_manager

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Executes and manages trades."""

    def __init__(
        self,
        oanda_client: OandaClient,
        risk_manager: RiskManager,
        instrument_manager: Optional[InstrumentManager] = None
    ):
        """
        Initialize trade executor.

        Args:
            oanda_client: OANDA API client
            risk_manager: Risk manager instance
            instrument_manager: Instrument manager instance
        """
        self.oanda = oanda_client
        self.risk_manager = risk_manager
        self.instrument_manager = instrument_manager or get_instrument_manager()

        logger.info("Trade executor initialized")

    def execute_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trading signal.

        Args:
            signal: Trading signal from TradingView or strategy

        Returns:
            Execution result
        """
        try:
            action = signal.get('action', '').lower()
            instrument = signal.get('instrument')

            logger.info(f"Executing signal: {action} {instrument}")

            if action == 'buy':
                return self._execute_buy(signal)
            elif action == 'sell':
                return self._execute_sell(signal)
            elif action == 'close':
                return self._execute_close(signal)
            else:
                logger.error(f"Unknown action: {action}")
                return {'status': 'error', 'message': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return {'status': 'error', 'message': str(e)}

    def _execute_buy(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a buy signal."""
        instrument = signal['instrument']

        # Normalize instrument symbol
        instrument = self.instrument_manager.normalize_symbol(instrument)

        # Get current price
        price_data = self.oanda.get_current_price(instrument)
        entry_price = price_data['ask']
        spread = price_data['spread']

        # Get stop loss and take profit
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')

        # Calculate SL/TP from pips if not provided
        if stop_loss is None:
            sl_pips = signal.get('sl_pips', 20)
            sl_price = self.instrument_manager.calculate_price_from_pips(instrument, sl_pips)
            stop_loss = entry_price - sl_price

        if take_profit is None:
            tp_pips = signal.get('tp_pips', 40)
            tp_price = self.instrument_manager.calculate_price_from_pips(instrument, tp_pips)
            take_profit = entry_price + tp_price

        # Validate the trade
        is_valid, reason = self.risk_manager.validate_trade(
            instrument=instrument,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            spread=spread
        )

        if not is_valid:
            logger.warning(f"Trade validation failed: {reason}")
            return {'status': 'rejected', 'message': reason}

        # Get account balance
        account_balance = self.oanda.get_account_balance()

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss=stop_loss,
            instrument=instrument,
            pip_value=self.instrument_manager.get_pip_value(instrument)
        )

        # Check if we can open the position
        current_positions = self.oanda.get_position_count()
        risk_amount = abs(entry_price - stop_loss) * position_size

        can_open, reason = self.risk_manager.can_open_position(
            current_positions=current_positions,
            account_balance=account_balance,
            proposed_risk=risk_amount
        )

        if not can_open:
            logger.warning(f"Cannot open position: {reason}")
            return {'status': 'rejected', 'message': reason}

        # Place the order
        logger.info(
            f"Placing BUY order: {instrument} {position_size} units @ {entry_price:.5f} "
            f"SL: {stop_loss:.5f} TP: {take_profit:.5f}"
        )

        try:
            response = self.oanda.place_market_order(
                instrument=instrument,
                units=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            # Extract trade ID if available
            trade_id = None
            if 'orderFillTransaction' in response:
                trade_id = response['orderFillTransaction'].get('id')
            elif 'orderCreateTransaction' in response:
                trade_id = response['orderCreateTransaction'].get('id')

            return {
                'status': 'success',
                'action': 'buy',
                'instrument': instrument,
                'units': position_size,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trade_id': trade_id,
                'response': response
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OANDA order failed: {error_msg}")

            # Parse OANDA error message for common issues
            if 'MARKET_HALTED' in error_msg or 'market is not tradeable' in error_msg:
                error_msg = "Market is currently closed or halted"
            elif 'Insufficient authorization' in error_msg:
                error_msg = "Insufficient authorization to trade"
            elif 'closeout' in error_msg.lower():
                error_msg = "Order would trigger margin closeout"

            return {
                'status': 'error',
                'message': error_msg,
                'action': 'buy',
                'instrument': instrument
            }

    def _execute_sell(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a sell signal."""
        instrument = signal['instrument']

        # Normalize instrument symbol
        instrument = self.instrument_manager.normalize_symbol(instrument)

        # Get current price
        price_data = self.oanda.get_current_price(instrument)
        entry_price = price_data['bid']
        spread = price_data['spread']

        # Get stop loss and take profit
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')

        # Calculate SL/TP from pips if not provided
        if stop_loss is None:
            sl_pips = signal.get('sl_pips', 20)
            sl_price = self.instrument_manager.calculate_price_from_pips(instrument, sl_pips)
            stop_loss = entry_price + sl_price

        if take_profit is None:
            tp_pips = signal.get('tp_pips', 40)
            tp_price = self.instrument_manager.calculate_price_from_pips(instrument, tp_pips)
            take_profit = entry_price - tp_price

        # Validate the trade
        is_valid, reason = self.risk_manager.validate_trade(
            instrument=instrument,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            spread=spread
        )

        if not is_valid:
            logger.warning(f"Trade validation failed: {reason}")
            return {'status': 'rejected', 'message': reason}

        # Get account balance
        account_balance = self.oanda.get_account_balance()

        # Calculate position size (negative for sell)
        position_size = self.risk_manager.calculate_position_size(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss=stop_loss,
            instrument=instrument,
            pip_value=self.instrument_manager.get_pip_value(instrument)
        )

        # Check if we can open the position
        current_positions = self.oanda.get_position_count()
        risk_amount = abs(entry_price - stop_loss) * position_size

        can_open, reason = self.risk_manager.can_open_position(
            current_positions=current_positions,
            account_balance=account_balance,
            proposed_risk=risk_amount
        )

        if not can_open:
            logger.warning(f"Cannot open position: {reason}")
            return {'status': 'rejected', 'message': reason}

        # Place the order (negative units for sell)
        logger.info(
            f"Placing SELL order: {instrument} {position_size} units @ {entry_price:.5f} "
            f"SL: {stop_loss:.5f} TP: {take_profit:.5f}"
        )

        try:
            response = self.oanda.place_market_order(
                instrument=instrument,
                units=-position_size,  # Negative for sell
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            # Extract trade ID if available
            trade_id = None
            if 'orderFillTransaction' in response:
                trade_id = response['orderFillTransaction'].get('id')
            elif 'orderCreateTransaction' in response:
                trade_id = response['orderCreateTransaction'].get('id')

            return {
                'status': 'success',
                'action': 'sell',
                'instrument': instrument,
                'units': -position_size,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'trade_id': trade_id,
                'response': response
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"OANDA order failed: {error_msg}")

            # Parse OANDA error message for common issues
            if 'MARKET_HALTED' in error_msg or 'market is not tradeable' in error_msg:
                error_msg = "Market is currently closed or halted"
            elif 'Insufficient authorization' in error_msg:
                error_msg = "Insufficient authorization to trade"
            elif 'closeout' in error_msg.lower():
                error_msg = "Order would trigger margin closeout"

            return {
                'status': 'error',
                'message': error_msg,
                'action': 'sell',
                'instrument': instrument
            }

    def _execute_close(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a close signal."""
        instrument = signal['instrument']

        # Normalize instrument symbol
        instrument = self.instrument_manager.normalize_symbol(instrument)

        logger.info(f"Closing position: {instrument}")

        try:
            response = self.oanda.close_position(instrument)
            return {
                'status': 'success',
                'action': 'close',
                'instrument': instrument,
                'response': response
            }
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return {
                'status': 'error',
                'action': 'close',
                'instrument': instrument,
                'message': str(e)
            }

    def get_open_positions(self) -> list:
        """Get all open positions."""
        return self.oanda.get_current_positions()

    def get_open_trades(self) -> list:
        """Get all open trades."""
        return self.oanda.get_open_trades()

    def modify_trade_sl_tp(
        self,
        trade_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Modify stop loss or take profit of an existing trade.

        Args:
            trade_id: Trade ID
            stop_loss: New stop loss price
            take_profit: New take profit price

        Returns:
            Modification result
        """
        try:
            response = self.oanda.modify_trade(
                trade_id=trade_id,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            logger.info(f"Trade {trade_id} modified")
            return {'status': 'success', 'response': response}
        except Exception as e:
            logger.error(f"Error modifying trade: {e}")
            return {'status': 'error', 'message': str(e)}
