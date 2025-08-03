#!/bin/bash

# Crytata 快速启动脚本
# 这个脚本会自动设置环境并启动基本的数据收集

set -e

echo "🚀 Crytata 快速启动脚本"
echo "=========================="

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在 crytata 项目根目录运行此脚本"
    exit 1
fi

# 创建必要的目录
echo "📁 创建目录..."
mkdir -p data downloads logs

# 启动 Docker 服务
echo "🐳 启动 Docker 服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️ 初始化 TimescaleDB..."
python -m crytata timescaledb init

# 收集一些示例数据
echo "📊 收集示例数据..."

# 收集 BTCUSDT 的实时数据
echo "  收集 BTCUSDT 实时数据..."
python -m crytata collect-klines --symbol BTCUSDT --interval 1h --limit 100 --save-csv

# 收集 ETHUSDT 的实时数据
echo "  收集 ETHUSDT 实时数据..."
python -m crytata collect-klines --symbol ETHUSDT --interval 1h --limit 100 --save-csv

# 收集行情数据
echo "  收集行情数据..."
python -m crytata collect-tickers --save-csv

echo ""
echo "✅ 快速启动完成！"
echo ""
echo "📊 可用的服务："
echo "  - TimescaleDB: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "📁 生成的文件："
echo "  - data/: CSV 数据文件"
echo "  - downloads/: 下载的原始数据"
echo "  - logs/: 日志文件"
echo ""
echo "🔧 常用命令："
echo "  # 查看帮助"
echo "  python -m crytata --help"
echo ""
echo "  # 收集实时数据"
echo "  python -m crytata collect-klines --symbol BTCUSDT --interval 1h"
echo ""
echo "  # 下载历史数据"
echo "  python -m crytata historical download-klines --symbols BTCUSDT,ETHUSDT"
echo ""
echo "  # 查询数据库"
echo "  python -m crytata timescaledb query --symbol BTCUSDT --interval 1h"
echo ""
echo "  # 运行示例"
echo "  python examples/basic_usage.py"
echo ""
echo "🛑 停止服务："
echo "  docker-compose down" 