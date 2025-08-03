"""Command line interface for crytata."""

import os
from datetime import datetime, timedelta
from typing import Optional
import click
from loguru import logger
import pandas as pd

from .core import BinanceDataCollector, DataProcessor
from .storage import DataStorage
from .historical_downloader import BinanceHistoricalDownloader
from .timescaledb_config import TimescaleDBConfig, TimescaleDBStorage


@click.group()
@click.option('--log-level', default='INFO', help='Log level')
def cli(log_level):
    """Cryptocurrency data collection and processing tool."""
    logger.remove()
    logger.add(lambda msg: click.echo(msg, err=True), level=log_level)


@cli.command()
@click.option('--symbol', required=True, help='Trading pair symbol (e.g., BTCUSDT)')
@click.option('--interval', default='1h', help='Kline interval (1m, 5m, 1h, 1d, etc.)')
@click.option('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS)')
@click.option('--end-time', help='End time (YYYY-MM-DD HH:MM:SS)')
@click.option('--limit', default=1000, help='Number of klines to retrieve')
@click.option('--output', default='data', help='Output directory for CSV files')
@click.option('--db-url', help='Database URL (optional)')
@click.option('--save-csv/--no-save-csv', default=True, help='Save to CSV file')
@click.option('--save-db/--no-save-db', default=False, help='Save to database')
def collect_klines(symbol, interval, start_time, end_time, limit, output, db_url, save_csv, save_db):
    """Collect kline/candlestick data."""
    # Parse datetime strings
    start_dt = None
    end_dt = None
    
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            click.echo(f"Invalid start_time format: {start_time}. Use YYYY-MM-DD HH:MM:SS", err=True)
            return
    
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            click.echo(f"Invalid end_time format: {end_time}. Use YYYY-MM-DD HH:MM:SS", err=True)
            return
    
    # Initialize components
    collector = BinanceDataCollector()
    storage = DataStorage(csv_dir=output, db_url=db_url)
    
    # Collect data
    click.echo(f"Collecting {interval} klines for {symbol}...")
    klines = collector.get_klines(symbol, interval, start_dt, end_dt, limit)
    
    if not klines:
        click.echo("No data collected.", err=True)
        return
    
    click.echo(f"Collected {len(klines)} klines")
    
    # Save data
    if save_csv:
        csv_file = storage.save_klines_csv(klines)
        click.echo(f"Saved to CSV: {csv_file}")
    
    if save_db:
        if storage.save_klines_db(klines):
            click.echo("Saved to database")
        else:
            click.echo("Failed to save to database", err=True)


@cli.command()
@click.option('--symbol', required=True, help='Trading pair symbol (e.g., BTCUSDT)')
@click.option('--limit', default=1000, help='Number of trades to retrieve')
@click.option('--output', default='data', help='Output directory for CSV files')
@click.option('--db-url', help='Database URL (optional)')
@click.option('--save-csv/--no-save-csv', default=True, help='Save to CSV file')
@click.option('--save-db/--no-save-db', default=False, help='Save to database')
def collect_trades(symbol, limit, output, db_url, save_csv, save_db):
    """Collect recent trades."""
    # Initialize components
    collector = BinanceDataCollector()
    storage = DataStorage(csv_dir=output, db_url=db_url)
    
    # Collect data
    click.echo(f"Collecting recent trades for {symbol}...")
    trades = collector.get_recent_trades(symbol, limit)
    
    if not trades:
        click.echo("No data collected.", err=True)
        return
    
    click.echo(f"Collected {len(trades)} trades")
    
    # Save data
    if save_csv:
        csv_file = storage.save_trades_csv(trades)
        click.echo(f"Saved to CSV: {csv_file}")
    
    if save_db:
        if storage.save_trades_db(trades):
            click.echo("Saved to database")
        else:
            click.echo("Failed to save to database", err=True)


@cli.command()
@click.option('--symbol', help='Trading pair symbol (e.g., BTCUSDT). If not provided, gets all symbols.')
@click.option('--output', default='data', help='Output directory for CSV files')
@click.option('--db-url', help='Database URL (optional)')
@click.option('--save-csv/--no-save-csv', default=True, help='Save to CSV file')
@click.option('--save-db/--no-save-db', default=False, help='Save to database')
def collect_tickers(symbol, output, db_url, save_csv, save_db):
    """Collect 24hr ticker data."""
    # Initialize components
    collector = BinanceDataCollector()
    storage = DataStorage(csv_dir=output, db_url=db_url)
    
    if symbol:
        # Collect single symbol ticker
        click.echo(f"Collecting ticker for {symbol}...")
        ticker = collector.get_24hr_ticker(symbol)
        
        if not ticker:
            click.echo("No data collected.", err=True)
            return
        
        tickers = [ticker]
        click.echo(f"Collected ticker for {symbol}")
    else:
        # Collect all tickers
        click.echo("Collecting all tickers...")
        tickers = collector.get_all_tickers()
        
        if not tickers:
            click.echo("No data collected.", err=True)
            return
        
        click.echo(f"Collected {len(tickers)} tickers")
    
    # Save data
    if save_csv:
        csv_file = storage.save_tickers_csv(tickers)
        click.echo(f"Saved to CSV: {csv_file}")
    
    if save_db:
        if storage.save_tickers_db(tickers):
            click.echo("Saved to database")
        else:
            click.echo("Failed to save to database", err=True)


