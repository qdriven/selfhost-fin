"""Data storage functionality."""

import os
from datetime import datetime
from typing import List, Optional
import pandas as pd
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from .models import KlineData, TradeData, TickerData


Base = declarative_base()


class KlineTable(Base):
    """SQLAlchemy model for kline data."""
    __tablename__ = 'klines'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    open_time = Column(DateTime, nullable=False, index=True)
    close_time = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, nullable=False)
    trade_count = Column(Integer, nullable=False)
    taker_buy_volume = Column(Float, nullable=False)
    taker_buy_quote_volume = Column(Float, nullable=False)
    interval = Column(String(10), nullable=False, index=True)


class TradeTable(Base):
    """SQLAlchemy model for trade data."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    trade_id = Column(Integer, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    quote_quantity = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False, index=True)
    is_buyer_maker = Column(Boolean, nullable=False)
    is_best_match = Column(Boolean, nullable=True)


class TickerTable(Base):
    """SQLAlchemy model for ticker data."""
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    price_change = Column(Float, nullable=False)
    price_change_percent = Column(Float, nullable=False)
    weighted_avg_price = Column(Float, nullable=False)
    prev_close_price = Column(Float, nullable=False)
    last_price = Column(Float, nullable=False)
    last_qty = Column(Float, nullable=False)
    bid_price = Column(Float, nullable=False)
    ask_price = Column(Float, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, nullable=False)
    open_time = Column(DateTime, nullable=False)
    close_time = Column(DateTime, nullable=False)
    first_id = Column(Integer, nullable=False)
    last_id = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class DataStorage:
    """Data storage manager for CSV and database storage."""
    
    def __init__(self, csv_dir: str = "data", db_url: Optional[str] = None):
        """Initialize data storage.
        
        Args:
            csv_dir: Directory for CSV files
            db_url: Database URL (e.g., 'sqlite:///data.db' or 'postgresql://user:pass@localhost/db')
        """
        self.csv_dir = csv_dir
        self.db_url = db_url
        
        # Create CSV directory
        os.makedirs(csv_dir, exist_ok=True)
        
        # Initialize database if URL provided
        if db_url:
            self.engine = create_engine(db_url)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            logger.info(f"Database initialized: {db_url}")
        else:
            self.engine = None
            self.Session = None
    
    def save_klines_csv(self, klines: List[KlineData], filename: Optional[str] = None) -> str:
        """Save kline data to CSV file with clear headers.
        
        Args:
            klines: List of KlineData objects
            filename: Optional filename, will auto-generate if not provided
            
        Returns:
            Path to saved CSV file
        """
        if not klines:
            logger.warning("No kline data to save")
            return ""
        
        if not filename:
            symbol = klines[0].symbol
            interval = klines[0].interval
            start_time = klines[0].open_time.strftime('%Y%m%d')
            filename = f"{symbol}_{interval}_{start_time}.csv"
        
        filepath = os.path.join(self.csv_dir, filename)
        
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
        # Ensure CSV is saved with headers
        df.to_csv(filepath, index=False, header=True)
        logger.info(f"Saved {len(klines)} klines to {filepath} with headers")
        return filepath
    
    def save_trades_csv(self, trades: List[TradeData], filename: Optional[str] = None) -> str:
        """Save trade data to CSV file with clear headers.
        
        Args:
            trades: List of TradeData objects
            filename: Optional filename, will auto-generate if not provided
            
        Returns:
            Path to saved CSV file
        """
        if not trades:
            logger.warning("No trade data to save")
            return ""
        
        if not filename:
            symbol = trades[0].symbol
            start_time = trades[0].time.strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_trades_{start_time}.csv"
        
        filepath = os.path.join(self.csv_dir, filename)
        
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
        # Ensure CSV is saved with headers
        df.to_csv(filepath, index=False, header=True)
        logger.info(f"Saved {len(trades)} trades to {filepath} with headers")
        return filepath
    
    def save_tickers_csv(self, tickers: List[TickerData], filename: Optional[str] = None) -> str:
        """Save ticker data to CSV file with clear headers.
        
        Args:
            tickers: List of TickerData objects
            filename: Optional filename, will auto-generate if not provided
            
        Returns:
            Path to saved CSV file
        """
        if not tickers:
            logger.warning("No ticker data to save")
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tickers_{timestamp}.csv"
        
        filepath = os.path.join(self.csv_dir, filename)
        
        data = []
        for ticker in tickers:
            data.append({
                'symbol': ticker.symbol,
                'price_change': ticker.price_change,
                'price_change_percent': ticker.price_change_percent,
                'weighted_avg_price': ticker.weighted_avg_price,
                'prev_close_price': ticker.prev_close_price,
                'last_price': ticker.last_price,
                'last_qty': ticker.last_qty,
                'bid_price': ticker.bid_price,
                'ask_price': ticker.ask_price,
                'open_price': ticker.open_price,
                'high_price': ticker.high_price,
                'low_price': ticker.low_price,
                'volume': ticker.volume,
                'quote_volume': ticker.quote_volume,
                'open_time': ticker.open_time,
                'close_time': ticker.close_time,
                'first_id': ticker.first_id,
                'last_id': ticker.last_id,
                'count': ticker.count
            })
        
        df = pd.DataFrame(data)
        # Ensure CSV is saved with headers
        df.to_csv(filepath, index=False, header=True)
        logger.info(f"Saved {len(tickers)} tickers to {filepath} with headers")
        return filepath
    
    def save_klines_db(self, klines: List[KlineData]) -> bool:
        """Save kline data to database.
        
        Args:
            klines: List of KlineData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.Session:
            logger.error("Database not initialized")
            return False
        
        if not klines:
            logger.warning("No kline data to save")
            return False
        
        try:
            session = self.Session()
            
            for kline in klines:
                db_kline = KlineTable(
                    symbol=kline.symbol,
                    open_time=kline.open_time,
                    close_time=kline.close_time,
                    open_price=kline.open_price,
                    high_price=kline.high_price,
                    low_price=kline.low_price,
                    close_price=kline.close_price,
                    volume=kline.volume,
                    quote_volume=kline.quote_volume,
                    trade_count=kline.trade_count,
                    taker_buy_volume=kline.taker_buy_volume,
                    taker_buy_quote_volume=kline.taker_buy_quote_volume,
                    interval=kline.interval
                )
                session.add(db_kline)
            
            session.commit()
            logger.info(f"Saved {len(klines)} klines to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving klines to database: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_trades_db(self, trades: List[TradeData]) -> bool:
        """Save trade data to database.
        
        Args:
            trades: List of TradeData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.Session:
            logger.error("Database not initialized")
            return False
        
        if not trades:
            logger.warning("No trade data to save")
            return False
        
        try:
            session = self.Session()
            
            for trade in trades:
                db_trade = TradeTable(
                    symbol=trade.symbol,
                    trade_id=trade.trade_id,
                    price=trade.price,
                    quantity=trade.quantity,
                    quote_quantity=trade.quote_quantity,
                    time=trade.time,
                    is_buyer_maker=trade.is_buyer_maker,
                    is_best_match=trade.is_best_match
                )
                session.add(db_trade)
            
            session.commit()
            logger.info(f"Saved {len(trades)} trades to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trades to database: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_tickers_db(self, tickers: List[TickerData]) -> bool:
        """Save ticker data to database.
        
        Args:
            tickers: List of TickerData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.Session:
            logger.error("Database not initialized")
            return False
        
        if not tickers:
            logger.warning("No ticker data to save")
            return False
        
        try:
            session = self.Session()
            
            for ticker in tickers:
                db_ticker = TickerTable(
                    symbol=ticker.symbol,
                    price_change=ticker.price_change,
                    price_change_percent=ticker.price_change_percent,
                    weighted_avg_price=ticker.weighted_avg_price,
                    prev_close_price=ticker.prev_close_price,
                    last_price=ticker.last_price,
                    last_qty=ticker.last_qty,
                    bid_price=ticker.bid_price,
                    ask_price=ticker.ask_price,
                    open_price=ticker.open_price,
                    high_price=ticker.high_price,
                    low_price=ticker.low_price,
                    volume=ticker.volume,
                    quote_volume=ticker.quote_volume,
                    open_time=ticker.open_time,
                    close_time=ticker.close_time,
                    first_id=ticker.first_id,
                    last_id=ticker.last_id,
                    count=ticker.count
                )
                session.add(db_ticker)
            
            session.commit()
            logger.info(f"Saved {len(tickers)} tickers to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tickers to database: {e}")
            session.rollback()
            return False
        finally:
            session.close() 