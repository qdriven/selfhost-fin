"""Core data collection and processing functionality."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from loguru import logger

from .models import KlineData, TradeData, TickerData


class BinanceDataCollector:
    """Binance data collector for public market data."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the Binance data collector.
        
        Args:
            api_key: Binance API key (optional for public data)
            api_secret: Binance API secret (optional for public data)
        """
        self.client = Client(api_key, api_secret)
        logger.info("Binance data collector initialized")
    
    def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[KlineData]:
        """Get kline/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            start_time: Start time for data collection
            end_time: End time for data collection
            limit: Number of klines to retrieve (max 1000)
            
        Returns:
            List of KlineData objects
        """
        try:
            # Convert datetime to string format expected by Binance
            start_str = start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None
            end_str = end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None
            
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=start_str,
                endTime=end_str,
                limit=limit
            )
            
            kline_data = []
            for kline in klines:
                kline_data.append(KlineData(
                    symbol=symbol,
                    open_time=datetime.fromtimestamp(kline[0] / 1000),
                    close_time=datetime.fromtimestamp(kline[6] / 1000),
                    open_price=float(kline[1]),
                    high_price=float(kline[2]),
                    low_price=float(kline[3]),
                    close_price=float(kline[4]),
                    volume=float(kline[5]),
                    quote_volume=float(kline[7]),
                    trade_count=int(kline[8]),
                    taker_buy_volume=float(kline[9]),
                    taker_buy_quote_volume=float(kline[10]),
                    interval=interval
                ))
            
            logger.info(f"Retrieved {len(kline_data)} klines for {symbol} {interval}")
            return kline_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving klines: {e}")
            return []
    
    def get_recent_trades(self, symbol: str, limit: int = 1000) -> List[TradeData]:
        """Get recent trades for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Number of trades to retrieve (max 1000)
            
        Returns:
            List of TradeData objects
        """
        try:
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            
            trade_data = []
            for trade in trades:
                trade_data.append(TradeData(
                    symbol=symbol,
                    trade_id=int(trade['id']),
                    price=float(trade['price']),
                    quantity=float(trade['qty']),
                    quote_quantity=float(trade['price']) * float(trade['qty']),
                    time=datetime.fromtimestamp(trade['time'] / 1000),
                    is_buyer_maker=trade['isBuyerMaker'],
                    is_best_match=trade.get('isBestMatch')
                ))
            
            logger.info(f"Retrieved {len(trade_data)} recent trades for {symbol}")
            return trade_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving trades: {e}")
            return []
    
    def get_24hr_ticker(self, symbol: str) -> Optional[TickerData]:
        """Get 24hr ticker statistics for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            TickerData object or None if error
        """
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            
            return TickerData(
                symbol=symbol,
                price_change=float(ticker['priceChange']),
                price_change_percent=float(ticker['priceChangePercent']),
                weighted_avg_price=float(ticker['weightedAvgPrice']),
                prev_close_price=float(ticker['prevClosePrice']),
                last_price=float(ticker['lastPrice']),
                last_qty=float(ticker['lastQty']),
                bid_price=float(ticker['bidPrice']),
                ask_price=float(ticker['askPrice']),
                open_price=float(ticker['openPrice']),
                high_price=float(ticker['highPrice']),
                low_price=float(ticker['lowPrice']),
                volume=float(ticker['volume']),
                quote_volume=float(ticker['quoteVolume']),
                open_time=datetime.fromtimestamp(ticker['openTime'] / 1000),
                close_time=datetime.fromtimestamp(ticker['closeTime'] / 1000),
                first_id=int(ticker['firstId']),
                last_id=int(ticker['lastId']),
                count=int(ticker['count'])
            )
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving ticker: {e}")
            return None
    
    def get_all_tickers(self) -> List[TickerData]:
        """Get 24hr ticker statistics for all symbols.
        
        Returns:
            List of TickerData objects
        """
        try:
            tickers = self.client.get_ticker()
            
            ticker_data = []
            for ticker in tickers:
                ticker_data.append(TickerData(
                    symbol=ticker['symbol'],
                    price_change=float(ticker['priceChange']),
                    price_change_percent=float(ticker['priceChangePercent']),
                    weighted_avg_price=float(ticker['weightedAvgPrice']),
                    prev_close_price=float(ticker['prevClosePrice']),
                    last_price=float(ticker['lastPrice']),
                    last_qty=float(ticker['lastQty']),
                    bid_price=float(ticker['bidPrice']),
                    ask_price=float(ticker['askPrice']),
                    open_price=float(ticker['openPrice']),
                    high_price=float(ticker['highPrice']),
                    low_price=float(ticker['lowPrice']),
                    volume=float(ticker['volume']),
                    quote_volume=float(ticker['quoteVolume']),
                    open_time=datetime.fromtimestamp(ticker['openTime'] / 1000),
                    close_time=datetime.fromtimestamp(ticker['closeTime'] / 1000),
                    first_id=int(ticker['firstId']),
                    last_id=int(ticker['lastId']),
                    count=int(ticker['count'])
                ))
            
            logger.info(f"Retrieved {len(ticker_data)} tickers")
            return ticker_data
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving tickers: {e}")
            return []


class DataProcessor:
    """Data processing utilities."""
    
    @staticmethod
    def klines_to_dataframe(klines: List[KlineData]) -> pd.DataFrame:
        """Convert kline data to pandas DataFrame.
        
        Args:
            klines: List of KlineData objects
            
        Returns:
            pandas DataFrame
        """
        if not klines:
            return pd.DataFrame()
        
        data = []
        for kline in klines:
            data.append({
                'symbol': kline.symbol,
                'open_time': kline.open_time,
                'close_time': kline.close_time,
                'open_price': kline.open_price,
                'high_price': kline.high_price,
                'low_price': kline.low_price,
                'close_price': kline.close_price,
                'volume': kline.volume,
                'quote_volume': kline.quote_volume,
                'trade_count': kline.trade_count,
                'taker_buy_volume': kline.taker_buy_volume,
                'taker_buy_quote_volume': kline.taker_buy_quote_volume,
                'interval': kline.interval
            })
        
        df = pd.DataFrame(data)
        df.set_index('open_time', inplace=True)
        return df
    
    @staticmethod
    def trades_to_dataframe(trades: List[TradeData]) -> pd.DataFrame:
        """Convert trade data to pandas DataFrame.
        
        Args:
            trades: List of TradeData objects
            
        Returns:
            pandas DataFrame
        """
        if not trades:
            return pd.DataFrame()
        
        data = []
        for trade in trades:
            data.append({
                'symbol': trade.symbol,
                'trade_id': trade.trade_id,
                'price': trade.price,
                'quantity': trade.quantity,
                'quote_quantity': trade.quote_quantity,
                'time': trade.time,
                'is_buyer_maker': trade.is_buyer_maker,
                'is_best_match': trade.is_best_match
            })
        
        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        return df
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate basic technical indicators for OHLCV data.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicators
        """
        if df.empty:
            return df
        
        # Simple Moving Averages
        df['sma_20'] = df['close_price'].rolling(window=20).mean()
        df['sma_50'] = df['close_price'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close_price'].ewm(span=12).mean()
        df['ema_26'] = df['close_price'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close_price'].rolling(window=20).mean()
        bb_std = df['close_price'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df 