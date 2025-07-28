"""
VNPY 配置文件
配置数据库连接、网关、日志等核心设置
"""

import os
from typing import Dict, Any
from pathlib import Path

# 获取环境变量
def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent.parent

# 数据库配置
DATABASE_CONFIG = {
    "driver": "postgresql",
    "host": get_env("POSTGRES_HOST", "localhost"),
    "port": int(get_env("POSTGRES_PORT", "5432")),
    "user": get_env("POSTGRES_USER", "vnpy"),
    "password": get_env("POSTGRES_PASSWORD", "vnpy_password_2024"),
    "database": get_env("POSTGRES_DATABASE", "vnpy_crypto"),
    "timezone": "UTC"
}

# Redis 配置
REDIS_CONFIG = {
    "host": get_env("REDIS_HOST", "localhost"),
    "port": int(get_env("REDIS_PORT", "6379")),
    "db": int(get_env("REDIS_DB", "0")),
    "password": get_env("REDIS_PASSWORD", ""),
    "decode_responses": True
}

# OKX 网关配置
OKX_CONFIG = {
    "api_key": get_env("OKX_API_KEY"),
    "secret_key": get_env("OKX_SECRET_KEY"),
    "passphrase": get_env("OKX_PASSPHRASE"),
    "subdomain": get_env("OKX_SUBDOMAIN", "www"),  # www, app, my
    "sandbox": get_env("OKX_SANDBOX", "false").lower() == "true",
    "proxy_host": get_env("OKX_PROXY_HOST", ""),
    "proxy_port": int(get_env("OKX_PROXY_PORT", "0")) if get_env("OKX_PROXY_PORT") else 0
}

# 交易网关列表
GATEWAYS = [
    "vnpy_okx",
    # "vnpy_binance",
    # "vnpy_bybit",
]

# 应用模块列表
APPS = [
    "vnpy_datarecorder",     # 数据记录
    "vnpy_ctastrategy",      # CTA策略
    "vnpy_portfoliostrategy", # 组合策略
    "vnpy_algotrading",      # 算法交易
    "vnpy_riskmanager",      # 风险管理
    "vnpy_webtrader",        # Web交易
    "vnpy_portfoliomanager", # 组合管理
    "vnpy_papertrading",     # 模拟交易
]

# 日志配置
LOGGING_CONFIG = {
    "level": get_env("LOG_LEVEL", "INFO"),
    "file_handler": True,
    "console_handler": True,
    "file_path": BASE_DIR / "logs" / "vnpy.log",
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "backup_count": 10,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# 数据源配置
DATA_SOURCE_CONFIG = {
    "default_gateway": "OKX",
    "tick_data_enabled": True,
    "bar_data_enabled": True,
    "bar_intervals": ["1m", "5m", "15m", "1h", "1d"],
    "symbols": [
        "BTCUSDT.OKX",
        "ETHUSDT.OKX", 
        "BNBUSDT.OKX",
        "ADAUSDT.OKX",
        "SOLUSDT.OKX",
        "DOTUSDT.OKX",
        "AVAXUSDT.OKX",
        "MATICUSDT.OKX"
    ]
}

# 风险管理配置
RISK_CONFIG = {
    "trade_limit": True,
    "active_order_limit": 50,
    "cancel_order_limit": 1000,
    "order_flow_limit": 100,  # 每分钟订单限制
    "order_flow_clear": 60,   # 订单流量清除时间(秒)
    "order_size_limit": 1000000,  # 单笔订单大小限制
    "order_cancel_limit": 50,   # 撤单限制
    "trade_limit": 1000,       # 交易限制
}

# 策略配置
STRATEGY_CONFIG = {
    "auto_start": False,
    "load_strategies": True,
    "strategy_folder": BASE_DIR / "strategies",
    "default_settings": {
        "class_name": "",
        "author": "vnpy_trader",
        "parameters": {},
        "variables": {}
    }
}

# Web 界面配置
WEB_CONFIG = {
    "host": "0.0.0.0",
    "port": 8080,
    "username": "admin",
    "password": "admin123",
    "cors_origins": ["*"],
    "api_prefix": "/api/v1"
}

# 监控配置
MONITORING_CONFIG = {
    "enable_metrics": True,
    "metrics_port": 8090,
    "enable_health_check": True,
    "health_check_port": 8091,
    "alert_webhook": get_env("ALERT_WEBHOOK_URL", "")
}

# 全局设置字典
SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,
    
    # 数据库设置
    "database.driver": DATABASE_CONFIG["driver"],
    "database.host": DATABASE_CONFIG["host"],
    "database.port": DATABASE_CONFIG["port"],
    "database.database": DATABASE_CONFIG["database"],
    "database.user": DATABASE_CONFIG["user"],
    "database.password": DATABASE_CONFIG["password"],
    
    # 日志设置
    "log.active": True,
    "log.level": LOGGING_CONFIG["level"],
    "log.console": LOGGING_CONFIG["console_handler"],
    "log.file": LOGGING_CONFIG["file_handler"],
}

# 验证配置函数
def validate_config() -> bool:
    """验证配置是否正确"""
    # 检查必要的环境变量
    required_vars = ["POSTGRES_HOST", "REDIS_HOST"]
    for var in required_vars:
        if not get_env(var):
            print(f"警告: 环境变量 {var} 未设置")
            return False
    
    # 检查OKX配置（如果启用）
    if "vnpy_okx" in GATEWAYS:
        okx_vars = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
        for var in okx_vars:
            if not get_env(var):
                print(f"警告: OKX配置项 {var} 未设置")
                return False
    
    print("✅ 配置验证通过")
    return True

if __name__ == "__main__":
    validate_config() 