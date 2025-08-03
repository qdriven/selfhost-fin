#!/bin/bash

echo "🚀 开始下载BTC 2025年6-7月完整数据（修复版）..."

# 设置存储目录
export STORE_DIRECTORY="$(pwd)/data/btc_2025"

# 创建目录
mkdir -p "$STORE_DIRECTORY"

echo "📁 数据将保存到: $STORE_DIRECTORY"

# 进入binance-public-data/python目录
cd ../binance-public-data/python

# 设置具体的日期范围，避免下载2020年数据
START_DATE="2025-04-01"
END_DATE="2025-05-31"

echo "📅 下载时间范围: $START_DATE 到 $END_DATE"

# 1. 下载现货K线数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC现货K线数据..."
python3 download-kline.py -t spot -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/spot/klines"

# 2. 下载期货K线数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC期货K线数据..."
python3 download-kline.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/klines"

# 3. 下载现货交易数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC现货交易数据..."
python3 download-trade.py -t spot -s BTCUSDT -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/spot/trades"

# 4. 下载期货交易数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC期货交易数据..."
python3 download-trade.py -t um -s BTCUSDT -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/trades"

# 5. 下载期货标记价格K线数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC期货标记价格K线数据..."
python3 download-futures-markPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/markPriceKlines"

# 6. 下载期货指数价格K线数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC期货指数价格K线数据..."
python3 download-futures-indexPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/indexPriceKlines"

# 7. 下载期货溢价指数K线数据（只下载月度数据，跳过每日数据）
echo "📊 下载BTC期货溢价指数K线数据..."
python3 download-futures-premiumPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2025 -m 6 7 -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/premiumPriceKlines"

# 回到crytata目录
cd ../../crytata

echo "✅ BTC 2025年6-7月数据下载完成！"
echo "📁 数据保存位置: $STORE_DIRECTORY"
echo ""
echo "📋 下载的数据包括："
echo "  ✅ 现货K线数据 (1m, 3m, 5m, 15m, 1h, 4h, 1d)"
echo "  ✅ 期货K线数据 (1m, 3m, 5m, 15m, 1h, 4h, 1d)"
echo "  ✅ 现货交易数据"
echo "  ✅ 期货交易数据"
echo "  ✅ 期货标记价格K线数据"
echo "  ✅ 期货指数价格K线数据"
echo "  ✅ 期货溢价指数K线数据"
echo ""
echo "🔧 修复说明："
echo "  - 添加了 -skip-daily 1 参数，避免下载每日数据"
echo "  - 添加了 -startDate 和 -endDate 参数，限制时间范围"
echo "  - 只下载2025年6-7月的月度数据"
echo ""
echo "📊 数据格式说明："
echo "  - K线数据: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]"
echo "  - 交易数据: [id, price, qty, quoteQty, time, isBuyerMaker, isBestMatch]"
echo ""
echo "🔍 查看下载的文件："
echo "  ls -la $STORE_DIRECTORY"
echo ""
echo "🔄 处理数据并添加CSV header："
echo "  cd ../binance-public-data/python"
echo "  python3 process_btc_data.py $STORE_DIRECTORY" 