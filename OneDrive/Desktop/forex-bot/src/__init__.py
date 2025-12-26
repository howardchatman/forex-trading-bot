"""
Forex Trading Bot Package
"""
from .config_loader import ConfigLoader, get_config
from .oanda_client import OandaClient
from .tradingview_webhook import TradingViewWebhook
from .instrument_manager import InstrumentManager, get_instrument_manager, AssetType
from .risk_manager import RiskManager
from .trade_executor import TradeExecutor
from .logger_config import setup_logger, get_logger

__version__ = '1.0.0'

__all__ = [
    'ConfigLoader',
    'get_config',
    'OandaClient',
    'TradingViewWebhook',
    'InstrumentManager',
    'get_instrument_manager',
    'AssetType',
    'RiskManager',
    'TradeExecutor',
    'setup_logger',
    'get_logger',
]
