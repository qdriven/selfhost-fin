"""Data models for cryptocurrency data."""

from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum

from pydantic import BaseModel, Field


class TradingType(str, Enum):
    """Trading type enumeration."""
    SPOT = "spot"
    UM_FUTURES = "um"  # USD-M futures
    CM_FUTURES = "cm"  # COIN-M futures


class DataType(str, Enum):
    """Data type enumeration."""
    KLINES = "klines"
    TRADES = "trades"
    AGG_TRADES = "aggTrades"
    MARK_PRICE_KLINES = "markPriceKlines"
    INDEX_PRICE_KLINES = "indexPriceKlines"
    PREMIUM_INDEX_KLINES = "premiumIndexKlines"


class TimePeriod(str, Enum):
    """Time period enumeration."""
    DAILY = "daily"
    MONTHLY = "monthly"


class DownloadConfig(BaseModel):
    """Download configuration model."""
    
    proxy_url: Optional[str] = Field(None, description="HTTP/HTTPS proxy URL")
    proxy_username: Optional[str] = Field(None, description="Proxy username")
    proxy_password: Optional[str] = Field(None, description="Proxy password")
    resume_downloads: bool = Field(True, description="Resume incomplete downloads")
    concurrent_downloads: int = Field(3, description="Number of concurrent downloads")
    chunk_size: int = Field(8192, description="Download chunk size in bytes")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DownloadProgress(BaseModel):
    """Download progress tracking model."""
    
    file_path: str = Field(..., description="File path being downloaded")
    url: str = Field(..., description="Download URL")
    total_size: int = Field(0, description="Total file size in bytes")
    downloaded_size: int = Field(0, description="Downloaded size in bytes")
    status: Literal["pending", "downloading", "completed", "failed", "paused"] = Field("pending", description="Download status")
    started_at: Optional[datetime] = Field(None, description="Download start time")
    completed_at: Optional[datetime] = Field(None, description="Download completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class KlineData(BaseModel):
    """Kline/Candlestick data model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    open_time: datetime = Field(..., description="Open time of the kline")
    close_time: datetime = Field(..., description="Close time of the kline")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    close_price: float = Field(..., description="Close price")
    volume: float = Field(..., description="Volume")
    quote_volume: float = Field(..., description="Quote asset volume")
    trade_count: int = Field(..., description="Number of trades")
    taker_buy_volume: float = Field(..., description="Taker buy volume")
    taker_buy_quote_volume: float = Field(..., description="Taker buy quote volume")
    interval: str = Field(..., description="Kline interval (1m, 5m, 1h, etc.)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TradeData(BaseModel):
    """Trade data model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    trade_id: int = Field(..., description="Trade ID")
    price: float = Field(..., description="Trade price")
    quantity: float = Field(..., description="Trade quantity")
    quote_quantity: float = Field(..., description="Quote asset quantity")
    time: datetime = Field(..., description="Trade time")
    is_buyer_maker: bool = Field(..., description="Whether the buyer is the maker")
    is_best_match: Optional[bool] = Field(None, description="Whether this is the best match")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TickerData(BaseModel):
    """24hr ticker data model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    price_change: float = Field(..., description="Price change")
    price_change_percent: float = Field(..., description="Price change percent")
    weighted_avg_price: float = Field(..., description="Weighted average price")
    prev_close_price: float = Field(..., description="Previous close price")
    last_price: float = Field(..., description="Last price")
    last_qty: float = Field(..., description="Last quantity")
    bid_price: float = Field(..., description="Bid price")
    ask_price: float = Field(..., description="Ask price")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    volume: float = Field(..., description="Volume")
    quote_volume: float = Field(..., description="Quote asset volume")
    open_time: datetime = Field(..., description="Open time")
    close_time: datetime = Field(..., description="Close time")
    first_id: int = Field(..., description="First trade ID")
    last_id: int = Field(..., description="Last trade ID")
    count: int = Field(..., description="Trade count")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }