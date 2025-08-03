#!/usr/bin/env python3
"""
VNPY 加密货币交易系统主应用
"""

import sys
import os
from pathlib import Path
from typing import Dict
import logging
from datetime import datetime

# VNPY 核心模块
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.setting import SETTINGS

# VNPY GUI 模块 (可选导入)
try:
    from vnpy.trader.ui import create_qapp, MainWindow
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    create_qapp = None
    MainWindow = None

# VNPY 网关 (可选导入)
try:
    from vnpy_okx import OkxGateway
    HAS_OKX = True
except ImportError:
    HAS_OKX = False
    OkxGateway = None

# VNPY 应用 (可选导入)
try:
    from vnpy_datarecorder import DataRecorderApp
except ImportError:
    DataRecorderApp = None

try:
    from vnpy_ctastrategy import CtaStrategyApp
except ImportError:
    CtaStrategyApp = None

try:
    from vnpy_portfoliostrategy import PortfolioStrategyApp
except ImportError:
    PortfolioStrategyApp = None

try:
    from vnpy_algotrading import AlgoTradingApp
except ImportError:
    AlgoTradingApp = None

try:
    from vnpy_riskmanager import RiskManagerApp
except ImportError:
    RiskManagerApp = None

try:
    from vnpy_webtrader import WebTraderApp
except ImportError:
    WebTraderApp = None

try:
    from vnpy_portfoliomanager import PortfolioManagerApp
except ImportError:
    PortfolioManagerApp = None

try:
    from vnpy_papertrading import PaperTradingApp
except ImportError:
    PaperTradingApp = None

# 项目配置
from ..config import (
    DATABASE_CONFIG, 
    REDIS_CONFIG, 
    OKX_CONFIG,
    LOGGING_CONFIG,
    SETTINGS as CONFIG_SETTINGS,
    validate_config
)

class VnpyApplication:
    """VNPY 应用主类"""
    
    def __init__(self):
        """初始化应用"""
        self.main_engine = None
        self.event_engine = None
        self.main_window = None
        
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.parent.parent
        
        # 设置日志
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        """设置日志配置"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(LOGGING_CONFIG["format"])
        
        # 文件处理器
        if LOGGING_CONFIG["file_handler"]:
            file_handler = logging.FileHandler(
                log_dir / "vnpy_main.log",
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
            
            # 添加到根日志器
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            root_logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
            
        # 控制台处理器
        if LOGGING_CONFIG["console_handler"]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
            
            root_logger = logging.getLogger()
            root_logger.addHandler(console_handler)
    
    def configure_settings(self):
        """配置 VNPY 全局设置"""
        self.logger.info("配置 VNPY 全局设置...")
        
        # 更新 VNPY 设置
        for key, value in CONFIG_SETTINGS.items():
            SETTINGS[key] = value
            
        self.logger.info("VNPY 设置配置完成")
    
    def initialize_engines(self):
        """初始化引擎"""
        self.logger.info("初始化事件引擎和主引擎...")
        
        # 创建事件引擎
        self.event_engine = EventEngine()
        
        # 创建主引擎
        self.main_engine = MainEngine(self.event_engine)
        
        self.logger.info("引擎初始化完成")
    
    def register_gateways(self):
        """注册交易网关"""
        self.logger.info("注册交易网关...")
        
        # 注册 OKX 网关 (如果可用)
        if HAS_OKX and OkxGateway:
            self.main_engine.add_gateway(OkxGateway)
            self.logger.info("OKX 网关注册完成")
        else:
            self.logger.warning("OKX 网关不可用，请安装 vnpy-okx")
        
        # 这里可以添加其他网关
        # self.main_engine.add_gateway(BinanceGateway)
        # self.main_engine.add_gateway(BybitGateway)
    
    def register_apps(self):
        """注册应用模块"""
        self.logger.info("注册应用模块...")
        
        # 注册各种应用 (仅注册可用的应用)
        apps = {
            "DataRecorder": DataRecorderApp,
            "CtaStrategy": CtaStrategyApp,
            "PortfolioStrategy": PortfolioStrategyApp,
            "AlgoTrading": AlgoTradingApp,
            "RiskManager": RiskManagerApp,
            "WebTrader": WebTraderApp,
            "PortfolioManager": PortfolioManagerApp,
            "PaperTrading": PaperTradingApp,
        }
        
        for app_name, app_class in apps.items():
            if app_class is None:
                self.logger.warning(f"{app_name} 应用不可用，跳过注册")
                continue
                
            try:
                self.main_engine.add_app(app_class)
                self.logger.info(f"{app_name} 应用注册成功")
            except Exception as e:
                self.logger.error(f"{app_name} 应用注册失败: {e}")
    
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
            except Exception as e:
                self.logger.error(f"OKX 网关连接失败: {e}")
        else:
            self.logger.warning("OKX 配置不完整，跳过连接")
    
    def create_ui(self, use_gui: bool = True):
        """创建用户界面"""
        if use_gui and HAS_GUI:
            self.logger.info("创建图形用户界面...")
            
            # 创建 Qt 应用
            qapp = create_qapp()
            
            # 创建主窗口
            self.main_window = MainWindow(self.main_engine, self.event_engine)
            self.main_window.showMaximized()
            
            self.logger.info("图形界面创建完成")
            return qapp
        elif use_gui and not HAS_GUI:
            self.logger.warning("GUI 不可用，切换到控制台模式")
            return self.create_ui(use_gui=False)
        else:
            self.logger.info("使用控制台模式")
            return None
    
    def run_console_mode(self):
        """控制台模式运行"""
        self.logger.info("启动控制台模式...")
        
        try:
            while True:
                command = input("输入命令 (help/connect/quit): ").strip().lower()
                
                if command == "help":
                    print("""
可用命令:
- connect: 连接网关
- status: 查看连接状态
- quit: 退出程序
                    """)
                elif command == "connect":
                    self.connect_gateways()
                elif command == "status":
                    gateways = self.main_engine.get_all_gateway_names()
                    print(f"已注册网关: {gateways}")
                elif command == "quit":
                    break
                else:
                    print("未知命令，输入 help 查看帮助")
                    
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，准备退出...")
        except Exception as e:
            self.logger.error(f"运行时错误: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """关闭应用"""
        self.logger.info("关闭 VNPY 应用...")
        
        if self.main_engine:
            self.main_engine.close()
            
        if self.event_engine:
            self.event_engine.stop()
            
        self.logger.info("应用关闭完成")
    
    def run(self, use_gui: bool = True):
        """运行应用"""
        try:
            # 验证配置
            if not validate_config():
                self.logger.error("配置验证失败，退出程序")
                return
            
            # 初始化系统
            self.configure_settings()
            self.initialize_engines()
            self.register_gateways()
            self.register_apps()
            
            if use_gui:
                # GUI 模式
                qapp = self.create_ui(use_gui=True)
                self.connect_gateways()
                
                self.logger.info("VNPY 应用启动完成 (GUI 模式)")
                qapp.exec()
            else:
                # 控制台模式
                self.create_ui(use_gui=False)
                self.logger.info("VNPY 应用启动完成 (控制台模式)")
                self.run_console_mode()
                
        except Exception as e:
            self.logger.error(f"应用启动失败: {e}")
            raise
        finally:
            self.shutdown()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VNPY 加密货币交易系统")
    parser.add_argument(
        "--console", 
        action="store_true", 
        help="使用控制台模式运行"
    )
    
    args = parser.parse_args()
    
    # 创建应用实例
    app = VnpyApplication()
    
    # 运行应用
    app.run(use_gui=not args.console)

if __name__ == "__main__":
    main() 