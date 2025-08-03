#!/bin/bash
# 无GUI版本的安装脚本

echo "🚀 安装 VNPY 无GUI版本..."

# 创建临时requirements文件
cat > requirements-nogui.txt << EOF
# 核心依赖（跳过GUI相关）
vnpy>=3.5.0
numpy>=1.24.0
pandas>=2.0.0
psycopg2-binary>=2.9.0
redis>=4.5.0
sqlalchemy>=2.0.0
requests>=2.31.0
websockets>=11.0
pyyaml>=6.0
python-dotenv>=1.0.0
loguru>=0.7.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
EOF

# 使用uv安装
echo "📦 安装依赖..."
uv pip install -r requirements-nogui.txt

# 清理临时文件
rm requirements-nogui.txt

echo "✅ 安装完成！"
echo "💡 使用以下命令运行："
echo "   uv run python -m vnpy_cry.core.main --console" 