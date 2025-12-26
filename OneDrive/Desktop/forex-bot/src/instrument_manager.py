"""
Instrument manager for handling forex pairs and futures contracts.
"""
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Asset type enumeration."""
    FOREX = "forex"
    FUTURES = "futures"
    CFD = "cfd"
    COMMODITY = "commodity"
    INDEX = "index"


class Instrument:
    """Represents a tradeable instrument."""

    def __init__(
        self,
        symbol: str,
        asset_type: AssetType,
        pip_value: float = 0.0001,
        min_trade_size: int = 1,
        max_trade_size: int = 10000000,
        description: str = ""
    ):
        """
        Initialize an instrument.

        Args:
            symbol: Instrument symbol (e.g., 'EUR_USD', 'NQ')
            asset_type: Type of asset
            pip_value: Value of one pip
            min_trade_size: Minimum trade size
            max_trade_size: Maximum trade size
            description: Instrument description
        """
        self.symbol = symbol
        self.asset_type = asset_type
        self.pip_value = pip_value
        self.min_trade_size = min_trade_size
        self.max_trade_size = max_trade_size
        self.description = description

    def __repr__(self):
        return f"<Instrument {self.symbol} ({self.asset_type.value})>"


class InstrumentManager:
    """Manages available trading instruments."""

    # Common forex pairs and their pip values
    FOREX_PAIRS = {
        'EUR_USD': {'pip_value': 0.0001, 'description': 'Euro / US Dollar'},
        'GBP_USD': {'pip_value': 0.0001, 'description': 'British Pound / US Dollar'},
        'USD_JPY': {'pip_value': 0.01, 'description': 'US Dollar / Japanese Yen'},
        'USD_CHF': {'pip_value': 0.0001, 'description': 'US Dollar / Swiss Franc'},
        'AUD_USD': {'pip_value': 0.0001, 'description': 'Australian Dollar / US Dollar'},
        'USD_CAD': {'pip_value': 0.0001, 'description': 'US Dollar / Canadian Dollar'},
        'NZD_USD': {'pip_value': 0.0001, 'description': 'New Zealand Dollar / US Dollar'},
        'EUR_GBP': {'pip_value': 0.0001, 'description': 'Euro / British Pound'},
        'EUR_JPY': {'pip_value': 0.01, 'description': 'Euro / Japanese Yen'},
        'GBP_JPY': {'pip_value': 0.01, 'description': 'British Pound / Japanese Yen'},
    }

    # Common futures contracts
    FUTURES_CONTRACTS = {
        'ES': {'pip_value': 12.5, 'description': 'E-mini S&P 500 Futures'},
        'NQ': {'pip_value': 5.0, 'description': 'E-mini NASDAQ-100 Futures'},
        'YM': {'pip_value': 5.0, 'description': 'E-mini Dow Futures'},
        'RTY': {'pip_value': 5.0, 'description': 'E-mini Russell 2000 Futures'},
        'CL': {'pip_value': 10.0, 'description': 'Crude Oil Futures'},
        'GC': {'pip_value': 10.0, 'description': 'Gold Futures'},
        'SI': {'pip_value': 50.0, 'description': 'Silver Futures'},
        '6E': {'pip_value': 12.5, 'description': 'Euro FX Futures'},
        '6B': {'pip_value': 6.25, 'description': 'British Pound Futures'},
        '6J': {'pip_value': 12.5, 'description': 'Japanese Yen Futures'},
    }

    def __init__(self):
        """Initialize the instrument manager."""
        self.instruments: Dict[str, Instrument] = {}
        self._load_default_instruments()

    def _load_default_instruments(self):
        """Load default forex pairs and futures contracts."""
        # Load forex pairs
        for symbol, data in self.FOREX_PAIRS.items():
            self.add_instrument(
                symbol=symbol,
                asset_type=AssetType.FOREX,
                pip_value=data['pip_value'],
                description=data['description']
            )

        # Load futures contracts
        for symbol, data in self.FUTURES_CONTRACTS.items():
            self.add_instrument(
                symbol=symbol,
                asset_type=AssetType.FUTURES,
                pip_value=data['pip_value'],
                description=data['description']
            )

        logger.info(f"Loaded {len(self.instruments)} default instruments")

    def add_instrument(
        self,
        symbol: str,
        asset_type: AssetType,
        pip_value: float = 0.0001,
        min_trade_size: int = 1,
        max_trade_size: int = 10000000,
        description: str = ""
    ) -> Instrument:
        """
        Add an instrument to the manager.

        Args:
            symbol: Instrument symbol
            asset_type: Type of asset
            pip_value: Value of one pip
            min_trade_size: Minimum trade size
            max_trade_size: Maximum trade size
            description: Instrument description

        Returns:
            Created instrument
        """
        instrument = Instrument(
            symbol=symbol,
            asset_type=asset_type,
            pip_value=pip_value,
            min_trade_size=min_trade_size,
            max_trade_size=max_trade_size,
            description=description
        )
        self.instruments[symbol] = instrument
        logger.debug(f"Added instrument: {instrument}")
        return instrument

    def get_instrument(self, symbol: str) -> Optional[Instrument]:
        """
        Get an instrument by symbol.

        Args:
            symbol: Instrument symbol

        Returns:
            Instrument or None if not found
        """
        return self.instruments.get(symbol)

    def get_instruments_by_type(self, asset_type: AssetType) -> List[Instrument]:
        """
        Get all instruments of a specific type.

        Args:
            asset_type: Asset type to filter by

        Returns:
            List of instruments
        """
        return [
            inst for inst in self.instruments.values()
            if inst.asset_type == asset_type
        ]

    def get_forex_pairs(self) -> List[Instrument]:
        """Get all forex pairs."""
        return self.get_instruments_by_type(AssetType.FOREX)

    def get_futures_contracts(self) -> List[Instrument]:
        """Get all futures contracts."""
        return self.get_instruments_by_type(AssetType.FUTURES)

    def is_valid_instrument(self, symbol: str) -> bool:
        """Check if an instrument symbol is valid."""
        return symbol in self.instruments

    def get_pip_value(self, symbol: str) -> float:
        """
        Get pip value for an instrument.

        Args:
            symbol: Instrument symbol

        Returns:
            Pip value or default 0.0001
        """
        instrument = self.get_instrument(symbol)
        return instrument.pip_value if instrument else 0.0001

    def calculate_pips(self, symbol: str, price_diff: float) -> float:
        """
        Calculate number of pips from a price difference.

        Args:
            symbol: Instrument symbol
            price_diff: Price difference

        Returns:
            Number of pips
        """
        pip_value = self.get_pip_value(symbol)
        return abs(price_diff) / pip_value

    def calculate_price_from_pips(self, symbol: str, pips: float) -> float:
        """
        Calculate price difference from number of pips.

        Args:
            symbol: Instrument symbol
            pips: Number of pips

        Returns:
            Price difference
        """
        pip_value = self.get_pip_value(symbol)
        return pips * pip_value

    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize instrument symbol.

        Converts various formats to standard format:
        - EUR/USD -> EUR_USD
        - EURUSD -> EUR_USD
        - eur_usd -> EUR_USD

        Args:
            symbol: Input symbol

        Returns:
            Normalized symbol
        """
        # Remove forward slashes
        symbol = symbol.replace('/', '_')

        # Handle symbols without separator
        if '_' not in symbol and len(symbol) == 6:
            # Assume it's a forex pair like EURUSD
            symbol = f"{symbol[:3]}_{symbol[3:]}"

        # Convert to uppercase
        symbol = symbol.upper()

        return symbol

    def get_all_symbols(self) -> List[str]:
        """Get list of all available symbols."""
        return list(self.instruments.keys())

    def print_instruments(self):
        """Print all available instruments."""
        print("\nAvailable Instruments:")
        print("=" * 60)

        for asset_type in AssetType:
            instruments = self.get_instruments_by_type(asset_type)
            if instruments:
                print(f"\n{asset_type.value.upper()}:")
                for inst in instruments:
                    print(f"  {inst.symbol:15} - {inst.description}")


# Global instrument manager instance
_manager_instance: Optional[InstrumentManager] = None


def get_instrument_manager() -> InstrumentManager:
    """
    Get the global instrument manager instance.

    Returns:
        InstrumentManager instance
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = InstrumentManager()
    return _manager_instance
