#!/bin/bash

echo "🚀 开始下载BTC 6-7月数据..."

# 创建目录
mkdir -p data/btc_historical downloads/btc_historical

# 1. 下载现货K线数据
echo "📊 下载BTC现货K线数据..."
crytata historical download-klines \
  --trading-type spot \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2025-06-01" \
  --end-date "2025-07-31" \
  --download-dir downloads/btc_historical \
  --output data/btc_historical \
  --save-csv --save-timescaledb

# 2. 下载期货K线数据
echo "📊 下载BTC期货K线数据..."
crytata historical download-klines \
  --trading-type um \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2025-06-01" \
  --end-date "2025-07-31" \
  --download-dir downloads/btc_historical \
  --output data/btc_historical \
  --save-csv --save-timescaledb

echo "✅ BTC数据下载完成！"
echo "📁 数据保存位置："
echo "  - CSV文件: data/btc_historical/"
echo "  - 原始文件: downloads/btc_historical/"
echo "  - 数据库: TimescaleDB"