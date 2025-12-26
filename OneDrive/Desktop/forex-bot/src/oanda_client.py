"""
OANDA API client for forex and futures trading.
"""
import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import accounts, orders, positions, pricing, trades, instruments
from oandapyV20.exceptions import V20Error
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class OandaClient:
    """Client for interacting with OANDA API."""

    def __init__(self, account_id: str, api_key: str, environment: str = 'practice'):
        """
        Initialize OANDA client.

        Args:
            account_id: OANDA account ID
            api_key: OANDA API key
            environment: 'practice' or 'live'
        """
        self.account_id = account_id
        self.environment = environment

        # Initialize API client
        self.client = API(
            access_token=api_key,
            environment=environment
        )

        logger.info(f"OANDA client initialized for {environment} environment")

    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary information.

        Returns:
            Account summary data
        """
        try:
            endpoint = accounts.AccountSummary(accountID=self.account_id)
            response = self.client.request(endpoint)
            return response.get('account', {})
        except V20Error as e:
            logger.error(f"Error getting account summary: {e}")
            raise

    def get_account_balance(self) -> float:
        """
        Get current account balance.

        Returns:
            Account balance
        """
        summary = self.get_account_summary()
        return float(summary.get('balance', 0))

    def get_current_positions(self) -> List[Dict[str, Any]]:
        """
        Get all current open positions.

        Returns:
            List of open positions
        """
        try:
            endpoint = positions.OpenPositions(accountID=self.account_id)
            response = self.client.request(endpoint)
            return response.get('positions', [])
        except V20Error as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def get_position_count(self) -> int:
        """Get the number of open positions."""
        positions = self.get_current_positions()
        return len([p for p in positions if float(p.get('long', {}).get('units', 0)) != 0
                    or float(p.get('short', {}).get('units', 0)) != 0])

    def get_current_price(self, instrument: str) -> Dict[str, float]:
        """
        Get current bid/ask prices for an instrument.

        Args:
            instrument: Instrument symbol (e.g., 'EUR_USD')

        Returns:
            Dict with 'bid' and 'ask' prices
        """
        try:
            params = {"instruments": instrument}
            endpoint = pricing.PricingInfo(accountID=self.account_id, params=params)
            response = self.client.request(endpoint)

            prices = response.get('prices', [])
            if prices:
                price = prices[0]
                return {
                    'bid': float(price.get('bids', [{}])[0].get('price', 0)),
                    'ask': float(price.get('asks', [{}])[0].get('price', 0)),
                    'spread': float(price.get('asks', [{}])[0].get('price', 0)) -
                             float(price.get('bids', [{}])[0].get('price', 0))
                }
            return {'bid': 0, 'ask': 0, 'spread': 0}
        except V20Error as e:
            logger.error(f"Error getting price for {instrument}: {e}")
            return {'bid': 0, 'ask': 0, 'spread': 0}

    def place_market_order(
        self,
        instrument: str,
        units: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_stop: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a market order.

        Args:
            instrument: Instrument symbol (e.g., 'EUR_USD')
            units: Number of units (positive for buy, negative for sell)
            stop_loss: Stop loss price
            take_profit: Take profit price
            trailing_stop: Trailing stop distance in pips

        Returns:
            Order response
        """
        order_data = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units)
            }
        }

        # Add stop loss if provided
        if stop_loss is not None:
            order_data["order"]["stopLossOnFill"] = {
                "price": str(stop_loss)
            }

        # Add take profit if provided
        if take_profit is not None:
            order_data["order"]["takeProfitOnFill"] = {
                "price": str(take_profit)
            }

        # Add trailing stop if provided
        if trailing_stop is not None:
            order_data["order"]["trailingStopLossOnFill"] = {
                "distance": str(trailing_stop)
            }

        try:
            endpoint = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.client.request(endpoint)
            logger.info(f"Market order placed: {instrument} {units} units")
            return response
        except V20Error as e:
            logger.error(f"Error placing market order: {e}")
            raise

    def place_limit_order(
        self,
        instrument: str,
        units: int,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a limit order.

        Args:
            instrument: Instrument symbol
            units: Number of units (positive for buy, negative for sell)
            price: Limit price
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Order response
        """
        order_data = {
            "order": {
                "type": "LIMIT",
                "instrument": instrument,
                "units": str(units),
                "price": str(price),
                "timeInForce": "GTC"
            }
        }

        if stop_loss is not None:
            order_data["order"]["stopLossOnFill"] = {"price": str(stop_loss)}

        if take_profit is not None:
            order_data["order"]["takeProfitOnFill"] = {"price": str(take_profit)}

        try:
            endpoint = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.client.request(endpoint)
            logger.info(f"Limit order placed: {instrument} {units} units at {price}")
            return response
        except V20Error as e:
            logger.error(f"Error placing limit order: {e}")
            raise

    def close_position(self, instrument: str, units: Optional[str] = "ALL") -> Dict[str, Any]:
        """
        Close a position.

        Args:
            instrument: Instrument symbol
            units: Number of units to close or "ALL"

        Returns:
            Close response
        """
        try:
            # Determine long or short units
            data = {
                "longUnits": units if units == "ALL" else "NONE",
                "shortUnits": "NONE"
            }

            endpoint = positions.PositionClose(
                accountID=self.account_id,
                instrument=instrument,
                data=data
            )
            response = self.client.request(endpoint)
            logger.info(f"Position closed: {instrument}")
            return response
        except V20Error as e:
            # Try closing short position
            try:
                data = {
                    "longUnits": "NONE",
                    "shortUnits": units if units == "ALL" else "NONE"
                }
                endpoint = positions.PositionClose(
                    accountID=self.account_id,
                    instrument=instrument,
                    data=data
                )
                response = self.client.request(endpoint)
                logger.info(f"Position closed: {instrument}")
                return response
            except V20Error as e2:
                logger.error(f"Error closing position: {e2}")
                raise

    def get_open_trades(self) -> List[Dict[str, Any]]:
        """
        Get all open trades.

        Returns:
            List of open trades
        """
        try:
            endpoint = trades.OpenTrades(accountID=self.account_id)
            response = self.client.request(endpoint)
            return response.get('trades', [])
        except V20Error as e:
            logger.error(f"Error getting open trades: {e}")
            return []

    def modify_trade(
        self,
        trade_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_stop: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing trade's stop loss or take profit.

        Args:
            trade_id: Trade ID
            stop_loss: New stop loss price
            take_profit: New take profit price
            trailing_stop: Trailing stop distance

        Returns:
            Modification response
        """
        data = {}

        if stop_loss is not None:
            data["stopLoss"] = {"price": str(stop_loss)}

        if take_profit is not None:
            data["takeProfit"] = {"price": str(take_profit)}

        if trailing_stop is not None:
            data["trailingStopLoss"] = {"distance": str(trailing_stop)}

        try:
            endpoint = trades.TradeCRCDO(
                accountID=self.account_id,
                tradeID=trade_id,
                data=data
            )
            response = self.client.request(endpoint)
            logger.info(f"Trade modified: {trade_id}")
            return response
        except V20Error as e:
            logger.error(f"Error modifying trade: {e}")
            raise

    def get_candles(
        self,
        instrument: str,
        granularity: str = "H1",
        count: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Get historical candle data.

        Args:
            instrument: Instrument symbol
            granularity: Candle granularity (M1, M5, H1, H4, D, etc.)
            count: Number of candles to retrieve

        Returns:
            List of candles
        """
        try:
            params = {
                "granularity": granularity,
                "count": count
            }
            endpoint = instruments.InstrumentsCandles(instrument=instrument, params=params)
            response = self.client.request(endpoint)
            return response.get('candles', [])
        except V20Error as e:
            logger.error(f"Error getting candles: {e}")
            return []
