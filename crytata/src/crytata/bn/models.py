"""Data models for Binance data downloader."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TradingType(str, Enum):
    """Trading type enumeration."""
    SPOT = "spot"
    USD_M_FUTURES = "um"
    COIN_M_FUTURES = "cm"


class DataType(str, Enum):
    """Data type enumeration."""
    KLINES = "klines"
    TRADES = "trades"
    AGGRADES = "aggTrades"
    MARK_PRICE_KLINES = "markPriceKlines"
    INDEX_PRICE_KLINES = "indexPriceKlines"
    PREMIUM_INDEX_KLINES = "premiumIndexKlines"


class Interval(str, Enum):
    """Kline interval enumeration."""
    SECOND_1 = "1s"
    MINUTE_1 = "1m"
    MINUTE_3 = "3m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    DAY_3 = "3d"
    WEEK_1 = "1w"
    MONTH_1 = "1mo"


class DownloadConfig(BaseModel):
    """Configuration for data download."""
    trading_type: TradingType = Field(default=TradingType.SPOT, description="Trading type")
    data_type: DataType = Field(description="Data type to download")
    symbols: List[str] = Field(default_factory=list, description="List of symbols")
    intervals: Optional[List[Interval]] = Field(default=None, description="List of intervals (for klines)")
    start_date: Optional[datetime] = Field(default=None, description="Start date")
    end_date: Optional[datetime] = Field(default=None, description="End date")
    output_dir: str = Field(default="data", description="Output directory")
    proxy: Optional[str] = Field(default=None, description="HTTP proxy URL")
    resume: bool = Field(default=True, description="Resume interrupted downloads")
    progress_file: str = Field(default=".download_progress.json", description="Progress file path")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class DownloadProgress(BaseModel):
    """Download progress tracking."""
    config_id: str = Field(description="Unique identifier for download configuration")
    total_files: int = Field(default=0, description="Total number of files to download")
    completed_files: int = Field(default=0, description="Number of completed files")
    failed_files: int = Field(default=0, description="Number of failed files")
    current_file: Optional[str] = Field(default=None, description="Currently downloading file")
    start_time: Optional[datetime] = Field(default=None, description="Download start time")
    last_update: Optional[datetime] = Field(default=None, description="Last progress update")
    status: str = Field(default="pending", description="Download status")
    errors: List[str] = Field(default_factory=list, description="List of error messages")


class DownloadResult(BaseModel):
    """Result of a download operation."""
    success: bool = Field(description="Whether download was successful")
    files_downloaded: int = Field(default=0, description="Number of files downloaded")
    total_size: int = Field(default=0, description="Total size of downloaded files in bytes")
    duration: Optional[float] = Field(default=None, description="Download duration in seconds")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    output_dir: str = Field(description="Output directory path")
