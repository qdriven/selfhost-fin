"""
VNPY 核心模块

包含主要的应用程序类和服务。
"""

from .main import VnpyApplication
from .data_collector import DataCollectorService
from .web_trader import WebTraderService

__all__ = [
    "VnpyApplication",
    "DataCollectorService", 
    "WebTraderService",
] 