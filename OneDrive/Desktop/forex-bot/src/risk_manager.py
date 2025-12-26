"""
Risk management and position sizing for the trading bot.
"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and position sizing."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize risk manager.

        Args:
            config: Risk management configuration
        """
        self.config = config

        # Risk limits
        self.risk_per_trade = config.get('trading', {}).get('risk_per_trade', 0.02)
        self.max_positions = config.get('trading', {}).get('max_positions', 5)
        self.max_total_risk = config.get('trading', {}).get('max_total_risk', 0.06)

        # Loss limits
        self.daily_loss_limit = config.get('risk_management', {}).get('daily_loss_limit', 0.05)
        self.weekly_loss_limit = config.get('risk_management', {}).get('weekly_loss_limit', 0.10)
        self.auto_disable_on_limit = config.get('risk_management', {}).get('auto_disable_on_limit', True)

        # Tracking
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.last_reset_day = datetime.now().date()
        self.last_reset_week = datetime.now().isocalendar()[1]
        self.trading_enabled = True

        logger.info("Risk manager initialized")

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        instrument: str,
        pip_value: float = 0.0001,
        custom_risk: Optional[float] = None
    ) -> int:
        """
        Calculate position size based on risk parameters.

        Args:
            account_balance: Current account balance
            entry_price: Entry price for the trade
            stop_loss: Stop loss price
            instrument: Instrument symbol
            pip_value: Pip value for the instrument
            custom_risk: Custom risk percentage (overrides default)

        Returns:
            Position size in units
        """
        # Use custom risk or default
        risk_percent = custom_risk or self.risk_per_trade

        # Calculate risk amount in currency
        risk_amount = account_balance * risk_percent

        # Calculate stop loss distance in price
        sl_distance = abs(entry_price - stop_loss)

        if sl_distance == 0:
            logger.warning("Stop loss distance is zero, using minimum position size")
            return 1

        # Calculate position size
        # Risk amount = Position size * Stop loss distance
        position_size = int(risk_amount / sl_distance)

        # Get instrument-specific config
        instrument_config = self.config.get('instruments', {}).get(instrument, {})
        min_size = instrument_config.get('min_trade_size', 1)
        max_size = instrument_config.get('max_trade_size', 10000000)

        # Ensure position size is within limits
        position_size = max(min_size, min(position_size, max_size))

        logger.info(
            f"Position size calculated: {position_size} units "
            f"(Risk: ${risk_amount:.2f}, SL Distance: {sl_distance:.5f})"
        )

        return position_size

    def calculate_position_size_by_pips(
        self,
        account_balance: float,
        stop_loss_pips: float,
        instrument: str,
        pip_value: float = 0.0001,
        custom_risk: Optional[float] = None
    ) -> int:
        """
        Calculate position size based on stop loss in pips.

        Args:
            account_balance: Current account balance
            stop_loss_pips: Stop loss distance in pips
            instrument: Instrument symbol
            pip_value: Value of one pip
            custom_risk: Custom risk percentage

        Returns:
            Position size in units
        """
        risk_percent = custom_risk or self.risk_per_trade
        risk_amount = account_balance * risk_percent

        # Calculate position size
        # For forex: position_size = risk_amount / (pips * pip_value * lot_size)
        # Simplified: position_size = risk_amount / (pips * pip_value)
        if stop_loss_pips == 0:
            return 1

        position_size = int(risk_amount / (stop_loss_pips * pip_value))

        # Get instrument-specific limits
        instrument_config = self.config.get('instruments', {}).get(instrument, {})
        min_size = instrument_config.get('min_trade_size', 1)
        max_size = instrument_config.get('max_trade_size', 10000000)

        position_size = max(min_size, min(position_size, max_size))

        logger.info(
            f"Position size by pips: {position_size} units "
            f"(Risk: ${risk_amount:.2f}, SL: {stop_loss_pips} pips)"
        )

        return position_size

    def can_open_position(
        self,
        current_positions: int,
        account_balance: float,
        proposed_risk: float
    ) -> tuple[bool, str]:
        """
        Check if a new position can be opened.

        Args:
            current_positions: Number of current open positions
            account_balance: Current account balance
            proposed_risk: Risk amount for the proposed trade

        Returns:
            Tuple of (can_open, reason)
        """
        # Check if trading is enabled
        if not self.trading_enabled:
            return False, "Trading is disabled due to risk limits"

        # Check maximum positions
        if current_positions >= self.max_positions:
            return False, f"Maximum positions reached ({self.max_positions})"

        # Check daily loss limit
        daily_loss_percent = abs(self.daily_pnl) / account_balance if account_balance > 0 else 0
        if self.daily_pnl < 0 and daily_loss_percent >= self.daily_loss_limit:
            if self.auto_disable_on_limit:
                self.trading_enabled = False
            return False, f"Daily loss limit reached ({self.daily_loss_limit * 100}%)"

        # Check weekly loss limit
        weekly_loss_percent = abs(self.weekly_pnl) / account_balance if account_balance > 0 else 0
        if self.weekly_pnl < 0 and weekly_loss_percent >= self.weekly_loss_limit:
            if self.auto_disable_on_limit:
                self.trading_enabled = False
            return False, f"Weekly loss limit reached ({self.weekly_loss_limit * 100}%)"

        # Check total risk
        current_risk_percent = proposed_risk / account_balance if account_balance > 0 else 0
        if current_risk_percent > self.max_total_risk:
            return False, f"Total risk limit exceeded ({self.max_total_risk * 100}%)"

        return True, "OK"

    def validate_trade(
        self,
        instrument: str,
        entry_price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        spread: Optional[float] = None
    ) -> tuple[bool, str]:
        """
        Validate a trade before execution.

        Args:
            instrument: Instrument symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            spread: Current spread

        Returns:
            Tuple of (is_valid, reason)
        """
        # Get instrument configuration
        instrument_config = self.config.get('instruments', {}).get(instrument, {})

        # Check if instrument is enabled
        if not instrument_config.get('enabled', False):
            return False, f"Instrument {instrument} is not enabled"

        # Check spread
        max_spread = instrument_config.get('max_spread')
        if max_spread and spread and spread > max_spread:
            return False, f"Spread too high: {spread} pips (max: {max_spread})"

        # Validate stop loss
        if stop_loss is not None:
            if stop_loss == entry_price:
                return False, "Stop loss cannot equal entry price"

        # Validate take profit
        if take_profit is not None:
            if take_profit == entry_price:
                return False, "Take profit cannot equal entry price"

        # Validate risk/reward ratio (optional)
        if stop_loss and take_profit:
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0

            min_rr_ratio = instrument_config.get('min_risk_reward_ratio', 0)
            if min_rr_ratio > 0 and rr_ratio < min_rr_ratio:
                return False, f"Risk/reward ratio too low: {rr_ratio:.2f} (min: {min_rr_ratio})"

        return True, "OK"

    def record_trade_result(self, pnl: float):
        """
        Record the result of a closed trade.

        Args:
            pnl: Profit/loss from the trade
        """
        # Reset daily PnL if needed
        current_day = datetime.now().date()
        if current_day != self.last_reset_day:
            logger.info(f"Daily PnL reset. Previous: ${self.daily_pnl:.2f}")
            self.daily_pnl = 0.0
            self.last_reset_day = current_day

        # Reset weekly PnL if needed
        current_week = datetime.now().isocalendar()[1]
        if current_week != self.last_reset_week:
            logger.info(f"Weekly PnL reset. Previous: ${self.weekly_pnl:.2f}")
            self.weekly_pnl = 0.0
            self.last_reset_week = current_week

        # Update PnL
        self.daily_pnl += pnl
        self.weekly_pnl += pnl

        logger.info(
            f"Trade result recorded: ${pnl:.2f} "
            f"(Daily: ${self.daily_pnl:.2f}, Weekly: ${self.weekly_pnl:.2f})"
        )

    def get_risk_status(self, account_balance: float) -> Dict[str, Any]:
        """
        Get current risk status.

        Args:
            account_balance: Current account balance

        Returns:
            Risk status information
        """
        daily_loss_percent = abs(self.daily_pnl) / account_balance if account_balance > 0 else 0
        weekly_loss_percent = abs(self.weekly_pnl) / account_balance if account_balance > 0 else 0

        return {
            'trading_enabled': self.trading_enabled,
            'daily_pnl': self.daily_pnl,
            'weekly_pnl': self.weekly_pnl,
            'daily_loss_percent': daily_loss_percent,
            'weekly_loss_percent': weekly_loss_percent,
            'daily_limit_remaining': max(0, self.daily_loss_limit - daily_loss_percent),
            'weekly_limit_remaining': max(0, self.weekly_loss_limit - weekly_loss_percent),
            'daily_limit': self.daily_loss_limit,
            'weekly_limit': self.weekly_loss_limit
        }

    def enable_trading(self):
        """Enable trading."""
        self.trading_enabled = True
        logger.info("Trading enabled")

    def disable_trading(self):
        """Disable trading."""
        self.trading_enabled = False
        logger.warning("Trading disabled")

    def reset_limits(self):
        """Reset all risk limits (use with caution)."""
        self.daily_pnl = 0.0
        self.weekly_pnl = 0.0
        self.trading_enabled = True
        logger.warning("Risk limits have been reset")
