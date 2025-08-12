"""Command line interface for crytata using Typer."""

import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .bn.downloader import BinanceDataDownloader
from .bn.models import (
    DownloadConfig, TradingType, DataType, Interval,
    DownloadResult
)
from .core import BinanceDataCollector, DataProcessor
from .storage import DataStorage
from .timescaledb_config import TimescaleDBConfig, TimescaleDBStorage

app = typer.Typer(
    name="crytata",
    help="Cryptocurrency data collection and processing tool for public data",
    add_completion=False
)

console = Console()


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise typer.BadParameter(f"Invalid date format: {date_str}. Use YYYY-MM-DD format.")


def parse_intervals(interval_str: str) -> List[Interval]:
    """Parse interval string into list of Interval enums."""
    intervals = []
    for interval in interval_str.split(","):
        interval = interval.strip()
        try:
            intervals.append(Interval(interval))
        except ValueError:
            raise typer.BadParameter(f"Invalid interval: {interval}")
    return intervals


@app.command()
def download(
    trading_type: TradingType = typer.Option(
        TradingType.SPOT,
        "--trading-type", "-t",
        help="Trading type (spot, um, cm)"
    ),
    data_type: DataType = typer.Option(
        DataType.KLINES,
        "--data-type", "-d",
        help="Data type to download"
    ),
    symbols: Optional[List[str]] = typer.Option(
        None,
        "--symbols", "-s",
        help="List of symbols to download (e.g., BTCUSDT ETHUSDT)"
    ),
    intervals: Optional[str] = typer.Option(
        None,
        "--intervals", "-i",
        help="Comma-separated list of intervals (e.g., 1m,1h,1d) - only for klines"
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "--start-date",
        help="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="End date in YYYY-MM-DD format"
    ),
    output_dir: str = typer.Option(
        "data",
        "--output-dir", "-o",
        help="Output directory for downloaded files"
    ),
    proxy: Optional[str] = typer.Option(
        None,
        "--proxy",
        help="HTTP proxy URL (e.g., http://proxy:port)"
    ),
    resume: bool = typer.Option(
        True,
        "--resume/--no-resume",
        help="Resume interrupted downloads"
    ),
    progress_file: str = typer.Option(
        ".download_progress.json",
        "--progress-file",
        help="Progress file path for resume functionality"
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        help="Maximum retry attempts for failed downloads"
    ),
    timeout: int = typer.Option(
        30,
        "--timeout",
        help="Request timeout in seconds"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose logging"
    )
):
    """Download Binance public data with support for proxy and resume functionality."""
    
    # Setup logging
    if verbose:
        logger.add(lambda msg: console.print(msg), level="DEBUG")
    else:
        logger.add(lambda msg: console.print(msg), level="INFO")
    
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = parse_date(start_date)
    if end_date:
        end_dt = parse_date(end_date)
    
    # Parse intervals
    interval_list = None
    if intervals and data_type == DataType.KLINES:
        interval_list = parse_intervals(intervals)
    elif intervals and data_type != DataType.KLINES:
        typer.echo(f"Warning: Intervals are only applicable for klines data type, ignoring: {intervals}")
    
    # Validate configuration
    if data_type == DataType.KLINES and not interval_list:
        typer.echo("Error: Intervals are required for klines data type")
        raise typer.Exit(1)
    
    # Create configuration
    config = DownloadConfig(
        trading_type=trading_type,
        data_type=data_type,
        symbols=symbols or [],
        intervals=interval_list,
        start_date=start_dt,
        end_date=end_dt,
        output_dir=output_dir,
        proxy=proxy,
        resume=resume,
        progress_file=progress_file,
        max_retries=max_retries,
        timeout=timeout
    )
    
    # Display configuration
    console.print("\n[bold blue]Download Configuration:[/bold blue]")
    table = Table(show_header=False)
    table.add_row("Trading Type", trading_type.value)
    table.add_row("Data Type", data_type.value)
    table.add_row("Symbols", ", ".join(symbols) if symbols else "All available")
    if interval_list:
        table.add_row("Intervals", ", ".join(i.value for i in interval_list))
    table.add_row("Date Range", f"{start_date or 'Current year'} to {end_date or 'Current year'}")
    table.add_row("Output Directory", output_dir)
    if proxy:
        table.add_row("Proxy", proxy)
    table.add_row("Resume", str(resume))
    table.add_row("Max Retries", str(max_retries))
    table.add_row("Timeout", f"{timeout}s")
    
    console.print(table)
    
    # Confirm download
    if not typer.confirm("\nProceed with download?"):
        typer.echo("Download cancelled.")
        raise typer.Exit()
    
    # Initialize downloader
    try:
        downloader = BinanceDataDownloader(config)
    except Exception as e:
        typer.echo(f"Error initializing downloader: {e}")
        raise typer.Exit(1)
    
    # Execute download
    console.print("\n[bold green]Starting download...[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Downloading files...", total=None)
        
        try:
            result = downloader.download()
            progress.update(task, completed=True)
        except KeyboardInterrupt:
            console.print("\n[yellow]Download interrupted by user[/yellow]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"\n[red]Download failed: {e}[/red]")
            raise typer.Exit(1)
    
    # Display results
    console.print("\n[bold green]Download Results:[/bold green]")
    result_table = Table(show_header=False)
    result_table.add_row("Success", "✅ Yes" if result.success else "❌ No")
    result_table.add_row("Files Downloaded", str(result.files_downloaded))
    result_table.add_row("Total Size", f"{result.total_size:,} bytes")
    if result.duration:
        result_table.add_row("Duration", f"{result.duration:.2f} seconds")
    result_table.add_row("Output Directory", result.output_dir)
    
    if result.errors:
        result_table.add_row("Errors", f"{len(result.errors)} errors occurred")
        for error in result.errors[:5]:  # Show first 5 errors
            result_table.add_row("", f"  • {error}")
        if len(result.errors) > 5:
            result_table.add_row("", f"  ... and {len(result.errors) - 5} more errors")
    
    console.print(result_table)
    
    if result.success:
        console.print(f"\n[green]Download completed successfully![/green]")
        console.print(f"Files saved to: [blue]{result.output_dir}[/blue]")
    else:
        console.print(f"\n[yellow]Download completed with errors.[/yellow]")
        console.print(f"Check the error log above for details.")


if __name__ == "__main__":
    app()