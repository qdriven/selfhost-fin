"""Core downloader for Binance public data."""

import os
import json
import time
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional, Dict, Any, Generator
import requests
from urllib.parse import urlparse
import zipfile
import pandas as pd
from loguru import logger

from .models import (
    DownloadConfig, DownloadProgress, DownloadResult,
    TradingType, DataType, Interval
)


class BinanceDataDownloader:
    """Downloader for Binance public data with proxy support and resume capability."""

    BASE_URL = "https://data.binance.vision/"
    
    def __init__(self, config: DownloadConfig):
        """Initialize the downloader with configuration.
        
        Args:
            config: Download configuration
        """
        self.config = config
        self.progress = self._load_progress()
        self.session = self._setup_session()
        
        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        logger.info(f"Downloader initialized for {config.trading_type.value} {config.data_type.value}")

    def _setup_session(self) -> requests.Session:
        """Setup requests session with proxy if configured."""
        session = requests.Session()
        
        if self.config.proxy:
            session.proxies.update({
                'http': self.config.proxy,
                'https': self.config.proxy
            })
            logger.info(f"Proxy configured: {self.config.proxy}")
        
        # Set timeout
        session.timeout = self.config.timeout
        
        return session

    def _load_progress(self) -> DownloadProgress:
        """Load download progress from file."""
        if not self.config.resume or not os.path.exists(self.config.progress_file):
            config_hash = self._generate_config_hash()
            return DownloadProgress(config_id=config_hash)
        
        try:
            with open(self.config.progress_file, 'r') as f:
                data = json.load(f)
                return DownloadProgress(**data)
        except Exception as e:
            logger.warning(f"Failed to load progress file: {e}")
            config_hash = self._generate_config_hash()
            return DownloadProgress(config_id=config_hash)

    def _save_progress(self):
        """Save download progress to file."""
        if not self.config.resume:
            return
        
        try:
            self.progress.last_update = datetime.now()
            with open(self.config.progress_file, 'w') as f:
                json.dump(self.progress.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save progress: {e}")

    def _generate_config_hash(self) -> str:
        """Generate a hash for the current configuration."""
        config_str = f"{self.config.trading_type.value}_{self.config.data_type.value}_{self.config.symbols}_{self.config.intervals}_{self.config.start_date}_{self.config.end_date}"
        return hashlib.md5(config_str.encode()).hexdigest()[:8]

    def _get_download_urls(self) -> Generator[str, None, None]:
        """Generate download URLs based on configuration."""
        if not self.config.symbols:
            # Get all symbols if none specified
            symbols = self._get_all_symbols()
        else:
            symbols = self.config.symbols

        # Determine date range
        if self.config.start_date and self.config.end_date:
            start_date = self.config.start_date
            end_date = self.config.end_date
        else:
            # Default to current year
            current_year = datetime.now().year
            start_date = datetime(current_year, 1, 1)
            end_date = datetime(current_year, 12, 31)

        # Generate monthly URLs
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            
            for symbol in symbols:
                if self.config.data_type == DataType.KLINES and self.config.intervals:
                    for interval in self.config.intervals:
                        url = self._build_monthly_url(symbol, interval, year, month)
                        yield url
                else:
                    url = self._build_monthly_url(symbol, None, year, month)
                    yield url
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    def _build_monthly_url(self, symbol: str, interval: Optional[Interval], year: int, month: int) -> str:
        """Build monthly download URL."""
        if self.config.trading_type == TradingType.SPOT:
            base_path = f"data/spot/monthly/{self.config.data_type.value}/{symbol}"
        else:
            base_path = f"data/futures/{self.config.trading_type.value}/monthly/{self.config.data_type.value}/{symbol}"

        if interval:
            base_path += f"/{interval.value}"
            filename = f"{symbol}-{interval.value}-{year}-{month:02d}.zip"
        else:
            if self.config.data_type == DataType.TRADES:
                filename = f"{symbol}-trades-{year}-{month:02d}.zip"
            else:
                filename = f"{symbol}-{self.config.data_type.value}-{year}-{month:02d}.zip"

        return f"{self.BASE_URL}{base_path}/{filename}"

    def _get_all_symbols(self) -> List[str]:
        """Get all available symbols for the trading type."""
        try:
            if self.config.trading_type == TradingType.USD_M_FUTURES:
                url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
            elif self.config.trading_type == TradingType.COIN_M_FUTURES:
                url = "https://dapi.binance.com/dapi/v1/exchangeInfo"
            else:
                url = "https://api.binance.com/api/v3/exchangeInfo"

            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            logger.info(f"Retrieved {len(symbols)} symbols for {self.config.trading_type.value}")
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols: {e}")
            return []

    def _download_file(self, url: str, retries: int = 0) -> Optional[str]:
        """Download a single file with retry logic and resume support."""
        try:
            # Parse URL to get filename
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # Create output path
            output_path = os.path.join(self.config.output_dir, filename)
            temp_path = output_path + ".part"
            
            # Determine resume position
            resume_bytes = 0
            if os.path.exists(temp_path):
                resume_bytes = os.path.getsize(temp_path)
                logger.info(f"Resuming download from {resume_bytes} bytes for {filename}")
            elif os.path.exists(output_path) and not self._is_file_complete(output_path):
                # Move incomplete final file to temp for resume
                os.replace(output_path, temp_path)
                resume_bytes = os.path.getsize(temp_path)
                logger.info(f"Resuming (moved) download from {resume_bytes} bytes for {filename}")
            elif os.path.exists(output_path) and self._is_file_complete(output_path):
                logger.info(f"File already exists and complete: {filename}")
                return output_path
            
            # Prepare headers for range request
            headers = {}
            if self.config.resume and resume_bytes > 0:
                headers["Range"] = f"bytes={resume_bytes}-"
            
            # Start download
            logger.info(f"Downloading: {url}")
            self.progress.current_file = filename
            self._save_progress()
            
            with self.session.get(url, headers=headers, stream=True, timeout=self.config.timeout) as response:
                if response.status_code == 404:
                    logger.warning(f"File not found: {url}")
                    return None
                response.raise_for_status()
                total_size = int(response.headers.get('Content-Length', 0))
                mode = 'ab' if resume_bytes > 0 else 'wb'
                downloaded = resume_bytes
                
                with open(temp_path if self.config.resume else output_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded - resume_bytes) / total_size * 100
                            logger.debug(f"Download progress: {progress:.1f}%")
            
            # Finalize file
            if self.config.resume:
                os.replace(temp_path, output_path)
            logger.info(f"Downloaded: {filename}")
            return output_path
            
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                logger.warning(f"File not found: {url}")
                return None
            else:
                logger.error(f"HTTP error downloading {url}: {e}")
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
        
        # Retry logic
        if retries < self.config.max_retries:
            logger.info(f"Retrying download of {url} (attempt {retries + 1}/{self.config.max_retries})")
            time.sleep(2 ** retries)  # Exponential backoff
            return self._download_file(url, retries + 1)
        
        return None

    def _is_file_complete(self, file_path: str) -> bool:
        """Check if a downloaded file is complete."""
        try:
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Check if zip file is valid
                    zip_file.testzip()
                    return True
            else:
                # For non-zip files, just check if they exist and have size > 0
                return os.path.getsize(file_path) > 0
        except Exception:
            return False

    def download(self) -> DownloadResult:
        """Execute the download operation."""
        start_time = time.time()
        self.progress.start_time = datetime.now()
        self.progress.status = "downloading"
        
        # Get all URLs to download
        urls = list(self._get_download_urls())
        self.progress.total_files = len(urls)
        logger.info(f"Starting download of {len(urls)} files")
        
        downloaded_files = []
        failed_files = []
        
        for i, url in enumerate(urls):
            try:
                result = self._download_file(url)
                if result:
                    downloaded_files.append(result)
                    self.progress.completed_files += 1
                else:
                    failed_files.append(url)
                    self.progress.failed_files += 1
                
                # Update progress
                self._save_progress()
                
                # Progress update
                if (i + 1) % 10 == 0 or i + 1 == len(urls):
                    logger.info(f"Progress: {i + 1}/{len(urls)} files processed")
                
            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
                failed_files.append(url)
                self.progress.failed_files += 1
                self.progress.errors.append(f"{url}: {str(e)}")
        
        # Calculate total size
        total_size = sum(os.path.getsize(f) for f in downloaded_files if os.path.exists(f))
        
        # Update final status
        duration = time.time() - start_time
        self.progress.status = "completed" if failed_files else "completed"
        self.progress.last_update = datetime.now()
        self._save_progress()
        
        # Clean up progress file if successful
        if not failed_files and os.path.exists(self.config.progress_file):
            os.remove(self.config.progress_file)
        
        result = DownloadResult(
            success=len(failed_files) == 0,
            files_downloaded=len(downloaded_files),
            total_size=total_size,
            duration=duration,
            errors=self.progress.errors,
            output_dir=self.config.output_dir
        )
        
        logger.info(f"Download completed: {result.files_downloaded} files, {result.total_size} bytes, {duration:.2f}s")
        return result
