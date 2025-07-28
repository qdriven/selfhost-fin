#!/usr/bin/env python3
"""
VNPY 加密货币交易系统设置脚本
帮助用户快速配置和启动系统
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 添加 src 目录到 Python 路径
src_path = PROJECT_ROOT / "src"
sys.path.insert(0, str(src_path))

class VnpySetup:
    """VNPY 项目设置类"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        
    def check_prerequisites(self) -> bool:
        """检查先决条件"""
        print("🔍 检查系统环境...")
        
        # 检查 Python 版本
        if sys.version_info < (3, 11):
            print("❌ Python 版本需要 3.11 或更高")
            return False
        print("✅ Python 版本符合要求")
        
        # 检查 uv
        if not shutil.which("uv"):
            print("❌ 未找到 uv，请先安装: curl -LsSf https://astral.sh/uv/install.sh | sh")
            return False
        print("✅ uv 已安装")
        
        # 检查 Docker
        if not shutil.which("docker"):
            print("❌ 未找到 Docker，请先安装 Docker")
            return False
        print("✅ Docker 已安装")
        
        # 检查 Docker Compose
        if not shutil.which("docker-compose"):
            print("❌ 未找到 docker-compose，请先安装")
            return False
        print("✅ Docker Compose 已安装")
        
        return True
    
    def setup_environment(self):
        """设置环境配置"""
        print("🔧 设置环境配置...")
        
        env_template = self.project_root / "config.env.template"
        env_file = self.project_root / ".env"
        
        if not env_file.exists() and env_template.exists():
            shutil.copy(env_template, env_file)
            print(f"✅ 已创建环境配置文件: {env_file}")
            print("⚠️  请编辑 .env 文件，配置你的 OKX API 密钥")
        else:
            print("ℹ️  环境配置文件已存在")
    
    def install_dependencies(self):
        """安装依赖"""
        print("📦 安装 Python 依赖...")
        
        try:
            # 安装主要依赖
            subprocess.run(["uv", "sync"], cwd=self.project_root, check=True)
            print("✅ 主要依赖安装完成")
            
            # 安装开发依赖
            subprocess.run(["uv", "sync", "--group", "dev"], cwd=self.project_root, check=True)
            print("✅ 开发依赖安装完成")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
        
        return True
    
    def setup_database(self):
        """设置数据库"""
        print("🗄️  准备数据库环境...")
        
        # 确保数据库初始化脚本可执行
        init_script = self.project_root / "database" / "timescaledb" / "init" / "01-init-vnpy.sql"
        if init_script.exists():
            print("✅ 数据库初始化脚本已准备")
        else:
            print("⚠️  未找到数据库初始化脚本")
    
    def create_directories(self):
        """创建必要的目录"""
        print("📁 创建项目目录...")
        
        directories = [
            "logs",
            "data", 
            "strategies/custom",
            "notebooks",
            "monitoring/grafana/dashboards",
            "monitoring/grafana/datasources"
        ]
        
        for dir_path in directories:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_path}")
    
    def show_configuration_guide(self):
        """显示配置指南"""
        print("\n" + "="*60)
        print("🎯 配置指南")
        print("="*60)
        
        print("\n1. 配置 OKX API 密钥:")
        print("   - 编辑 .env 文件")
        print("   - 设置 OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE")
        
        print("\n2. 启动服务:")
        print("   docker-compose up -d")
        
        print("\n3. 查看服务状态:")
        print("   docker-compose ps")
        
        print("\n4. 查看日志:")
        print("   docker-compose logs -f")
        
        print("\n5. 访问服务:")
        print("   - Web 交易界面: http://localhost:8080")
        print("   - Jupyter Lab: http://localhost:8888")
        print("   - Grafana 监控: http://localhost:3000")
        
        print("\n6. 本地开发:")
        print("   uv run python scripts/main.py --console")
        
        print("\n" + "="*60)
    
    def run_setup(self):
        """运行完整设置"""
        print("🚀 VNPY 加密货币交易系统设置")
        print("="*50)
        
        # 检查先决条件
        if not self.check_prerequisites():
            print("❌ 环境检查失败，请先安装必要的工具")
            return False
        
        # 创建目录
        self.create_directories()
        
        # 设置环境
        self.setup_environment()
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        # 设置数据库
        self.setup_database()
        
        print("\n✅ 设置完成！")
        
        # 显示配置指南
        self.show_configuration_guide()
        
        return True

def main():
    """主函数"""
    setup = VnpySetup()
    success = setup.run_setup()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 