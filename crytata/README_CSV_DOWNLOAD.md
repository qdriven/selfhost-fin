# BTC数据下载指南 - 带Header的CSV格式

本指南说明如何下载BTC 6-7月数据，并确保CSV文件包含清晰的header信息。

## 修改内容

### 1. 代码修改

已对以下文件进行了修改，确保CSV文件保留header信息：

- `src/crytata/historical_downloader.py`: 修改了CSV读取逻辑，自动检测并保留header
- `src/crytata/storage.py`: 确保所有CSV保存操作都包含header

### 2. 新增工具

- `download_btc_csv_with_headers.sh`: 完整的Shell脚本，下载所有BTC数据
- `download_btc_csv_simple.py`: 简单的Python脚本，直接下载并处理CSV数据

## 使用方法

### 方法1: 使用简单的Python脚本（推荐）

```bash
# 进入crytata目录
cd crytata

# 运行Python脚本
python download_btc_csv_simple.py
```

这个脚本会：
- 下载BTC 6-7月的现货和期货数据
- 自动提取ZIP文件中的CSV
- 为CSV添加清晰的header
- 保存到 `data/btc_csv_with_headers/` 目录

### 方法2: 使用Shell脚本

```bash
# 进入crytata目录
cd crytata

# 给脚本执行权限
chmod +x download_btc_csv_with_headers.sh

# 运行脚本
./download_btc_csv_with_headers.sh
```

### 方法3: 使用crytata工具

```bash
# 启动数据库服务
docker-compose up -d

# 下载现货K线数据
crytata historical download-klines \
  --trading-type spot \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --save-csv

# 下载期货K线数据
crytata historical download-klines \
  --trading-type um \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --save-csv
```

## CSV文件格式

### K线数据Header
```
timestamp,open,high,low,close,volume,close_time,quote_volume,trades,taker_buy_base,taker_buy_quote,ignore
```

### 交易数据Header
```
id,price,qty,quoteQty,time,isBuyerMaker,isBestMatch
```

### 处理后的K线数据Header（crytata工具）
```
symbol,open_time,close_time,open_price,high_price,low_price,close_price,volume,quote_volume,trade_count,taker_buy_volume,taker_buy_quote_volume,interval
```

### 处理后的交易数据Header（crytata工具）
```
symbol,trade_id,price,quantity,quote_quantity,time,is_buyer_maker,is_best_match
```

## 数据目录结构

使用Python脚本下载后的目录结构：

```
data/btc_csv_with_headers/
├── spot/
│   ├── klines/
│   │   ├── 1m/
│   │   │   ├── processed_BTCUSDT-1m-2024-06.csv
│   │   │   └── processed_BTCUSDT-1m-2024-07.csv
│   │   ├── 3m/
│   │   ├── 5m/
│   │   ├── 15m/
│   │   ├── 1h/
│   │   ├── 4h/
│   │   └── 1d/
│   └── trades/
│       ├── processed_BTCUSDT-trades-2024-06.csv
│       └── processed_BTCUSDT-trades-2024-07.csv
└── um/
    ├── klines/
    │   ├── 1m/
    │   ├── 3m/
    │   ├── 5m/
    │   ├── 15m/
    │   ├── 1h/
    │   ├── 4h/
    │   └── 1d/
    └── trades/
        ├── processed_BTCUSDT-trades-2024-06.csv
        └── processed_BTCUSDT-trades-2024-07.csv
```

## 数据说明

### 时间间隔
- `1m`: 1分钟K线
- `3m`: 3分钟K线
- `5m`: 5分钟K线
- `15m`: 15分钟K线
- `1h`: 1小时K线
- `4h`: 4小时K线
- `1d`: 日线K线

### 交易类型
- `spot`: 现货交易
- `um`: U本位期货

### 数据类型
- `klines`: K线数据（OHLCV）
- `trades`: 交易数据

## 注意事项

1. **网络连接**: 确保有稳定的网络连接，数据文件较大
2. **存储空间**: 6-7月的BTC数据大约需要几GB存储空间
3. **处理时间**: 下载和处理可能需要几分钟到几十分钟
4. **文件完整性**: 脚本会自动检查文件是否存在，避免重复下载

## 故障排除

### 下载失败
```bash
# 检查网络连接
curl https://data.binance.vision/

# 重试下载
python download_btc_csv_simple.py
```

### 文件损坏
```bash
# 删除损坏的文件并重新下载
rm -rf data/btc_csv_with_headers/
python download_btc_csv_simple.py
```

### 权限问题
```bash
# 确保有写入权限
chmod -R 755 data/
```

## 数据验证

下载完成后，可以检查CSV文件：

```bash
# 查看文件header
head -1 data/btc_csv_with_headers/spot/klines/1m/processed_BTCUSDT-1m-2024-06.csv

# 查看数据行数
wc -l data/btc_csv_with_headers/spot/klines/1m/processed_BTCUSDT-1m-2024-06.csv

# 查看数据样本
head -5 data/btc_csv_with_headers/spot/klines/1m/processed_BTCUSDT-1m-2024-06.csv
``` 