#!/usr/bin/env python3
"""
VNPY 加密货币交易系统主应用启动脚本
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 导入应用类
from vnpy_cry.core.main import VnpyApplication, main

if __name__ == "__main__":
    main() 