@cli.command()
@click.option('--symbol', required=True, help='Trading pair symbol (e.g., BTCUSDT)')
@click.option('--interval', default='1h', help='Kline interval')
@click.option('--days', default=7, help='Number of days to collect')
@click.option('--output', default='data', help='Output directory for CSV files')
@click.option('--db-url', help='Database URL (optional)')
@click.option('--save-csv/--no-save-csv', default=True, help='Save to CSV file')
@click.option('--save-db/--no-save-db', default=False, help='Save to database')
def collect_historical(symbol, interval, days, output, db_url, save_csv, save_db):
    """Collect historical data for the specified number of days."""
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    click.echo(f"Collecting {days} days of {interval} data for {symbol}...")
    click.echo(f"Time range: {start_time} to {end_time}")
    
    # Initialize components
    collector = BinanceDataCollector()
    storage = DataStorage(csv_dir=output, db_url=db_url)
    
    all_klines = []
    current_start = start_time
    
    # Collect data in chunks (max 1000 klines per request)
    while current_start < end_time:
        current_end = min(current_start + timedelta(days=days//10), end_time)
        
        klines = collector.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=current_start,
            end_time=current_end,
            limit=1000
        )
        
        if klines:
            all_klines.extend(klines)
            click.echo(f"Collected {len(klines)} klines from {current_start} to {current_end}")
        
        current_start = current_end
    
    if not all_klines:
        click.echo("No data collected.", err=True)
        return
    
    click.echo(f"Total collected: {len(all_klines)} klines")
    
    # Save data
    if save_csv:
        csv_file = storage.save_klines_csv(all_klines)
        click.echo(f"Saved to CSV: {csv_file}")
    
    if save_db:
        if storage.save_klines_db(all_klines):
            click.echo("Saved to database")
        else:
            click.echo("Failed to save to database", err=True)


@cli.command()
@click.option('--csv-file', required=True, help='Path to CSV file')
@click.option('--output', default='data', help='Output directory for processed files')
def process_csv(csv_file, output):
    """Process CSV file and add technical indicators."""
    if not os.path.exists(csv_file):
        click.echo(f"File not found: {csv_file}", err=True)
        return
    
    try:
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Check if it's kline data
        if 'open_price' in df.columns and 'close_price' in df.columns:
            # Set index to open_time if available
            if 'open_time' in df.columns:
                df['open_time'] = pd.to_datetime(df['open_time'])
                df.set_index('open_time', inplace=True)
            
            # Calculate technical indicators
            df = DataProcessor.calculate_technical_indicators(df)
            
            # Save processed data
            output_file = os.path.join(output, f"processed_{os.path.basename(csv_file)}")
            df.to_csv(output_file)
            click.echo(f"Processed data saved to: {output_file}")
        else:
            click.echo("CSV file does not appear to contain OHLCV data", err=True)
    
    except Exception as e:
        click.echo(f"Error processing CSV: {e}", err=True)


@cli.group()
def historical():
    """Historical data download commands."""
    pass


@historical.command()
@click.option('--trading-type', default='spot', type=click.Choice(['spot', 'um', 'cm']), help='Trading type')
@click.option('--symbols', help='Comma-separated list of symbols (e.g., BTCUSDT,ETHUSDT)')
@click.option('--intervals', default='1h,1d', help='Comma-separated list of intervals')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--download-dir', default='downloads', help='Download directory')
@click.option('--output', default='data', help='Output directory for processed CSV files')
@click.option('--save-csv/--no-save-csv', default=True, help='Save processed data to CSV')
@click.option('--save-timescaledb/--no-save-timescaledb', default=False, help='Save to TimescaleDB')
@click.option('--timescaledb-host', default='localhost', help='TimescaleDB host')
@click.option('--timescaledb-port', default=5432, help='TimescaleDB port')
@click.option('--timescaledb-database', default='crytata', help='TimescaleDB database name')
@click.option('--timescaledb-username', default='crytata', help='TimescaleDB username')
@click.option('--timescaledb-password', default='crytata_password', help='TimescaleDB password')
def download_klines(trading_type, symbols, intervals, start_date, end_date, download_dir, 
                   output, save_csv, save_timescaledb, timescaledb_host, timescaledb_port,
                   timescaledb_database, timescaledb_username, timescaledb_password):
    """Download historical kline data from Binance public data repository."""
    
    # Parse symbols
    symbol_list = None
    if symbols:
        symbol_list = [s.strip() for s in symbols.split(',')]
    
    # Parse intervals
    interval_list = [i.strip() for i in intervals.split(',')]
    
    click.echo(f"Downloading historical klines for {trading_type} trading")
    if symbol_list:
        click.echo(f"Symbols: {', '.join(symbol_list)}")
    else:
        click.echo("All symbols")
    click.echo(f"Intervals: {', '.join(interval_list)}")
    click.echo(f"Date range: {start_date or '2020-01-01'} to {end_date or 'today'}")
    
    # Initialize components
    downloader = BinanceHistoricalDownloader(download_dir=download_dir)
    
    # Initialize storage
    storage = None
    if save_csv or save_timescaledb:
        storage = DataStorage(csv_dir=output)
    
    # Initialize TimescaleDB if needed
    timescaledb_storage = None
    if save_timescaledb:
        config = TimescaleDBConfig(
            host=timescaledb_host,
            port=timescaledb_port,
            database=timescaledb_database,
            username=timescaledb_username,
            password=timescaledb_password
        )
        timescaledb_storage = TimescaleDBStorage(config)
        
        if not timescaledb_storage.connected:
            click.echo("Failed to connect to TimescaleDB", err=True)
            return
    
    # Download and process data
    all_klines = downloader.download_and_process_klines(
        trading_type=trading_type,
        symbols=symbol_list,
        intervals=interval_list,
        start_date=start_date,
        end_date=end_date,
        storage=storage
    )
    
    # Save to TimescaleDB if requested
    if save_timescaledb and timescaledb_storage:
        total_klines = 0
        for symbol, klines in all_klines.items():
            if timescaledb_storage.save_klines(klines):
                total_klines += len(klines)
                click.echo(f"Saved {len(klines)} klines for {symbol} to TimescaleDB")
            else:
                click.echo(f"Failed to save klines for {symbol} to TimescaleDB", err=True)
        
        click.echo(f"Total klines saved to TimescaleDB: {total_klines}")
    
    click.echo("Historical data download completed")


@cli.group()
def timescaledb():
    """TimescaleDB management commands."""
    pass


@timescaledb.command()
@click.option('--host', default='localhost', help='TimescaleDB host')
@click.option('--port', default=5432, help='TimescaleDB port')
@click.option('--database', default='crytata', help='Database name')
@click.option('--username', default='crytata', help='Username')
@click.option('--password', default='crytata_password', help='Password')
def init(host, port, database, username, password):
    """Initialize TimescaleDB database and tables."""
    click.echo(f"Initializing TimescaleDB at {host}:{port}/{database}")
    
    config = TimescaleDBConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    if config.connect():
        if config.create_tables():
            click.echo("TimescaleDB initialized successfully")
        else:
            click.echo("Failed to create tables", err=True)
    else:
        click.echo("Failed to connect to TimescaleDB", err=True)


@timescaledb.command()
@click.option('--symbol', required=True, help='Symbol to query')
@click.option('--interval', required=True, help='Interval to query')
@click.option('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS)')
@click.option('--end-time', help='End time (YYYY-MM-DD HH:MM:SS)')
@click.option('--limit', default=100, help='Maximum number of records')
@click.option('--host', default='localhost', help='TimescaleDB host')
@click.option('--port', default=5432, help='TimescaleDB port')
@click.option('--database', default='crytata', help='Database name')
@click.option('--username', default='crytata', help='Username')
@click.option('--password', default='crytata_password', help='Password')
def query(symbol, interval, start_time, end_time, limit, host, port, database, username, password):
    """Query data from TimescaleDB."""
    config = TimescaleDBConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    storage = TimescaleDBStorage(config)
    
    if not storage.connected:
        click.echo("Failed to connect to TimescaleDB", err=True)
        return
    
    # Parse datetime strings
    start_dt = None
    end_dt = None
    
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            click.echo(f"Invalid start_time format: {start_time}", err=True)
            return
    
    if end_time:
        try:
            end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            click.echo(f"Invalid end_time format: {end_time}", err=True)
            return
    
    klines = storage.query_klines(symbol, interval, start_dt, end_dt, limit)
    
    if klines:
        click.echo(f"Found {len(klines)} klines for {symbol} {interval}")
        for kline in klines[:5]:  # Show first 5
            click.echo(f"  {kline.open_time}: O={kline.open_price}, H={kline.high_price}, L={kline.low_price}, C={kline.close_price}, V={kline.volume}")
        if len(klines) > 5:
            click.echo(f"  ... and {len(klines) - 5} more")
    else:
        click.echo("No data found")


if __name__ == '__main__':
    cli() 