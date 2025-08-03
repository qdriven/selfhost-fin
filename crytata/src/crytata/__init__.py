"""Cryptocurrency data collection and processing tool for Binance public data."""

__version__ = "0.1.0"
__author__ = "Patrick"
__email__ = "patrick@example.com"

from .core import BinanceDataCollector, DataProcessor
from .models import KlineData, TradeData, TickerData
from .storage import DataStorage
from .historical_downloader import BinanceHistoricalDownloader
from .timescaledb_config import TimescaleDBConfig, TimescaleDBStorage

__all__ = [
    "BinanceDataCollector",
    "DataProcessor", 
    "KlineData",
    "TradeData",
    "TickerData",
    "DataStorage",
    "BinanceHistoricalDownloader",
    "TimescaleDBConfig",
    "TimescaleDBStorage",
] 