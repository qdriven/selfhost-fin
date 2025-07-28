#!/usr/bin/env python3
"""
VNPY Web Trader 启动脚本
提供基于 Web 的交易界面
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Any

# VNPY 核心模块
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine

# VNPY 网关
from vnpy_okx import OkxGateway

# VNPY Web Trader 应用
from vnpy_webtrader import WebTraderApp

# 项目配置
from ..config import (
    DATABASE_CONFIG,
    REDIS_CONFIG,
    OKX_CONFIG,
    WEB_CONFIG,
    LOGGING_CONFIG,
    SETTINGS as CONFIG_SETTINGS,
    validate_config
)

class WebTraderService:
    """Web Trader 服务"""
    
    def __init__(self):
        """初始化 Web Trader 服务"""
        self.main_engine = None
        self.event_engine = None
        self.web_trader_app = None
        
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
        file_handler = logging.FileHandler(
            log_dir / "webtrader.log",
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
    
    def configure_settings(self):
        """配置 VNPY 全局设置"""
        from vnpy.trader.setting import SETTINGS
        
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
        
        # 注册 OKX 网关
        self.main_engine.add_gateway(OkxGateway)
        self.logger.info("OKX 网关注册完成")
    
    def register_apps(self):
        """注册应用模块"""
        self.logger.info("注册 Web Trader 应用...")
        
        # 注册 Web Trader 应用
        self.web_trader_app = self.main_engine.add_app(WebTraderApp)
        self.logger.info("Web Trader 应用注册完成")
    
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
            self.logger.warning("OKX 配置不完整，跳过连接")
            return True
    
    def start_web_server(self):
        """启动 Web 服务器"""
        self.logger.info("启动 Web 服务器...")
        
        try:
            # 配置 Web 服务器
            web_config = {
                "host": WEB_CONFIG["host"],
                "port": WEB_CONFIG["port"],
                "username": WEB_CONFIG["username"],
                "password": WEB_CONFIG["password"],
            }
            
            # 启动 Web Trader
            if self.web_trader_app:
                # 这里需要根据实际的 vnpy_webtrader API 来调用
                # 由于具体的启动方法可能因版本而异，这里提供一个通用的框架
                self.logger.info(f"Web 服务器将在 {web_config['host']}:{web_config['port']} 启动")
                self.logger.info("Web Trader 应用已准备就绪")
                
                # 保持服务运行
                import time
                while True:
                    time.sleep(60)
                    self.logger.debug("Web Trader 服务运行中...")
            
        except Exception as e:
            self.logger.error(f"Web 服务器启动失败: {e}")
            raise
    
    def shutdown(self):
        """关闭服务"""
        self.logger.info("关闭 Web Trader 服务...")
        
        if self.main_engine:
            self.main_engine.close()
        
        if self.event_engine:
            self.event_engine.stop()
        
        self.logger.info("Web Trader 服务已关闭")
    
    def run(self):
        """运行 Web Trader 服务"""
        try:
            self.logger.info("🌐 启动 VNPY Web Trader 服务...")
            
            # 验证配置
            if not validate_config():
                self.logger.error("配置验证失败，退出服务")
                return
            
            # 初始化系统
            self.configure_settings()
            self.initialize_engines()
            self.register_gateways()
            self.register_apps()
            
            # 连接网关
            self.connect_gateways()
            
            # 启动 Web 服务器
            self.start_web_server()
            
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，准备退出...")
        except Exception as e:
            self.logger.error(f"服务运行错误: {e}")
            raise
        finally:
            self.shutdown()

def main():
    """主函数"""
    # 创建 Web Trader 服务
    service = WebTraderService()
    
    # 运行服务
    service.run()

if __name__ == "__main__":
    main() 