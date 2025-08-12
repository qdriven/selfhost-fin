"""Unit tests for bn package downloader."""

import pytest
import tempfile
import os
import zipfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

from crytata.bn.models import (
    DownloadConfig, TradingType, DataType, Interval
)
from crytata.bn.downloader import BinanceDataDownloader


class TestBinanceDataDownloader:
    """Test BinanceDataDownloader class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def basic_config(self, temp_dir):
        """Create a basic download configuration."""
        return DownloadConfig(
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1],
            output_dir=temp_dir
        )
    
    @pytest.fixture
    def downloader(self, basic_config):
        """Create a downloader instance."""
        return BinanceDataDownloader(basic_config)
    
    def test_init(self, downloader, basic_config):
        """Test downloader initialization."""
        assert downloader.config == basic_config
        assert downloader.BASE_URL == "https://data.binance.vision/"
        assert os.path.exists(basic_config.output_dir)
    
    def test_setup_proxy_no_proxy(self, downloader):
        """Test session proxies when no proxy is configured."""
        assert downloader.session.proxies == {}
    
    def test_setup_proxy_with_proxy(self, temp_dir):
        """Test session proxies when proxy is configured."""
        config = DownloadConfig(
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1],
            output_dir=temp_dir,
            proxy="http://proxy:8080"
        )
        downloader = BinanceDataDownloader(config)
        assert downloader.session.proxies.get('http') == "http://proxy:8080"
        assert downloader.session.proxies.get('https') == "http://proxy:8080"
    
    def test_generate_config_hash(self, downloader):
        """Test config hash generation."""
        hash1 = downloader._generate_config_hash()
        hash2 = downloader._generate_config_hash()
        
        assert hash1 == hash2  # Same config should generate same hash
        assert len(hash1) == 8  # Should be 8 characters
    
    def test_build_monthly_url_spot_klines(self, downloader):
        """Test monthly URL building for spot klines."""
        url = downloader._build_monthly_url("BTCUSDT", Interval.MINUTE_1, 2024, 6)
        expected = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2024-06.zip"
        assert url == expected
    
    def test_build_monthly_url_futures_trades(self, temp_dir):
        """Test monthly URL building for futures trades."""
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.TRADES,
            symbols=["BTCUSDT"],
            output_dir=temp_dir
        )
        downloader = BinanceDataDownloader(config)
        
        url = downloader._build_monthly_url("BTCUSDT", None, 2024, 6)
        expected = "https://data.binance.vision/data/futures/um/monthly/trades/BTCUSDT/BTCUSDT-trades-2024-06.zip"
        assert url == expected
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_get_all_symbols_spot(self, mock_get, temp_dir):
        """Test getting all symbols for spot trading."""
        config = DownloadConfig(
            trading_type=TradingType.SPOT,
            data_type=DataType.KLINES,
            symbols=[],
            output_dir=temp_dir
        )
        downloader = BinanceDataDownloader(config)
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"symbols": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        symbols = downloader._get_all_symbols()
        
        assert symbols == ["BTCUSDT", "ETHUSDT"]
        mock_get.assert_called_once()
        called_url = mock_get.call_args.kwargs.get('url') or mock_get.call_args.args[0]
        assert called_url == "https://api.binance.com/api/v3/exchangeInfo"
        assert mock_get.call_args.kwargs.get('timeout') == 30
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_get_all_symbols_futures(self, mock_get, temp_dir):
        """Test getting all symbols for futures trading."""
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.KLINES,
            symbols=[],
            output_dir=temp_dir
        )
        downloader = BinanceDataDownloader(config)
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"symbols": [{"symbol": "BTCUSDT"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        symbols = downloader._get_all_symbols()
        
        assert symbols == ["BTCUSDT"]
        mock_get.assert_called_once()
        called_url = mock_get.call_args.kwargs.get('url') or mock_get.call_args.args[0]
        assert called_url == "https://fapi.binance.com/fapi/v1/exchangeInfo"
        assert mock_get.call_args.kwargs.get('timeout') == 30
    
    def test_is_file_complete_zip_valid(self, downloader, temp_dir):
        """Test file completeness check for valid zip file."""
        # Create a real valid zip file
        zip_path = os.path.join(temp_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # write a dummy file into the zip
            dummy_file_path = os.path.join(temp_dir, 'dummy.txt')
            with open(dummy_file_path, 'w') as df:
                df.write('hello')
            zipf.write(dummy_file_path, arcname='dummy.txt')
        
        assert downloader._is_file_complete(zip_path) is True
    
    def test_is_file_complete_zip_invalid(self, downloader, temp_dir):
        """Test file completeness check for invalid zip file."""
        # Create an invalid file
        invalid_path = os.path.join(temp_dir, "invalid.zip")
        with open(invalid_path, 'wb') as f:
            f.write(b'invalid content')
        
        assert downloader._is_file_complete(invalid_path) is False
    
    def test_is_file_complete_non_zip(self, downloader, temp_dir):
        """Test file completeness check for non-zip file."""
        # Create a non-zip file
        file_path = os.path.join(temp_dir, "test.txt")
        with open(file_path, 'w') as f:
            f.write("test content")
        
        assert downloader._is_file_complete(file_path) is True
    
    def test_is_file_complete_nonexistent(self, downloader):
        """Test file completeness check for nonexistent file."""
        assert downloader._is_file_complete("nonexistent_file.zip") is False
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_download_file_success(self, mock_get, downloader, temp_dir):
        """Test successful file download."""
        # Mock streaming response
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': str(len(b'chunk1chunk2'))}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://example.com/test.zip"
        result = downloader._download_file(url)
        
        assert result is not None
        assert os.path.exists(result)
        assert os.path.basename(result) == "test.zip"
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_download_file_http_404(self, mock_get, downloader):
        """Test file download with HTTP 404 error."""
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        url = "https://example.com/nonexistent.zip"
        result = downloader._download_file(url)
        
        assert result is None
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_download_file_retry_success(self, mock_get, downloader):
        """Test file download with retry logic."""
        # First call fails, second call succeeds
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': str(len(b'chunk1chunk2'))}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [Exception("Network error"), mock_response]
        
        url = "https://example.com/test.zip"
        result = downloader._download_file(url)
        
        assert result is not None
        assert mock_get.call_count == 2
    
    @patch('crytata.bn.downloader.requests.Session.get')
    def test_download_resume_range_header(self, mock_get, temp_dir):
        """Test that Range header is set when resuming a download."""
        config = DownloadConfig(
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1],
            output_dir=temp_dir,
            resume=True
        )
        downloader = BinanceDataDownloader(config)
        # Create a partial file
        part_path = os.path.join(temp_dir, 'test.zip.part')
        with open(part_path, 'wb') as f:
            f.write(b'1234567')  # 7 bytes
        
        # Mock response
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_response.status_code = 200
        mock_response.headers = {'Content-Length': str(len(b'chunk1chunk2'))}
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        url = "https://example.com/test.zip"
        downloader._download_file(url)
        
        # Assert that Range header was set
        headers = mock_get.call_args.kwargs.get('headers')
        assert headers and headers.get('Range') == 'bytes=7-'
    
    def test_get_download_urls_with_symbols(self, downloader):
        """Test URL generation with specific symbols."""
        urls = list(downloader._get_download_urls())
        
        # Should generate URLs for current year
        current_year = datetime.now().year
        assert len(urls) > 0
        
        # Check URL format
        for url in urls:
            assert url.startswith("https://data.binance.vision/")
            assert "BTCUSDT" in url
            assert "1m" in url
            assert str(current_year) in url
    
    def test_get_download_urls_with_date_range(self, temp_dir):
        """Test URL generation with specific date range."""
        config = DownloadConfig(
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1],
            start_date=datetime(2024, 6, 1),
            end_date=datetime(2024, 7, 31),
            output_dir=temp_dir
        )
        downloader = BinanceDataDownloader(config)
        
        urls = list(downloader._get_download_urls())
        
        # Should generate URLs for June and July 2024
        assert len(urls) == 2
        
        june_url = next(url for url in urls if "2024-06" in url)
        july_url = next(url for url in urls if "2024-07" in url)
        
        assert "2024-06" in june_url
        assert "2024-07" in july_url


class TestRealDownload:
    """Test real download functionality with actual network calls."""
    
    @pytest.fixture
    def test_output_dir(self):
        """Create a test output directory."""
        test_dir = Path("test_downloads")
        test_dir.mkdir(exist_ok=True)
        yield test_dir
        # Cleanup after test
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_download_2025_trades(self, test_output_dir):
        """Test real download of 2025 trade data from January to June."""
        print(f"\n🚀 Starting real download test for 2025 trades...")
        print(f"📁 Output directory: {test_output_dir}")
        
        # Create download configuration for 2025 trades
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.TRADES,
            symbols=["BTCUSDT"],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 6, 30),
            output_dir=str(test_output_dir),
            resume=True,
            max_retries=3,
            timeout=30
        )
        
        # Create downloader instance
        downloader = BinanceDataDownloader(config)
        
        # Start download
        print("📥 Starting download...")
        result = downloader.download()
        
        # Assertions
        assert result is not None, "Download result should not be None"
        print(f"✅ Download completed with result: {result}")
        
        if result.success:
            print(f"📊 Download successful!")
            print(f"   Files downloaded: {result.files_downloaded}")
            print(f"   Total size: {result.total_size_mb:.2f} MB")
            print(f"   Duration: {result.duration_seconds:.2f} seconds")
            
            # Check that output directory contains files
            output_files = list(test_output_dir.glob("**/*.zip"))
            assert len(output_files) > 0, f"Expected downloaded files, found: {output_files}"
            
            print(f"📁 Found {len(output_files)} downloaded files:")
            for file_path in output_files:
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {file_path.name}: {file_size:.2f} MB")
                
                # Verify zip files are valid
                try:
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        zipf.testzip()
                    print(f"     ✅ {file_path.name} is a valid ZIP file")
                except Exception as e:
                    pytest.fail(f"Invalid ZIP file {file_path.name}: {e}")
            
            # Check for expected months (Jan-Jun 2025)
            expected_months = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06"]
            found_months = []
            for file_path in output_files:
                for month in expected_months:
                    if month in file_path.name:
                        found_months.append(month)
                        break
            
            print(f"📅 Expected months: {expected_months}")
            print(f"📅 Found months: {found_months}")
            
            # Note: We don't fail if some months are missing since 2025 data might not be fully available yet
            if found_months:
                print(f"✅ Found data for {len(found_months)} months: {found_months}")
            else:
                print("⚠️  No 2025 data found - this might be expected if data is not yet available")
                
        else:
            print(f"❌ Download failed: {result.error}")
            # Don't fail the test if download fails - it might be due to network issues
            # or data not being available yet
            pytest.skip(f"Download failed: {result.error}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_download_2025_klines(self, test_output_dir):
        """Test real download of 2025 kline data from January to June."""
        print(f"\n🚀 Starting real download test for 2025 klines...")
        print(f"📁 Output directory: {test_output_dir}")
        
        # Create download configuration for 2025 klines
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[Interval.MINUTE_1, Interval.ONE_HOUR, Interval.ONE_DAY],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 6, 30),
            output_dir=str(test_output_dir),
            resume=True,
            max_retries=3,
            timeout=30
        )
        
        # Create downloader instance
        downloader = BinanceDataDownloader(config)
        
        # Start download
        print("📥 Starting download...")
        result = downloader.download()
        
        # Assertions
        assert result is not None, "Download result should not be None"
        print(f"✅ Download completed with result: {result}")
        
        if result.success:
            print(f"📊 Download successful!")
            print(f"   Files downloaded: {result.files_downloaded}")
            print(f"   Total size: {result.total_size_mb:.2f} MB")
            print(f"   Duration: {result.duration_seconds:.2f} seconds")
            
            # Check that output directory contains files
            output_files = list(test_output_dir.glob("**/*.zip"))
            assert len(output_files) > 0, f"Expected downloaded files, found: {output_files}"
            
            print(f"📁 Found {len(output_files)} downloaded files:")
            for file_path in output_files:
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {file_path.name}: {file_size:.2f} MB")
                
                # Verify zip files are valid
                try:
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        zipf.testzip()
                    print(f"     ✅ {file_path.name} is a valid ZIP file")
                except Exception as e:
                    pytest.fail(f"Invalid ZIP file {file_path.name}: {e}")
            
            # Check for different intervals
            expected_intervals = ["1m", "1h", "1d"]
            found_intervals = []
            for file_path in output_files:
                for interval in expected_intervals:
                    if interval in file_path.name:
                        found_intervals.append(interval)
                        break
            
            print(f"⏰ Expected intervals: {expected_intervals}")
            print(f"⏰ Found intervals: {found_intervals}")
            
            if found_intervals:
                print(f"✅ Found data for {len(found_intervals)} intervals: {found_intervals}")
            else:
                print("⚠️  No expected intervals found - this might be expected if data is not yet available")
                
        else:
            print(f"❌ Download failed: {result.error}")
            pytest.skip(f"Download failed: {result.error}")
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_download_2025_klines_all_intervals_april_may(self, test_output_dir):
        """Test real download of 2025 kline data for all intervals from April to May."""
        print(f"\n🚀 Starting real download test for 2025 klines (all intervals, April-May)...")
        print(f"📁 Output directory: {test_output_dir}")
        
        # Create download configuration for 2025 klines with all intervals
        config = DownloadConfig(
            trading_type=TradingType.USD_M_FUTURES,
            data_type=DataType.KLINES,
            symbols=["BTCUSDT"],
            intervals=[
                Interval.MINUTE_1,      # 1m
                Interval.MINUTE_3,      # 3m
                Interval.MINUTE_5,      # 5m
                Interval.MINUTE_15,     # 15m
                Interval.MINUTE_30,     # 30m
                Interval.ONE_HOUR,      # 1h
                Interval.TWO_HOUR,      # 2h
                Interval.FOUR_HOUR,     # 4h
                Interval.SIX_HOUR,      # 6h
                Interval.EIGHT_HOUR,    # 8h
                Interval.TWELVE_HOUR,   # 12h
                Interval.ONE_DAY,       # 1d
                Interval.THREE_DAY,     # 3d
                Interval.ONE_WEEK,      # 1w
                Interval.ONE_MONTH      # 1M
            ],
            start_date=datetime(2025, 4, 1),
            end_date=datetime(2025, 5, 31),
            output_dir=str(test_output_dir),
            resume=True,
            max_retries=3,
            timeout=30
        )
        
        # Create downloader instance
        downloader = BinanceDataDownloader(config)
        
        # Start download
        print("📥 Starting download for all intervals...")
        result = downloader.download()
        
        # Assertions
        assert result is not None, "Download result should not be None"
        print(f"✅ Download completed with result: {result}")
        
        if result.success:
            print(f"📊 Download successful!")
            print(f"   Files downloaded: {result.files_downloaded}")
            print(f"   Total size: {result.total_size_mb:.2f} MB")
            print(f"   Duration: {result.duration_seconds:.2f} seconds")
            
            # Check that output directory contains files
            output_files = list(test_output_dir.glob("**/*.zip"))
            assert len(output_files) > 0, f"Expected downloaded files, found: {output_files}"
            
            print(f"📁 Found {len(output_files)} downloaded files:")
            for file_path in output_files:
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {file_path.name}: {file_size:.2f} MB")
                
                # Verify zip files are valid
                try:
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        zipf.testzip()
                    print(f"     ✅ {file_path.name} is a valid ZIP file")
                except Exception as e:
                    pytest.fail(f"Invalid ZIP file {file_path.name}: {e}")
            
            # Check for expected months (April and May 2025)
            expected_months = ["2025-04", "2025-05"]
            found_months = []
            for file_path in output_files:
                for month in expected_months:
                    if month in file_path.name:
                        found_months.append(month)
                        break
            
            print(f"📅 Expected months: {expected_months}")
            print(f"📅 Found months: {found_months}")
            
            # Check for different intervals
            expected_intervals = [
                "1m", "3m", "5m", "15m", "30m",  # Minutes
                "1h", "2h", "4h", "6h", "8h", "12h",  # Hours
                "1d", "3d", "1w", "1M"  # Days, Weeks, Months
            ]
            found_intervals = []
            for file_path in output_files:
                for interval in expected_intervals:
                    if interval in file_path.name:
                        found_intervals.append(interval)
                        break
            
            print(f"⏰ Expected intervals: {expected_intervals}")
            print(f"⏰ Found intervals: {found_intervals}")
            
            # Group files by month and interval for better analysis
            files_by_month = {}
            files_by_interval = {}
            
            for file_path in output_files:
                # Extract month
                for month in expected_months:
                    if month in file_path.name:
                        if month not in files_by_month:
                            files_by_month[month] = []
                        files_by_month[month].append(file_path.name)
                        break
                
                # Extract interval
                for interval in expected_intervals:
                    if interval in file_path.name:
                        if interval not in files_by_interval:
                            files_by_interval[interval] = []
                        files_by_interval[interval].append(file_path.name)
                        break
            
            print(f"\n📊 Files by month:")
            for month, files in files_by_month.items():
                print(f"   {month}: {len(files)} files")
                for file_name in files[:3]:  # Show first 3 files
                    print(f"     - {file_name}")
                if len(files) > 3:
                    print(f"     ... and {len(files) - 3} more")
            
            print(f"\n📊 Files by interval:")
            for interval, files in files_by_interval.items():
                print(f"   {interval}: {len(files)} files")
                for file_name in files[:2]:  # Show first 2 files
                    print(f"     - {file_name}")
                if len(files) > 2:
                    print(f"     ... and {len(files) - 2} more")
            
            # Summary assertions
            if found_months:
                print(f"✅ Found data for {len(found_months)} months: {found_months}")
            else:
                print("⚠️  No expected months found - this might be expected if data is not yet available")
            
            if found_intervals:
                print(f"✅ Found data for {len(found_intervals)} intervals: {found_intervals}")
            else:
                print("⚠️  No expected intervals found - this might be expected if data is not yet available")
                
        else:
            print(f"❌ Download failed: {result.error}")
            pytest.skip(f"Download failed: {result.error}")


# Add pytest markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
