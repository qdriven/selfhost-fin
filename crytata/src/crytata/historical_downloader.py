"""Historical data downloader for Binance public data."""

import os
import sys
import zipfile
import urllib.request
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import pandas as pd
from loguru import logger

from .models import KlineData, TradeData
from .storage import DataStorage


class BinanceHistoricalDownloader:
    """Download historical data from Binance public data repository."""

    # Constants from binance-public-data
    YEARS = ['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
    INTERVALS = ["1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1mo"]
    DAILY_INTERVALS = ["1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
    TRADING_TYPE = ["spot", "um", "cm"]
    MONTHS = list(range(1, 13))
    BASE_URL = 'https://data.binance.vision/'

    def __init__(self, download_dir: str = "downloads"):
        """Initialize the historical downloader.
        
        Args:
            download_dir: Directory to store downloaded files
        """
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"Historical downloader initialized with download directory: {download_dir}")

    def get_all_symbols(self, trading_type: str = 'spot') -> List[str]:
        """Get all available symbols from Binance.
        
        Args:
            trading_type: Trading type ('spot', 'um', 'cm')
            
        Returns:
            List of symbol names
        """
        try:
            if trading_type == 'um':
                url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
            elif trading_type == 'cm':
                url = "https://dapi.binance.com/dapi/v1/exchangeInfo"
            else:
                url = "https://api.binance.com/api/v3/exchangeInfo"

            response = urllib.request.urlopen(url).read()
            data = pd.read_json(response)
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            logger.info(f"Retrieved {len(symbols)} symbols for {trading_type}")
            return symbols

        except Exception as e:
            logger.error(f"Error retrieving symbols: {e}")
            return []

    def get_path(self, trading_type: str, market_data_type: str, time_period: str,
                 symbol: str, interval: Optional[str] = None) -> str:
        """Generate download path for Binance data.
        
        Args:
            trading_type: Trading type ('spot', 'um', 'cm')
            market_data_type: Data type ('klines', 'trades', etc.)
            time_period: Time period ('daily', 'monthly')
            symbol: Symbol name
            interval: Kline interval (for klines data)
            
        Returns:
            Download path
        """
        trading_type_path = 'data/spot'
        if trading_type != 'spot':
            trading_type_path = f'data/futures/{trading_type}'

        if interval is not None:
            path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/{interval}/'
        else:
            path = f'{trading_type_path}/{time_period}/{market_data_type}/{symbol.upper()}/'

        return path

    def download_file(self, base_path: str, file_name: str, date_range: Optional[str] = None) -> Optional[str]:
        """Download a file from Binance public data.
        
        Args:
            base_path: Base path for the file
            file_name: File name to download
            date_range: Optional date range for organization
            
        Returns:
            Path to downloaded file or None if failed
        """
        download_path = f"{base_path}{file_name}"
        download_url = f"{self.BASE_URL}{download_path}"

        # Create save path
        if date_range:
            date_range = date_range.replace(" ", "_")
            base_path = os.path.join(base_path, date_range)

        save_path = os.path.join(self.download_dir, base_path, file_name)

        # Check if file already exists
        if os.path.exists(save_path):
            logger.info(f"File already exists: {save_path}")
            return save_path

        # Create directory
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            logger.info(f"Downloading: {download_url}")
            dl_file = urllib.request.urlopen(download_url)
            length = dl_file.getheader('content-length')

            if length:
                length = int(length)
                blocksize = max(4096, length // 100)
            else:
                blocksize = 4096

            with open(save_path, 'wb') as out_file:
                dl_progress = 0
                while True:
                    buf = dl_file.read(blocksize)
                    if not buf:
                        break
                    dl_progress += len(buf)
                    out_file.write(buf)

                    if length:
                        done = int(50 * dl_progress / length)
                        sys.stdout.write(f"\r[{'#' * done}{'.' * (50 - done)}]")
                        sys.stdout.flush()

            logger.info(f"Downloaded: {save_path}")
            return save_path

        except urllib.error.HTTPError as e:
            logger.error(f"File not found: {download_url} - {e}")
            return None
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def extract_zip_file(self, zip_path: str) -> Optional[str]:
        """Extract a zip file and return the path to the extracted CSV.
        
        Args:
            zip_path: Path to the zip file
            
        Returns:
            Path to extracted CSV file or None if failed
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get the CSV file name (should be the only file in the zip)
                csv_filename = zip_ref.namelist()[0]
                extract_dir = os.path.dirname(zip_path)
                zip_ref.extract(csv_filename, extract_dir)

                csv_path = os.path.join(extract_dir, csv_filename)
                logger.info(f"Extracted: {csv_path}")
                return csv_path

        except Exception as e:
            logger.error(f"Error extracting zip file {zip_path}: {e}")
            return None

    def download_monthly_klines(self, trading_type: str, symbols: List[str],
                                intervals: List[str], years: List[str],
                                months: List[int], start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> List[str]:
        """Download monthly kline data.
        
        Args:
            trading_type: Trading type ('spot', 'um', 'cm')
            symbols: List of symbols to download
            intervals: List of intervals to download
            years: List of years to download
            months: List of months to download
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        # Convert dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

        logger.info(f"Downloading monthly klines for {len(symbols)} symbols")

        for i, symbol in enumerate(symbols):
            logger.info(f"[{i + 1}/{len(symbols)}] Downloading monthly klines for {symbol}")

            for interval in intervals:
                for year in years:
                    for month in months:
                        current_date = date(int(year), month, 1)

                        if start_dt and current_date < start_dt:
                            continue
                        if end_dt and current_date > end_dt:
                            continue

                        path = self.get_path(trading_type, "klines", "monthly", symbol, interval)
                        file_name = f"{symbol.upper()}-{interval}-{year}-{month:02d}.zip"

                        file_path = self.download_file(path, file_name)
                        if file_path:
                            downloaded_files.append(file_path)

        logger.info(f"Downloaded {len(downloaded_files)} monthly kline files")
        return downloaded_files

    def download_daily_klines(self, trading_type: str, symbols: List[str],
                              intervals: List[str], dates: List[str],
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> List[str]:
        """Download daily kline data.
        
        Args:
            trading_type: Trading type ('spot', 'um', 'cm')
            symbols: List of symbols to download
            intervals: List of intervals to download
            dates: List of dates to download
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        # Filter intervals for daily data
        intervals = list(set(intervals) & set(self.DAILY_INTERVALS))

        # Convert dates
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

        logger.info(f"Downloading daily klines for {len(symbols)} symbols")

        for i, symbol in enumerate(symbols):
            logger.info(f"[{i + 1}/{len(symbols)}] Downloading daily klines for {symbol}")

            for interval in intervals:
                for date_str in dates:
                    current_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    if start_dt and current_date < start_dt:
                        continue
                    if end_dt and current_date > end_dt:
                        continue

                    path = self.get_path(trading_type, "klines", "daily", symbol, interval)
                    file_name = f"{symbol.upper()}-{interval}-{date_str}.zip"

                    file_path = self.download_file(path, file_name)
                    if file_path:
                        downloaded_files.append(file_path)

        logger.info(f"Downloaded {len(downloaded_files)} daily kline files")
        return downloaded_files

    def process_klines_csv(self, csv_path: str, symbol: str, interval: str) -> List[KlineData]:
        """Process klines CSV file and convert to KlineData objects.
        
        Args:
            csv_path: Path to CSV file
            symbol: Symbol name
            interval: Kline interval
            
        Returns:
            List of KlineData objects
        """
        try:
            # First, read the raw CSV to preserve header if it exists
            df_raw = pd.read_csv(csv_path)
            
            # Check if the first row contains header information
            # If the first column is numeric (timestamp), then there's no header
            # If the first column contains text, then there's a header
            has_header = False
            if len(df_raw.columns) > 0:
                first_col = df_raw.columns[0]
                if isinstance(first_col, str) and not first_col.replace('.', '').replace('-', '').isdigit():
                    has_header = True
            
            # Read the CSV with appropriate header setting
            if has_header:
                df = pd.read_csv(csv_path)
                logger.info(f"CSV file {csv_path} contains header: {list(df.columns)}")
            else:
                df = pd.read_csv(csv_path, header=None)
                logger.info(f"CSV file {csv_path} has no header, using default column names")

            # Binance CSV format: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
            klines = []
            for _, row in df.iterrows():
                kline = KlineData(
                    symbol=symbol,
                    open_time=datetime.fromtimestamp(row[0] / 1000),
                    close_time=datetime.fromtimestamp(row[6] / 1000),
                    open_price=float(row[1]),
                    high_price=float(row[2]),
                    low_price=float(row[3]),
                    close_price=float(row[4]),
                    volume=float(row[5]),
                    quote_volume=float(row[7]),
                    trade_count=int(row[8]),
                    taker_buy_volume=float(row[9]),
                    taker_buy_quote_volume=float(row[10]),
                    interval=interval
                )
                klines.append(kline)

            logger.info(f"Processed {len(klines)} klines from {csv_path}")
            return klines

        except Exception as e:
            logger.error(f"Error processing CSV file {csv_path}: {e}")
            return []

    def download_and_process_klines(self, trading_type: str = 'spot',
                                    symbols: Optional[List[str]] = None,
                                    intervals: Optional[List[str]] = None,
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None,
                                    storage: Optional[DataStorage] = None) -> Dict[str, List[KlineData]]:
        """Download and process kline data.
        
        Args:
            trading_type: Trading type ('spot', 'um', 'cm')
            symbols: List of symbols to download (None for all)
            intervals: List of intervals to download (None for all)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            storage: DataStorage instance for saving data
            
        Returns:
            Dictionary mapping symbol to list of KlineData objects
        """
        if symbols is None:
            symbols = self.get_all_symbols(trading_type)

        if intervals is None:
            intervals = self.INTERVALS

        # Generate date range
        if not start_date:
            start_date = '2020-01-01'
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Download files
        downloaded_files = []

        # Download monthly files
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        years = [str(year) for year in range(start_dt.year, end_dt.year + 1)]
        months = list(range(1, 13))

        monthly_files = self.download_monthly_klines(
            trading_type, symbols, intervals, years, months, start_date, end_date
        )
        downloaded_files.extend(monthly_files)

        # Download daily files
        dates = pd.date_range(start=start_date, end=end_date, freq='D').strftime('%Y-%m-%d').tolist()
        daily_files = self.download_daily_klines(
            trading_type, symbols, intervals, dates, start_date, end_date
        )
        downloaded_files.extend(daily_files)

        # Process files
        all_klines = {}

        for file_path in downloaded_files:
            if file_path.endswith('.zip'):
                csv_path = self.extract_zip_file(file_path)
                if csv_path:
                    # Extract symbol and interval from filename
                    filename = os.path.basename(file_path)
                    parts = filename.replace('.zip', '').split('-')
                    if len(parts) >= 3:
                        symbol = parts[0]
                        interval = parts[1]

                        klines = self.process_klines_csv(csv_path, symbol, interval)

                        if symbol not in all_klines:
                            all_klines[symbol] = []
                        all_klines[symbol].extend(klines)

                        # Save to storage if provided
                        if storage:
                            storage.save_klines_csv(klines)
                            storage.save_klines_db(klines)

        logger.info(f"Processed klines for {len(all_klines)} symbols")
        return all_klines
