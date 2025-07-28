"""
VNPY 加密货币交易系统

基于 VNPY 框架的现代化加密货币交易系统，
集成 TimescaleDB 时序数据库和 OKX 交易所接口。
"""

__version__ = "1.0.0"
__author__ = "VNPY Crypto Team"
__email__ = "admin@vnpy-crypto.com"

from .core import (
    VnpyApplication,
    DataCollectorService, 
    WebTraderService
)

from .config import (
    DATABASE_CONFIG,
    REDIS_CONFIG,
    OKX_CONFIG,
    SETTINGS
)

__all__ = [
    "VnpyApplication",
    "DataCollectorService",
    "WebTraderService",
    "DATABASE_CONFIG",
    "REDIS_CONFIG", 
    "OKX_CONFIG",
    "SETTINGS",
] 