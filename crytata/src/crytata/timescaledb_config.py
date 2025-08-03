"""TimescaleDB configuration and initialization."""

import os
from typing import Optional
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Float, Integer, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger

from .models import KlineData, TradeData, TickerData

Base = declarative_base()


class TimescaleDBConfig:
    """TimescaleDB configuration and management."""
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "crytata", username: str = "crytata", 
                 password: str = "crytata_password"):
        """Initialize TimescaleDB configuration.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        
        self.connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        self.engine = None
        self.Session = None
        
        logger.info(f"TimescaleDB config initialized for {host}:{port}/{database}")
    
    def connect(self) -> bool:
        """Connect to TimescaleDB.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.engine = create_engine(self.connection_string)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Successfully connected to TimescaleDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create TimescaleDB tables with hypertables.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.engine:
            logger.error("Database not connected")
            return False
        
        try:
            # Create base tables
            Base.metadata.create_all(self.engine)
            
            # Create hypertables
            with self.engine.connect() as conn:
                # Create klines hypertable
                conn.execute(text("""
                    SELECT create_hypertable('klines', 'open_time', 
                                           if_not_exists => TRUE,
                                           chunk_time_interval => INTERVAL '1 day');
                """))
                
                # Create trades hypertable
                conn.execute(text("""
                    SELECT create_hypertable('trades', 'time', 
                                           if_not_exists => TRUE,
                                           chunk_time_interval => INTERVAL '1 hour');
                """))
                
                # Create tickers hypertable
                conn.execute(text("""
                    SELECT create_hypertable('tickers', 'timestamp', 
                                           if_not_exists => TRUE,
                                           chunk_time_interval => INTERVAL '1 day');
                """))
                
                # Create indexes for better performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_klines_symbol_interval 
                    ON klines (symbol, interval, open_time DESC);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_trades_symbol_time 
                    ON trades (symbol, time DESC);
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_tickers_symbol_timestamp 
                    ON tickers (symbol, timestamp DESC);
                """))
                
                conn.commit()
            
            logger.info("TimescaleDB tables and hypertables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create TimescaleDB tables: {e}")
            return False
    
    def get_session(self):
        """Get database session.
        
        Returns:
            Database session
        """
        if not self.Session:
            raise RuntimeError("Database not connected")
        return self.Session()


class KlineTable(Base):
    """SQLAlchemy model for kline data with TimescaleDB optimizations."""
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
    
    # TimescaleDB specific indexes
    __table_args__ = (
        Index('idx_klines_symbol_interval_time', 'symbol', 'interval', 'open_time'),
    )


class TradeTable(Base):
    """SQLAlchemy model for trade data with TimescaleDB optimizations."""
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
    
    # TimescaleDB specific indexes
    __table_args__ = (
        Index('idx_trades_symbol_time', 'symbol', 'time'),
    )


class TickerTable(Base):
    """SQLAlchemy model for ticker data with TimescaleDB optimizations."""
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
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # TimescaleDB specific indexes
    __table_args__ = (
        Index('idx_tickers_symbol_timestamp', 'symbol', 'timestamp'),
    )


class TimescaleDBStorage:
    """TimescaleDB storage manager."""
    
    def __init__(self, config: TimescaleDBConfig):
        """Initialize TimescaleDB storage.
        
        Args:
            config: TimescaleDB configuration
        """
        self.config = config
        self.connected = False
        
        if config.connect():
            self.connected = True
            if config.create_tables():
                logger.info("TimescaleDB storage initialized successfully")
            else:
                logger.error("Failed to create TimescaleDB tables")
        else:
            logger.error("Failed to connect to TimescaleDB")
    
    def save_klines(self, klines: list[KlineData]) -> bool:
        """Save kline data to TimescaleDB.
        
        Args:
            klines: List of KlineData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("TimescaleDB not connected")
            return False
        
        if not klines:
            logger.warning("No kline data to save")
            return False
        
        try:
            session = self.config.get_session()
            
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
            logger.info(f"Saved {len(klines)} klines to TimescaleDB")
            return True
            
        except Exception as e:
            logger.error(f"Error saving klines to TimescaleDB: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_trades(self, trades: list[TradeData]) -> bool:
        """Save trade data to TimescaleDB.
        
        Args:
            trades: List of TradeData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("TimescaleDB not connected")
            return False
        
        if not trades:
            logger.warning("No trade data to save")
            return False
        
        try:
            session = self.config.get_session()
            
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
            logger.info(f"Saved {len(trades)} trades to TimescaleDB")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trades to TimescaleDB: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_tickers(self, tickers: list[TickerData]) -> bool:
        """Save ticker data to TimescaleDB.
        
        Args:
            tickers: List of TickerData objects
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.error("TimescaleDB not connected")
            return False
        
        if not tickers:
            logger.warning("No ticker data to save")
            return False
        
        try:
            session = self.config.get_session()
            
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
            logger.info(f"Saved {len(tickers)} tickers to TimescaleDB")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tickers to TimescaleDB: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def query_klines(self, symbol: str, interval: str, 
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 1000) -> list[KlineData]:
        """Query kline data from TimescaleDB.
        
        Args:
            symbol: Symbol to query
            interval: Interval to query
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of records to return
            
        Returns:
            List of KlineData objects
        """
        if not self.connected:
            logger.error("TimescaleDB not connected")
            return []
        
        try:
            session = self.config.get_session()
            
            query = session.query(KlineTable).filter(
                KlineTable.symbol == symbol,
                KlineTable.interval == interval
            )
            
            if start_time:
                query = query.filter(KlineTable.open_time >= start_time)
            if end_time:
                query = query.filter(KlineTable.open_time <= end_time)
            
            query = query.order_by(KlineTable.open_time.desc()).limit(limit)
            
            results = query.all()
            
            klines = []
            for result in results:
                kline = KlineData(
                    symbol=result.symbol,
                    open_time=result.open_time,
                    close_time=result.close_time,
                    open_price=result.open_price,
                    high_price=result.high_price,
                    low_price=result.low_price,
                    close_price=result.close_price,
                    volume=result.volume,
                    quote_volume=result.quote_volume,
                    trade_count=result.trade_count,
                    taker_buy_volume=result.taker_buy_volume,
                    taker_buy_quote_volume=result.taker_buy_quote_volume,
                    interval=result.interval
                )
                klines.append(kline)
            
            logger.info(f"Queried {len(klines)} klines for {symbol} {interval}")
            return klines
            
        except Exception as e:
            logger.error(f"Error querying klines from TimescaleDB: {e}")
            return []
        finally:
            session.close() 