#!/usr/bin/env python3
"""
VNPY 数据采集服务
专门负责从交易所采集实时数据并存储到 TimescaleDB
"""

import sys
import asyncio
import signal
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

# VNPY 核心模块
from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.constant import Exchange
from vnpy.trader.object import SubscribeRequest, ContractData, TickData, BarData

# VNPY 网关和应用
from vnpy_okx import OkxGateway
from vnpy_datarecorder import DataRecorderApp

# 项目配置
from ..config import (
    DATABASE_CONFIG,
    REDIS_CONFIG,
    OKX_CONFIG,
    DATA_SOURCE_CONFIG,
    LOGGING_CONFIG,
    validate_config
)

class DataCollectorService:
    """数据采集服务"""
    
    def __init__(self):
        """初始化数据采集服务"""
        self.main_engine = None
        self.event_engine = None
        self.data_recorder_app = None
        self.running = False
        
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.parent.parent
        
        # 设置日志
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 订阅的合约列表
        self.subscribed_symbols: List[str] = []
        
        # 统计信息
        self.tick_count = 0
        self.bar_count = 0
        self.last_stats_time = datetime.now()
        
    def setup_logging(self):
        """设置日志配置"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(LOGGING_CONFIG["format"])
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / "data_collector.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
        
        # 添加到根日志器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
    
    def initialize_engines(self):
        """初始化引擎"""
        self.logger.info("初始化事件引擎和主引擎...")
        
        # 创建事件引擎
        self.event_engine = EventEngine()
        
        # 创建主引擎
        self.main_engine = MainEngine(self.event_engine)
        
        # 注册事件处理器
        self.register_event_handlers()
        
        self.logger.info("引擎初始化完成")
    
    def register_event_handlers(self):
        """注册事件处理器"""
        from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT
        
        # 注册 Tick 数据处理器
        self.event_engine.register(EVENT_TICK, self.on_tick)
        
        # 注册合约数据处理器
        self.event_engine.register(EVENT_CONTRACT, self.on_contract)
        
        self.logger.info("事件处理器注册完成")
    
    def on_tick(self, event: Event):
        """处理 Tick 数据"""
        tick: TickData = event.data
        self.tick_count += 1
        
        # 每 1000 个 tick 打印一次统计信息
        if self.tick_count % 1000 == 0:
            now = datetime.now()
            duration = (now - self.last_stats_time).total_seconds()
            rate = 1000 / duration if duration > 0 else 0
            
            self.logger.info(
                f"📊 Tick 统计: 总计 {self.tick_count}, "
                f"最近1000个用时 {duration:.2f}s, "
                f"速率 {rate:.2f} tick/s, "
                f"最新: {tick.symbol}@{tick.last_price}"
            )
            
            self.last_stats_time = now
    
    def on_contract(self, event: Event):
        """处理合约数据"""
        contract: ContractData = event.data
        self.logger.debug(f"收到合约信息: {contract.symbol}.{contract.exchange.value}")
    
    def register_gateways(self):
        """注册交易网关"""
        self.logger.info("注册交易网关...")
        
        # 注册 OKX 网关
        self.main_engine.add_gateway(OkxGateway)
        self.logger.info("OKX 网关注册完成")
    
    def register_apps(self):
        """注册应用模块"""
        self.logger.info("注册数据记录应用...")
        
        # 注册数据记录应用
        self.data_recorder_app = self.main_engine.add_app(DataRecorderApp)
        self.logger.info("数据记录应用注册完成")
    
    def connect_gateways(self):
        """连接交易网关"""
        self.logger.info("连接交易网关...")
        
        # 连接 OKX
        if all([OKX_CONFIG["api_key"], OKX_CONFIG["secret_key"], OKX_CONFIG["passphrase"]]):
            okx_setting = {
                "API Key": OKX_CONFIG["api_key"],
                "Secret Key": OKX_CONFIG["secret_key"], 
                "Passphrase": OKX_CONFIG["passphrase"],
                "服务器": OKX_CONFIG["subdomain"],
                "代理地址": OKX_CONFIG["proxy_host"],
                "代理端口": OKX_CONFIG["proxy_port"],
            }
            
            try:
                self.main_engine.connect(okx_setting, "OKX")
                self.logger.info("OKX 网关连接成功")
                return True
            except Exception as e:
                self.logger.error(f"OKX 网关连接失败: {e}")
                return False
        else:
            self.logger.error("OKX 配置不完整，无法连接")
            return False
    
    def subscribe_data(self):
        """订阅市场数据"""
        self.logger.info("开始订阅市场数据...")
        
        # 等待网关连接完成
        asyncio.sleep(5)
        
        # 从配置中获取要订阅的合约
        symbols = DATA_SOURCE_CONFIG.get("symbols", [])
        
        for symbol_str in symbols:
            try:
                # 解析符号格式: BTCUSDT.OKX
                if "." in symbol_str:
                    symbol, exchange_str = symbol_str.split(".")
                    exchange = Exchange(exchange_str)
                else:
                    symbol = symbol_str
                    exchange = Exchange.OKX
                
                # 创建订阅请求
                req = SubscribeRequest(
                    symbol=symbol,
                    exchange=exchange
                )
                
                # 发送订阅请求
                self.main_engine.subscribe(req, "OKX")
                self.subscribed_symbols.append(symbol_str)
                
                self.logger.info(f"✅ 订阅成功: {symbol_str}")
                
            except Exception as e:
                self.logger.error(f"❌ 订阅失败 {symbol_str}: {e}")
        
        self.logger.info(f"📡 总计订阅了 {len(self.subscribed_symbols)} 个合约")
    
    def setup_data_recording(self):
        """设置数据记录"""
        if self.data_recorder_app:
            self.logger.info("配置数据记录器...")
            
            # 这里可以配置数据记录的具体参数
            # 比如记录哪些数据、记录频率等
            
            self.logger.info("数据记录器配置完成")
    
    def print_statistics(self):
        """打印统计信息"""
        self.logger.info("=== 数据采集统计 ===")
        self.logger.info(f"📈 已处理 Tick 数据: {self.tick_count}")
        self.logger.info(f"📊 已处理 Bar 数据: {self.bar_count}")
        self.logger.info(f"📡 订阅合约数量: {len(self.subscribed_symbols)}")
        self.logger.info(f"⏰ 运行时间: {datetime.now()}")
        self.logger.info("==================")
    
    def setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info(f"收到信号 {signum}，准备关闭...")
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """启动数据采集服务"""
        try:
            self.logger.info("🚀 启动 VNPY 数据采集服务...")
            
            # 验证配置
            if not validate_config():
                self.logger.error("配置验证失败，退出服务")
                return
            
            # 初始化系统
            self.initialize_engines()
            self.register_gateways()
            self.register_apps()
            
            # 连接网关
            if not self.connect_gateways():
                self.logger.error("网关连接失败，退出服务")
                return
            
            # 设置数据记录
            self.setup_data_recording()
            
            # 等待连接稳定
            self.logger.info("等待网关连接稳定...")
            asyncio.sleep(10)
            
            # 订阅数据
            self.subscribe_data()
            
            # 设置信号处理器
            self.setup_signal_handlers()
            
            self.running = True
            self.logger.info("✅ 数据采集服务启动完成")
            
            # 主循环
            while self.running:
                asyncio.sleep(60)  # 每分钟检查一次
                self.print_statistics()
            
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，准备退出...")
        except Exception as e:
            self.logger.error(f"服务运行错误: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """停止数据采集服务"""
        self.logger.info("🛑 关闭数据采集服务...")
        
        self.running = False
        
        if self.main_engine:
            self.main_engine.close()
        
        if self.event_engine:
            self.event_engine.stop()
        
        self.print_statistics()
        self.logger.info("数据采集服务已关闭")

def main():
    """主函数"""
    # 创建数据采集服务
    collector = DataCollectorService()
    
    # 启动服务
    collector.start()

if __name__ == "__main__":
    main() 