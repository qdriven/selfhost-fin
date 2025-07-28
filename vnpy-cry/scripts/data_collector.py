#!/usr/bin/env python3
"""
VNPY 数据采集服务启动脚本
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 导入数据采集服务
from vnpy_cry.core.data_collector import DataCollectorService, main

if __name__ == "__main__":
    main() 