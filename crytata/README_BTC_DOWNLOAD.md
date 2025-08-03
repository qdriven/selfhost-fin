# BTC 6-7月数据下载指南

根据binance-public-data官方工具，获取BTC现货和期货的完整数据。

## 快速开始

### 方法1: 使用完整脚本（推荐）

```bash
# 进入python目录
cd binance-public-data/python

# 给脚本执行权限
chmod +x download_btc_complete.sh

# 运行完整下载脚本
./download_btc_complete.sh
```

### 方法2: 手动执行命令

```bash
# 设置存储目录
export STORE_DIRECTORY="$(pwd)/data/btc_2024_06_07"

# 1. 下载现货K线数据
python3 download-kline.py -t spot -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2024 -m 6 7

# 2. 下载期货K线数据
python3 download-kline.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2024 -m 6 7

# 3. 下载现货交易数据
python3 download-trade.py -t spot -s BTCUSDT -y 2024 -m 6 7

# 4. 下载期货交易数据
python3 download-trade.py -t um -s BTCUSDT -y 2024 -m 6 7

# 5. 下载期货标记价格K线数据
python3 download-futures-markPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2024 -m 6 7

# 6. 下载期货指数价格K线数据
python3 download-futures-indexPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2024 -m 6 7

# 7. 下载期货溢价指数K线数据
python3 download-futures-premiumPriceKlines.py -t um -s BTCUSDT -i 1m 3m 5m 15m 1h 4h 1d -y 2024 -m 6 7
```

## 数据处理（添加CSV Header）

下载完成后，运行处理脚本为CSV文件添加header：

```bash
# 处理下载的数据并添加header
python3 process_btc_data.py

# 或者指定数据目录
python3 process_btc_data.py data/btc_2024_06_07
```

## 数据说明

### 下载的数据类型

1. **现货K线数据** (`spot/klines/`)
   - 时间间隔: 1m, 3m, 5m, 15m, 1h, 4h, 1d
   - 数据格式: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]

2. **期货K线数据** (`futures/klines/`)
   - 时间间隔: 1m, 3m, 5m, 15m, 1h, 4h, 1d
   - 数据格式: 同上

3. **现货交易数据** (`spot/trades/`)
   - 数据格式: [id, price, qty, quoteQty, time, isBuyerMaker, isBestMatch]

4. **期货交易数据** (`futures/trades/`)
   - 数据格式: 同上

5. **期货标记价格K线数据** (`futures/markPriceKlines/`)
   - 时间间隔: 1m, 3m, 5m, 15m, 1h, 4h, 1d
   - 数据格式: 同K线数据

6. **期货指数价格K线数据** (`futures/indexPriceKlines/`)
   - 时间间隔: 1m, 3m, 5m, 15m, 1h, 4h, 1d
   - 数据格式: 同K线数据

7. **期货溢价指数K线数据** (`futures/premiumPriceKlines/`)
   - 时间间隔: 1m, 3m, 5m, 15m, 1h, 4h, 1d
   - 数据格式: 同K线数据

### 文件命名规则

- **K线数据**: `BTCUSDT-{interval}-{year}-{month}.zip`
  - 例如: `BTCUSDT-1m-2024-06.zip`

- **交易数据**: `BTCUSDT-trades-{year}-{month}.zip`
  - 例如: `BTCUSDT-trades-2024-06.zip`

## 目录结构

下载完成后的目录结构：

```
data/btc_2024_06_07/
├── spot/
│   ├── klines/
│   │   ├── 1m/
│   │   │   ├── BTCUSDT-1m-2024-06.zip
│   │   │   └── BTCUSDT-1m-2024-07.zip
│   │   ├── 3m/
│   │   ├── 5m/
│   │   ├── 15m/
│   │   ├── 1h/
│   │   ├── 4h/
│   │   └── 1d/
│   └── trades/
│       ├── BTCUSDT-trades-2024-06.zip
│       └── BTCUSDT-trades-2024-07.zip
└── futures/
    ├── klines/
    ├── trades/
    ├── markPriceKlines/
    ├── indexPriceKlines/
    └── premiumPriceKlines/
```

处理后的目录结构：

```
data/btc_2024_06_07/processed/
├── spot/
│   ├── klines/
│   │   ├── 1m/
│   │   │   ├── processed_BTCUSDT-1m-2024-06.csv
│   │   │   └── processed_BTCUSDT-1m-2024-07.csv
│   │   └── ...
│   └── trades/
│       ├── processed_BTCUSDT-trades-2024-06.csv
│       └── processed_BTCUSDT-trades-2024-07.csv
└── futures/
    ├── klines/
    ├── trades/
    ├── markPriceKlines/
    ├── indexPriceKlines/
    └── premiumPriceKlines/
```

## 数据验证

下载完成后，可以验证数据：

```bash
# 查看下载的文件
ls -la data/btc_2024_06_07/

# 检查ZIP文件内容
unzip -l data/btc_2024_06_07/spot/klines/1m/BTCUSDT-1m-2024-06.zip

# 处理数据后查看CSV文件
head -5 data/btc_2024_06_07/processed/spot/klines/1m/processed_BTCUSDT-1m-2024-06.csv
```

## 参数说明

### 市场类型 (-t)
- `spot`: 现货市场
- `um`: USD-M期货市场
- `cm`: COIN-M期货市场

### 时间间隔 (-i)
- `1m`: 1分钟
- `3m`: 3分钟
- `5m`: 5分钟
- `15m`: 15分钟
- `30m`: 30分钟
- `1h`: 1小时
- `2h`: 2小时
- `4h`: 4小时
- `6h`: 6小时
- `8h`: 8小时
- `12h`: 12小时
- `1d`: 1天
- `3d`: 3天
- `1w`: 1周
- `1mo`: 1个月

### 其他参数
- `-s`: 交易对符号
- `-y`: 年份
- `-m`: 月份
- `-d`: 具体日期
- `-startDate`: 开始日期
- `-endDate`: 结束日期
- `-folder`: 存储目录
- `-c`: 是否下载校验文件

## 注意事项

1. **网络连接**: 确保有稳定的网络连接
2. **存储空间**: 6-7月的BTC数据大约需要几GB空间
3. **下载时间**: 根据网络速度，可能需要几分钟到几十分钟
4. **文件完整性**: 脚本会自动检查文件是否存在，避免重复下载

## 故障排除

### 下载失败
```bash
# 检查网络连接
curl https://data.binance.vision/

# 检查Python环境
python3 --version
pip3 list | grep pandas
```

### 文件损坏
```bash
# 删除损坏的文件并重新下载
rm -rf data/btc_2024_06_07/
./download_btc_complete.sh
```

### 权限问题
```bash
# 确保有写入权限
chmod -R 755 data/
``` 