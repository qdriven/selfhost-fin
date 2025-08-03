#!/bin/bash

echo "🚀 自定义BTC数据下载脚本..."
echo ""

# 获取用户输入
read -p "请输入年份 (默认: 2025): " YEAR
YEAR=${YEAR:-2025}

read -p "请输入开始月份 (1-12): " START_MONTH
read -p "请输入结束月份 (1-12): " END_MONTH

# 验证输入
if ! [[ "$START_MONTH" =~ ^[1-9]$|^1[0-2]$ ]] || ! [[ "$END_MONTH" =~ ^[1-9]$|^1[0-2]$ ]]; then
    echo "❌ 错误: 月份必须是1-12之间的数字"
    exit 1
fi

if [ "$START_MONTH" -gt "$END_MONTH" ]; then
    echo "❌ 错误: 开始月份不能大于结束月份"
    exit 1
fi

# 生成月份列表
MONTHS=""
for ((i=START_MONTH; i<=END_MONTH; i++)); do
    MONTHS="$MONTHS $i"
done

# 设置存储目录
export STORE_DIRECTORY="$(pwd)/data/btc_${YEAR}_${START_MONTH}_to_${END_MONTH}"

# 创建目录
mkdir -p "$STORE_DIRECTORY"

echo ""
echo "📅 下载配置:"
echo "  年份: ${YEAR}"
echo "  月份: ${START_MONTH} 到 ${END_MONTH}"
echo "  月份列表: ${MONTHS}"
echo "📁 数据将保存到: $STORE_DIRECTORY"
echo ""

# 确认下载
read -p "确认开始下载? (y/n): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ 取消下载"
    exit 1
fi

# 进入binance-public-data/python目录
cd ../binance-public-data/python

# 设置具体的日期范围
START_DATE="${YEAR}-$(printf "%02d" $START_MONTH)-01"
END_DATE="${YEAR}-$(printf "%02d" $END_MONTH)-31"

echo "📅 下载时间范围: $START_DATE 到 $END_DATE"
echo ""

# 1. 下载现货K线数据
echo "📊 下载BTC现货K线数据..."
python3 download-kline.py -t spot -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/spot/klines"

# 2. 下载期货K线数据
echo "📊 下载BTC期货K线数据..."
python3 download-kline.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/klines"

# 3. 下载现货交易数据
echo "📊 下载BTC现货交易数据..."
python3 download-trade.py -t spot -s BTCUSDT -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/spot/trades"

# 4. 下载期货交易数据
echo "📊 下载BTC期货交易数据..."
python3 download-trade.py -t um -s BTCUSDT -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/trades"

# 5. 下载期货标记价格K线数据
echo "📊 下载BTC期货标记价格K线数据..."
python3 download-futures-markPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/markPriceKlines"

# 6. 下载期货指数价格K线数据
echo "📊 下载BTC期货指数价格K线数据..."
python3 download-futures-indexPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/indexPriceKlines"

# 7. 下载期货溢价指数K线数据
echo "📊 下载BTC期货溢价指数K线数据..."
python3 download-futures-premiumPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y "$YEAR" -m $MONTHS -startDate "$START_DATE" -endDate "$END_DATE" -skip-daily 1 -folder "$STORE_DIRECTORY/futures/premiumPriceKlines"

# 回到crytata目录
cd ../../crytata

echo ""
echo "✅ BTC ${YEAR}年${START_MONTH}月-${END_MONTH}月数据下载完成！"
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
echo "🔧 下载配置："
echo "  - 年份: ${YEAR}"
echo "  - 月份范围: ${START_MONTH} - ${END_MONTH}"
echo "  - 跳过每日数据，只下载月度数据"
echo "  - 时间范围: ${START_DATE} 到 ${END_DATE}"
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