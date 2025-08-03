#!/usr/bin/env python3
"""
简单的功能测试脚本
"""

import sys
from pathlib import Path

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

def test_core():
    """测试核心模块"""
    print("\n🔍 测试核心模块...")
    
    try:
        from vnpy_cry.core.main import VnpyApplication
        print("✅ 核心模块导入成功")
        
        # 创建应用实例（不运行）
        app = VnpyApplication()
        print("✅ 应用实例创建成功")
        
    except ImportError as e:
        print(f"❌ 核心模块导入失败: {e}")
    except Exception as e:
        print(f"❌ 应用实例创建失败: {e}")

if __name__ == "__main__":
    print("🚀 VNPY 加密货币交易系统 - 功能测试")
    print("=" * 50)
    
    test_imports()
    test_config()
    test_core()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！") 