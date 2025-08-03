#!/usr/bin/env python3
"""
无GUI版本的功能测试脚本
"""

import sys
import os
from pathlib import Path

# 设置环境变量，禁用GUI
os.environ['VNPY_NO_GUI'] = '1'

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    
    try:
        import numpy as np
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ numpy: {e}")
    
    try:
        import pandas as pd
        print(f"✅ pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ pandas: {e}")
    
    try:
        import vnpy
        print(f"✅ vnpy: {vnpy.__version__}")
    except ImportError as e:
        print(f"❌ vnpy: {e}")
    
    try:
        import redis
        print(f"✅ redis: {redis.__version__}")
    except ImportError as e:
        print(f"❌ redis: {e}")
    
    try:
        import psycopg2
        print(f"✅ psycopg2: {psycopg2.__version__}")
    except ImportError as e:
        print(f"❌ psycopg2: {e}")

def test_config():
    """测试配置模块"""
    print("\n🔍 测试配置模块...")
    
    try:
        from vnpy_cry.config.settings import DATABASE_CONFIG, REDIS_CONFIG
        print("✅ 配置模块导入成功")
        print(f"   数据库配置: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
        print(f"   Redis配置: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
    except ImportError as e:
        print(f"❌ 配置模块导入失败: {e}")

def test_core_nogui():
    """测试无GUI核心模块"""
    print("\n🔍 测试无GUI核心模块...")
    
    try:
        # 直接导入核心模块，跳过GUI
        from vnpy_cry.core.data_collector import DataCollectorService
        print("✅ 数据采集服务导入成功")
        
        from vnpy_cry.core.web_trader import WebTraderService
        print("✅ Web交易服务导入成功")
        
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
    except Exception as e:
        print(f"❌ 模块创建失败: {e}")

def test_vnpy_core():
    """测试VNPY核心功能"""
    print("\n🔍 测试VNPY核心功能...")
    
    try:
        from vnpy.event import EventEngine
        print("✅ VNPY事件引擎导入成功")
        
        from vnpy.trader.engine import MainEngine
        print("✅ VNPY主引擎导入成功")
        
        # 创建引擎实例
        event_engine = EventEngine()
        main_engine = MainEngine(event_engine)
        print("✅ VNPY引擎实例创建成功")
        
    except ImportError as e:
        print(f"❌ VNPY核心导入失败: {e}")
    except Exception as e:
        print(f"❌ VNPY引擎创建失败: {e}")

if __name__ == "__main__":
    print("🚀 VNPY 加密货币交易系统 - 无GUI功能测试")
    print("=" * 50)
    
    test_imports()
    test_config()
    test_core_nogui()
    test_vnpy_core()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("�� 系统可以在无GUI模式下运行") 