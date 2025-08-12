"""Command line interface for Binance data downloader using Typer."""

import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .downloader import BinanceDataDownloader
from .models import (
    DownloadConfig, TradingType, DataType, Interval,
    DownloadResult
)

app = typer.Typer(
    name="bn",
    help="Binance public data downloader with proxy support and resume capability",
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


@app.command()
def batch_download(
    config_file: str = typer.Option(
        None,
        "--config-file", "-c",
        help="Path to configuration file (JSON format)"
    ),
    trading_type: TradingType = typer.Option(
        TradingType.SPOT,
        "--trading-type", "-t",
        help="Trading type for all downloads"
    ),
    symbols: Optional[List[str]] = typer.Option(
        None,
        "--symbols", "-s",
        help="List of symbols to download"
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
        help="Base output directory"
    ),
    proxy: Optional[str] = typer.Option(
        None,
        "--proxy",
        help="HTTP proxy URL"
    )
):
    """Download multiple data types in batch."""
    
    if config_file and os.path.exists(config_file):
        # Load from config file
        try:
            import json
            with open(config_file, 'r') as f:
                configs = json.load(f)
        except Exception as e:
            typer.echo(f"Error loading config file: {e}")
            raise typer.Exit(1)
    else:
        # Use command line arguments
        if not symbols:
            typer.echo("Error: Symbols are required for batch download")
            raise typer.Exit(1)
        
        # Define default data types to download
        configs = [
            {"data_type": "klines", "intervals": "1m,3m,5m,15m,1h,4h,1d"},
            {"data_type": "trades"},
            {"data_type": "aggTrades"}
        ]
        
        # Add futures-specific data types
        if trading_type != TradingType.SPOT:
            configs.extend([
                {"data_type": "markPriceKlines", "intervals": "1m,3m,5m,15m,1h,4h,1d"},
                {"data_type": "indexPriceKlines", "intervals": "1m,3m,5m,15m,1h,4h,1d"},
                {"data_type": "premiumIndexKlines", "intervals": "1m,3m,5m,15m,1h,4h,1d"}
            ])
    
    console.print(f"[bold blue]Batch Download Configuration:[/bold blue]")
    console.print(f"Trading Type: {trading_type.value}")
    console.print(f"Symbols: {', '.join(symbols) if symbols else 'From config file'}")
    console.print(f"Data Types: {len(configs)}")
    console.print(f"Output Directory: {output_dir}")
    if proxy:
        console.print(f"Proxy: {proxy}")
    
    if not typer.confirm("\nProceed with batch download?"):
        typer.echo("Batch download cancelled.")
        raise typer.Exit()
    
    # Execute batch download
    total_success = 0
    total_failed = 0
    
    for i, config_data in enumerate(configs, 1):
        data_type = DataType(config_data["data_type"])
        intervals = None
        if "intervals" in config_data:
            intervals = parse_intervals(config_data["intervals"])
        
        # Create output directory for this data type
        type_output_dir = os.path.join(output_dir, f"{trading_type.value}_{data_type.value}")
        
        console.print(f"\n[bold blue]Downloading {i}/{len(configs)}: {data_type.value}[/bold blue]")
        
        try:
            config = DownloadConfig(
                trading_type=trading_type,
                data_type=data_type,
                symbols=symbols or [],
                intervals=intervals,
                start_date=parse_date(start_date) if start_date else None,
                end_date=parse_date(end_date) if end_date else None,
                output_dir=type_output_dir,
                proxy=proxy,
                resume=True
            )
            
            downloader = BinanceDataDownloader(config)
            result = downloader.download()
            
            if result.success:
                console.print(f"[green]✅ {data_type.value} completed: {result.files_downloaded} files[/green]")
                total_success += 1
            else:
                console.print(f"[red]❌ {data_type.value} failed: {len(result.errors)} errors[/red]")
                total_failed += 1
                
        except Exception as e:
            console.print(f"[red]❌ {data_type.value} error: {e}[/red]")
            total_failed += 1
    
    # Summary
    console.print(f"\n[bold green]Batch Download Summary:[/bold green]")
    console.print(f"✅ Successful: {total_success}")
    console.print(f"❌ Failed: {total_failed}")
    console.print(f"📁 Output: {output_dir}")


@app.command()
def status(
    progress_file: str = typer.Option(
        ".download_progress.json",
        "--progress-file", "-p",
        help="Progress file path"
    )
):
    """Check download status and progress."""
    
    if not os.path.exists(progress_file):
        console.print("[yellow]No progress file found. No active downloads.[/yellow]")
        return
    
    try:
        import json
        with open(progress_file, 'r') as f:
            progress_data = json.load(f)
        
        progress = DownloadProgress(**progress_data)
        
        console.print(f"[bold blue]Download Status: {progress.status}[/bold blue]")
        
        table = Table(show_header=False)
        table.add_row("Config ID", progress.config_id)
        table.add_row("Total Files", str(progress.total_files))
        table.add_row("Completed", f"{progress.completed_files} ({progress.completed_files/progress.total_files*100:.1f}%)" if progress.total_files > 0 else "0")
        table.add_row("Failed", str(progress.failed_files))
        table.add_row("Current File", progress.current_file or "None")
        if progress.start_time:
            table.add_row("Start Time", progress.start_time)
        if progress.last_update:
            table.add_row("Last Update", progress.last_update)
        
        console.print(table)
        
        if progress.errors:
            console.print(f"\n[bold red]Errors ({len(progress.errors)}):[/bold red]")
            for error in progress.errors[:10]:  # Show first 10 errors
                console.print(f"  • {error}")
            if len(progress.errors) > 10:
                console.print(f"  ... and {len(progress.errors) - 10} more errors")
    
    except Exception as e:
        console.print(f"[red]Error reading progress file: {e}[/red]")


@app.command()
def resume(
    progress_file: str = typer.Option(
        ".download_progress.json",
        "--progress-file", "-p",
        help="Progress file path"
    )
):
    """Resume an interrupted download."""
    
    if not os.path.exists(progress_file):
        console.print("[red]No progress file found. Cannot resume.[/red]")
        raise typer.Exit(1)
    
    try:
        import json
        with open(progress_file, 'r') as f:
            progress_data = json.load(f)
        
        progress = DownloadProgress(**progress_data)
        
        if progress.status == "completed":
            console.print("[yellow]Download already completed.[/yellow]")
            return
        
        console.print(f"[bold blue]Resuming download: {progress.config_id}[/bold blue]")
        console.print(f"Progress: {progress.completed_files}/{progress.total_files} files completed")
        
        # Note: This would require storing the original config in the progress file
        # For now, just show the status
        console.print("[yellow]Note: Resume functionality requires the original download command.[/yellow]")
        console.print("Please run the original download command with --resume flag.")
    
    except Exception as e:
        console.print(f"[red]Error reading progress file: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_symbols(
    trading_type: TradingType = typer.Option(
        TradingType.SPOT,
        "--trading-type", "-t",
        help="Trading type to list symbols for"
    ),
    limit: int = typer.Option(
        50,
        "--limit", "-l",
        help="Maximum number of symbols to display"
    )
):
    """List available symbols for a trading type."""
    console.print(f"[bold blue]Available symbols for {trading_type.value}:[/bold blue]")
    
    try:
        # Create a minimal config to get symbols
        config = DownloadConfig(
            trading_type=trading_type,
            data_type=DataType.KLINES,  # Doesn't matter for symbol listing
            symbols=[],
            output_dir="temp"
        )
        
        downloader = BinanceDataDownloader(config)
        symbols = downloader._get_all_symbols()
        
        if not symbols:
            console.print("[yellow]No symbols found.[/yellow]")
            return
        
        # Display symbols in a table
        table = Table(title=f"Symbols ({trading_type.value})")
        table.add_column("Symbol", style="cyan")
        table.add_column("Index", style="dim")
        
        for i, symbol in enumerate(symbols[:limit], 1):
            table.add_row(symbol, str(i))
        
        console.print(table)
        
        if len(symbols) > limit:
            console.print(f"[dim]Showing {limit} of {len(symbols)} symbols. Use --limit to see more.[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error listing symbols: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_intervals():
    """List available kline intervals."""
    console.print("[bold blue]Available kline intervals:[/bold blue]")
    
    table = Table()
    table.add_column("Interval", style="cyan")
    table.add_column("Description", style="white")
    
    interval_descriptions = {
        "1s": "1 second",
        "1m": "1 minute",
        "3m": "3 minutes",
        "5m": "5 minutes",
        "15m": "15 minutes",
        "30m": "30 minutes",
        "1h": "1 hour",
        "2h": "2 hours",
        "4h": "4 hours",
        "6h": "6 hours",
        "8h": "8 hours",
        "12h": "12 hours",
        "1d": "1 day",
        "3d": "3 days",
        "1w": "1 week",
        "1mo": "1 month"
    }
    
    for interval in Interval:
        description = interval_descriptions.get(interval.value, "")
        table.add_row(interval.value, description)
    
    console.print(table)


@app.command()
def list_data_types():
    """List available data types."""
    console.print("[bold blue]Available data types:[/bold blue]")
    
    table = Table()
    table.add_column("Data Type", style="cyan")
    table.add_column("Description", style="white")
    
    type_descriptions = {
        "klines": "Kline/candlestick data",
        "trades": "Individual trade data",
        "aggTrades": "Aggregated trade data",
        "markPriceKlines": "Mark price kline data (futures only)",
        "indexPriceKlines": "Index price kline data (futures only)",
        "premiumIndexKlines": "Premium index kline data (futures only)"
    }
    
    for data_type in DataType:
        description = type_descriptions.get(data_type.value, "")
        table.add_row(data_type.value, description)
    
    console.print(table)


if __name__ == "__main__":
    app()
