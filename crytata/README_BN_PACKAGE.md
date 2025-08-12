# BN Package - Binance数据下载器

BN包是一个功能强大的Binance公共数据下载工具，支持代理、断点续传等高级功能。

## 🚀 快速开始

### 安装

```bash
# 在crytata目录下
pip install -e .
# 或者使用uv
uv run pip install -e .
```

### 基本使用

```bash
# 查看帮助
uv run bn --help

# 下载现货K线数据
uv run bn download --trading-type spot --data-type klines --intervals 1m,1h,1d --symbols BTCUSDT

# 下载期货交易数据
uv run bn download --trading-type um --data-type trades --symbols BTCUSDT
```

## 📊 支持的数据类型

### 交易类型 (Trading Types)
- `spot`: 现货交易
- `um`: U本位期货 (USD-M Futures)
- `cm`: 币本位期货 (COIN-M Futures)

### 数据类型 (Data Types)
- `klines`: K线/蜡烛图数据
- `trades`: 交易数据
- `aggTrades`: 聚合交易数据
- `markPriceKlines`: 标记价格K线 (仅期货)
- `indexPriceKlines`: 指数价格K线 (仅期货)
- `premiumIndexKlines`: 溢价指数K线 (仅期货)

### 时间间隔 (Intervals)
- `1s`, `1m`, `3m`, `5m`, `15m`, `30m`
- `1h`, `2h`, `4h`, `6h`, `8h`, `12h`
- `1d`, `3d`, `1w`, `1mo`

## 🔧 主要命令

### 1. 下载命令 (download)

```bash
# 基本下载
uv run bn download \
  --trading-type um \
  --data-type trades \
  --symbols BTCUSDT \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  --output-dir data/futures_2025

# 下载K线数据 (需要指定intervals)
uv run bn download \
  --trading-type um \
  --data-type klines \
  --intervals 1m,1h,1d \
  --symbols BTCUSDT \
  --start-date 2025-01-01 \
  --end-date 2025-12-31

# 使用代理
uv run bn download \
  --trading-type spot \
  --data-type klines \
  --intervals 1h \
  --symbols BTCUSDT \
  --proxy http://proxy:8080

# 自定义重试和超时
uv run bn download \
  --trading-type spot \
  --data-type trades \
  --symbols BTCUSDT \
  --max-retries 5 \
  --timeout 60
```

### 2. 批量下载 (batch-download)

```bash
# 批量下载所有数据类型
uv run bn batch-download \
  --trading-type um \
  --symbols BTCUSDT ETHUSDT \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  --output-dir data/futures_2025_complete

# 从配置文件批量下载
uv run bn batch-download \
  --config-file download_config.json \
  --output-dir data/custom_batch
```

### 3. 状态查询 (status)

```bash
# 查看下载状态
uv run bn status

# 指定进度文件
uv run bn status --progress-file .custom_progress.json
```

### 4. 断点续传 (resume)

```bash
# 继续之前的下载
uv run bn download \
  --trading-type um \
  --data-type trades \
  --symbols BTCUSDT \
  --resume \
  --progress-file .download_progress.json
```

### 5. 信息查询命令

```bash
# 列出可用交易对
uv run bn list-symbols --trading-type um --limit 100

# 列出可用时间间隔
uv run bn list-intervals

# 列出可用数据类型
uv run bn list-data-types
```

## 📁 输出文件结构

下载完成后，数据将保存在指定的输出目录中：

```
data/
├── futures_2025_trades_um/
│   ├── BTCUSDT-trades-2025-01.zip
│   ├── BTCUSDT-trades-2025-02.zip
│   └── ...
├── futures_2025_klines_um/
│   ├── BTCUSDT-1m-2025-01.zip
│   ├── BTCUSDT-1h-2025-01.zip
│   ├── BTCUSDT-1d-2025-01.zip
│   └── ...
└── ...
```

## 🌐 代理配置

支持HTTP代理，适用于需要代理访问的网络环境：

