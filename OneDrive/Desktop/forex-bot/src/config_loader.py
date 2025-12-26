"""
Configuration loader for the forex trading bot.
Loads settings from YAML config and environment variables.
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration settings."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to config YAML file. Defaults to config/config.yaml
        """
        # Load environment variables
        load_dotenv()

        # Set config path
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._merge_env_variables()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Using default configuration")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config or {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'oanda': {
                'environment': 'practice',
                'base_url': 'https://api-fxpractice.oanda.com'
            },
            'tradingview': {
                'enabled': True,
                'webhook_port': 5000
            },
            'trading': {
                'enabled_assets': {'forex': True, 'futures': True},
                'risk_per_trade': 0.02,
                'max_positions': 5,
                'max_total_risk': 0.06,
                'position_sizing': {'method': 'risk_based'}
            },
            'risk_management': {
                'daily_loss_limit': 0.05,
                'weekly_loss_limit': 0.10,
                'auto_disable_on_limit': True
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_dir': 'logs'
            }
        }

    def _merge_env_variables(self):
        """Override config with environment variables."""
        # OANDA configuration
        if os.getenv('OANDA_ACCOUNT_ID'):
            self.config.setdefault('oanda', {})
            self.config['oanda']['account_id'] = os.getenv('OANDA_ACCOUNT_ID')

        if os.getenv('OANDA_API_KEY'):
            self.config.setdefault('oanda', {})
            self.config['oanda']['api_key'] = os.getenv('OANDA_API_KEY')

        if os.getenv('OANDA_ENVIRONMENT'):
            self.config.setdefault('oanda', {})
            env = os.getenv('OANDA_ENVIRONMENT')
            self.config['oanda']['environment'] = env
            # Update base URL based on environment
            if env == 'live':
                self.config['oanda']['base_url'] = 'https://api-fxtrade.oanda.com'
            else:
                self.config['oanda']['base_url'] = 'https://api-fxpractice.oanda.com'

        # TradingView webhook secret
        if os.getenv('TRADINGVIEW_WEBHOOK_SECRET'):
            self.config.setdefault('tradingview', {})
            self.config['tradingview']['webhook_secret'] = os.getenv('TRADINGVIEW_WEBHOOK_SECRET')

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Path to config value (e.g., 'oanda.account_id')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_oanda_config(self) -> Dict[str, Any]:
        """Get OANDA API configuration."""
        return self.config.get('oanda', {})

    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading preferences configuration."""
        return self.config.get('trading', {})

    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration."""
        return self.config.get('risk_management', {})

    def get_instrument_config(self, instrument: str) -> Dict[str, Any]:
        """
        Get instrument-specific configuration.

        Args:
            instrument: Instrument symbol (e.g., 'EUR_USD')

        Returns:
            Instrument configuration or empty dict
        """
        instruments = self.config.get('instruments', {})
        return instruments.get(instrument, {})

    def is_instrument_enabled(self, instrument: str) -> bool:
        """Check if an instrument is enabled for trading."""
        config = self.get_instrument_config(instrument)
        return config.get('enabled', False)

    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        self._merge_env_variables()
        logger.info("Configuration reloaded")


# Global config instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance
