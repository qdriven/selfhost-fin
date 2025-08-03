#!/bin/bash

echo "🚀 开始下载BTC 6-7月数据（保留CSV header）..."

# 创建目录
mkdir -p data/btc_csv downloads/btc_csv

# 设置环境变量
export STORE_DIRECTORY="$(pwd)/downloads/btc_csv"

# 1. 下载现货K线数据
echo "📊 下载BTC现货K线数据..."
cd ../binance-public-data/python

# 下载1分钟K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 1m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载3分钟K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 3m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载5分钟K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 5m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载15分钟K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 15m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载1小时K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 1h \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载4小时K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 4h \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 下载日线K线
python download-kline.py \
  -t spot \
  -s BTCUSDT \
  -i 1d \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/klines"

# 2. 下载期货K线数据
echo "📊 下载BTC期货K线数据..."

# 下载1分钟K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 1m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载3分钟K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 3m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载5分钟K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 5m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载15分钟K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 15m \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载1小时K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 1h \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载4小时K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 4h \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 下载日线K线
python download-kline.py \
  -t um \
  -s BTCUSDT \
  -i 1d \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/klines"

# 3. 下载现货交易数据
echo "📊 下载BTC现货交易数据..."
python download-trade.py \
  -t spot \
  -s BTCUSDT \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/spot/trades"

# 4. 下载期货交易数据
echo "📊 下载BTC期货交易数据..."
python download-trade.py \
  -t um \
  -s BTCUSDT \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/trades"

# 5. 下载期货标记价格K线数据
echo "📊 下载BTC期货标记价格K线数据..."
python download-futures-markPriceKlines.py \
  -t um \
  -s BTCUSDT \
  -i 1m 3m 5m 15m 1h 4h 1d \
  -y 2024 \
  -m 6 7 \
  -folder "$(pwd)/../../crytata/data/btc_csv/futures/markPriceKlines"

# 回到crytata目录
cd ../../crytata

# 6. 使用crytata工具处理下载的数据并生成带header的CSV
echo "🔄 处理下载的数据并生成带header的CSV文件..."

# 启动数据库服务（如果需要）
docker-compose up -d

# 使用crytata工具处理现货数据
crytata historical download-klines \
  --trading-type spot \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --download-dir downloads/btc_csv \
  --output data/btc_csv_processed \
  --save-csv

# 使用crytata工具处理期货数据
crytata historical download-klines \
  --trading-type um \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --download-dir downloads/btc_csv \
  --output data/btc_csv_processed \
  --save-csv

echo "✅ BTC数据下载完成！"
echo "📁 数据保存位置："
echo "  - 原始ZIP文件: downloads/btc_csv/"
echo "  - 处理后的CSV文件: data/btc_csv_processed/"
echo "  - 带header的CSV文件已生成"
echo ""
echo "📋 CSV文件包含以下header："
echo "  - K线数据: symbol,open_time,close_time,open_price,high_price,low_price,close_price,volume,quote_volume,trade_count,taker_buy_volume,taker_buy_quote_volume,interval"
echo "  - 交易数据: symbol,trade_id,price,quantity,quote_quantity,time,is_buyer_maker,is_best_match" 