```bash
# 使用HTTP代理
uv run bn download \
  --trading-type spot \
  --data-type klines \
  --intervals 1h \
  --symbols BTCUSDT \
  --proxy http://proxy.company.com:8080

# 使用SOCKS代理 (通过环境变量)
export HTTP_PROXY=socks5://proxy:1080
export HTTPS_PROXY=socks5://proxy:1080
uv run bn download --trading-type spot --data-type trades --symbols BTCUSDT
```

## ⚡ 断点续传

下载支持断点续传功能：

1. **自动检测**: 如果文件已存在且完整，会跳过下载
2. **进度保存**: 下载进度保存在`.download_progress.json`文件中
3. **手动恢复**: 使用`--resume`参数继续下载

```bash
# 启用断点续传 (默认启用)
uv run bn download \
  --trading-type um \
  --data-type trades \
  --symbols BTCUSDT \
  --resume

# 禁用断点续传
uv run bn download \
  --trading-type um \
  --data-type trades \
  --symbols BTCUSDT \
  --no-resume
```

## 📋 配置文件示例

创建`download_config.json`文件进行批量下载：

```json
[
  {
    "data_type": "klines",
    "intervals": "1m,1h,1d"
  },
  {
    "data_type": "trades"
  },
  {
    "data_type": "aggTrades"
  },
  {
    "data_type": "markPriceKlines",
    "intervals": "1m,1h,1d"
  }
]
```

然后使用：

```bash
uv run bn batch-download \
  --config-file download_config.json \
  --trading-type um \
  --symbols BTCUSDT \
  --start-date 2025-01-01 \
  --end-date 2025-12-31
```

## 🐛 故障排除

### 常见问题

1. **网络超时**
   ```bash
   # 增加超时时间
   uv run bn download --timeout 120 --max-retries 5
   ```

2. **代理问题**
   ```bash
   # 检查代理配置
   uv run bn download --proxy http://proxy:8080 --verbose
   ```

3. **磁盘空间不足**
   ```bash
   # 检查可用空间
   df -h
   # 清理旧文件
   rm -rf data/old_downloads
   ```

4. **权限问题**
   ```bash
   # 确保有写入权限
   chmod 755 data/
   ```

### 日志和调试

```bash
# 启用详细日志
uv run bn download --verbose

# 查看下载状态
uv run bn status

# 检查进度文件
cat .download_progress.json
```

## 📚 高级用法

### 自定义进度文件

```bash
# 使用自定义进度文件
uv run bn download \
  --trading-type spot \
  --data-type klines \
  --intervals 1h \
  --symbols BTCUSDT \
  --progress-file .btc_klines_progress.json
```

### 并发下载

虽然bn包本身是单线程的，但可以通过多个终端实例实现并发：

```bash
# 终端1: 下载现货数据
uv run bn download --trading-type spot --data-type klines --intervals 1h --symbols BTCUSDT

# 终端2: 下载期货数据
uv run bn download --trading-type um --data-type trades --symbols BTCUSDT

# 终端3: 下载其他数据
uv run bn download --trading-type um --data-type klines --intervals 1d --symbols ETHUSDT
```

## 🔄 与旧脚本的对比

| 功能 | 旧Shell脚本 | 新的BN包 |
|------|-------------|----------|
| 代理支持 | ❌ 无 | ✅ 完整支持 |
| 断点续传 | ❌ 无 | ✅ 自动支持 |
| 错误处理 | ❌ 基础 | ✅ 高级重试 |
| 进度显示 | ❌ 无 | ✅ 实时进度 |
| 配置灵活性 | ❌ 硬编码 | ✅ 参数化 |
| 批量下载 | ❌ 手动 | ✅ 一键批量 |
| 状态查询 | ❌ 无 | ✅ 实时状态 |

## 📖 更多资源

- [Binance公共数据文档](https://data.binance.vision/)
- [项目主页](README.md)
- [示例代码](examples/)
- [问题反馈](issues)

---

**注意**: 请确保遵守Binance的使用条款和API限制。大量数据下载可能会受到频率限制。

