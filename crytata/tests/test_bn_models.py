"""Unit tests for bn package models."""

import pytest
from datetime import datetime
from crytata.bn.models import (
    TradingType, DataType, Interval, DownloadConfig,
    DownloadProgress, DownloadResult
)


class TestTradingType:
    """Test TradingType enum."""
    
    def test_trading_type_values(self):
        """Test that trading types have correct values."""
        assert TradingType.SPOT.value == "spot"
        assert TradingType.USD_M_FUTURES.value == "um"
        assert TradingType.COIN_M_FUTURES.value == "cm"
    
    def test_trading_type_choices(self):
        """Test that trading types can be used as choices."""
        types = [t.value for t in TradingType]
        assert "spot" in types
        assert "um" in types
        assert "cm" in types


class TestDataType:
    """Test DataType enum."""
    
    def test_data_type_values(self):
        """Test that data types have correct values."""
        assert DataType.KLINES.value == "klines"
        assert DataType.TRADES.value == "trades"
        assert DataType.AGGRADES.value == "aggTrades"
        assert DataType.MARK_PRICE_KLINES.value == "markPriceKlines"
        assert DataType.INDEX_PRICE_KLINES.value == "indexPriceKlines"
        assert DataType.PREMIUM_INDEX_KLINES.value == "premiumIndexKlines"


class TestInterval:
    """Test Interval enum."""
    
    def test_interval_values(self):
        """Test that intervals have correct values."""
        assert Interval.MINUTE_1.value == "1m"
        assert Interval.MINUTE_5.value == "5m"
        assert Interval.HOUR_1.value == "1h"
        assert Interval.DAY_1.value == "1d"
        assert Interval.WEEK_1.value == "1w"
        assert Interval.MONTH_1.value == "1mo"
    
    def test_interval_choices(self):
        """Test that intervals can be used as choices."""
        intervals = [i.value for i in Interval]
        assert "1m" in intervals
        assert "1h" in intervals
        assert "1d" in intervals


class TestDownloadConfig:
    """Test DownloadConfig model."""
    
    def test_download_config_defaults(self):
        """Test DownloadConfig default values."""
        config = DownloadConfig(data_type=DataType.KLINES)
        
        assert config.trading_type == TradingType.SPOT
        assert config.data_type == DataType.KLINES
        assert config.symbols == []
        assert config.intervals is None
        assert config.start_date is None
        assert config.end_date is None
        assert config.output_dir == "data"
        assert config.proxy is None
        assert config.resume is True
        assert config.progress_file == ".download_progress.json"
        assert config.max_retries == 3
        assert config.timeout == 30
    
    def test_download_config_custom_values(self):
        """Test DownloadConfig with custom values."""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 6, 30)
        
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1, Interval.HOUR_1],
            start_date=start_date,
            end_date=end_date,
            output_dir="custom_data",
            # proxy="http://proxy:8080",
            resume=False,
            max_retries=5,
            timeout=60
        )
        
        assert config.trading_type == TradingType.USD_M_FUTURES
        assert config.data_type == DataType.KLINES
        assert config.symbols == ["BTCUSDT"]
        assert config.intervals == [Interval.MINUTE_1, Interval.HOUR_1]
        assert config.start_date == start_date
        assert config.end_date == end_date
        assert config.output_dir == "custom_data"
        # assert config.proxy == "http://proxy:8080"
        assert config.resume is False
        assert config.max_retries == 5
        assert config.timeout == 60
    
    def test_download_config_validation(self):
        """Test DownloadConfig validation."""
        # Should not raise an exception
        config = DownloadConfig(
            data_type=DataType.TRADES,
            symbols=["BTCUSDT"]
        )
        assert config is not None


class TestDownloadProgress:
    """Test DownloadProgress model."""
    
    def test_download_progress_defaults(self):
        """Test DownloadProgress default values."""
        progress = DownloadProgress(config_id="test123")
        
        assert progress.config_id == "test123"
        assert progress.total_files == 0
        assert progress.completed_files == 0
        assert progress.failed_files == 0
        assert progress.current_file is None
        assert progress.start_time is None
        assert progress.last_update is None
        assert progress.status == "pending"
        assert progress.errors == []
    
    def test_download_progress_custom_values(self):
        """Test DownloadProgress with custom values."""
        start_time = datetime.now()
        
        progress = DownloadProgress(
            config_id="test123",
            total_files=100,
            completed_files=50,
            failed_files=5,
            current_file="test.zip",
            start_time=start_time,
            status="downloading",
            errors=["Error 1", "Error 2"]
        )
        
        assert progress.config_id == "test123"
        assert progress.total_files == 100
        assert progress.completed_files == 50
        assert progress.failed_files == 5
        assert progress.current_file == "test.zip"
        assert progress.start_time == start_time
        assert progress.status == "downloading"
        assert progress.errors == ["Error 1", "Error 2"]


class TestDownloadResult:
    """Test DownloadResult model."""
    
    def test_download_result_defaults(self):
        """Test DownloadResult default values."""
        result = DownloadResult(
            success=True,
            output_dir="data"
        )
        
        assert result.success is True
        assert result.files_downloaded == 0
        assert result.total_size == 0
        assert result.duration is None
        assert result.errors == []
        assert result.output_dir == "data"
    
    def test_download_result_custom_values(self):
        """Test DownloadResult with custom values."""
        result = DownloadResult(
            success=False,
            files_downloaded=95,
            total_size=1024000,
            duration=120.5,
            errors=["Network error", "File not found"],
            output_dir="custom_data"
        )
        
        assert result.success is False
        assert result.files_downloaded == 95
        assert result.total_size == 1024000
        assert result.duration == 120.5
        assert result.errors == ["Network error", "File not found"]
        assert result.output_dir == "custom_data"
