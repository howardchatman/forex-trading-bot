"""
Logging configuration for the trading bot.
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import colorlog


def setup_logger(
    name: str = 'forex_bot',
    level: str = 'INFO',
    log_to_file: bool = True,
    log_dir: str = 'logs',
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
        max_bytes: Maximum log file size
        backup_count: Number of backup files to keep

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with color
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))

    # Color formatter for console
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / f'{name}.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file

        # File formatter (no colors)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Separate file for errors
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / f'{name}_errors.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        # Trade log file
        trade_handler = logging.handlers.RotatingFileHandler(
            log_path / 'trades.log',
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        trade_handler.setLevel(logging.INFO)
        trade_handler.setFormatter(file_formatter)

        # Add filter to only log trade-related messages
        class TradeFilter(logging.Filter):
            def filter(self, record):
                return 'trade' in record.getMessage().lower() or 'order' in record.getMessage().lower()

        trade_handler.addFilter(TradeFilter())
        logger.addHandler(trade_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to 'forex_bot')

    Returns:
        Logger instance
    """
    return logging.getLogger(name or 'forex_bot')
