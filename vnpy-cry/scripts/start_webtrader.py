#!/usr/bin/env python3
"""
VNPY Web Trader 启动脚本
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 导入 Web Trader 服务
from vnpy_cry.core.web_trader import WebTraderService, main

if __name__ == "__main__":
    main() 