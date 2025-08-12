#!/bin/bash

# 统一的BTC数据下载脚本
# 使用新的bn包进行下载，支持代理和断点续传

set -e

# 默认参数
TRADING_TYPE=${1:-spot}
DATA_TYPE=${2:-klines}
START_DATE=${3:-"2024-06-01"}
END_DATE=${4:-"2024-07-31"}
OUTPUT_DIR=${5:-"data/btc_${TRADING_TYPE}_${DATA_TYPE}"}
PROXY=${6:-""}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo -e "${BLUE}统一的BTC数据下载脚本${NC}"
    echo "=========================="
    echo ""
    echo "用法: $0 [trading_type] [data_type] [start_date] [end_date] [output_dir] [proxy]"
    echo ""
    echo "参数说明:"
    echo "  trading_type: 交易类型 (spot|um|cm) [默认: spot]"
    echo "  data_type:    数据类型 (klines|trades|aggTrades|markPriceKlines|indexPriceKlines|premiumIndexKlines) [默认: klines]"
    echo "  start_date:   开始日期 (YYYY-MM-DD) [默认: 2024-06-01]"
    echo "  end_date:     结束日期 (YYYY-MM-DD) [默认: 2024-07-31]"
    echo "  output_dir:   输出目录 [默认: data/btc_{trading_type}_{data_type}]"
    echo "  proxy:        代理地址 (http://proxy:port) [可选]"
    echo ""
    echo "示例:"
    echo "  $0                                    # 下载现货K线数据 (6-7月)"
    echo "  $0 um klines                          # 下载U本位期货K线数据"
    echo "  $0 spot trades 2024-01-01 2024-12-31 # 下载现货交易数据 (全年)"
    echo "  $0 um klines 2024-06-01 2024-07-31 data/futures http://proxy:8080"
    echo ""
    echo "支持的数据类型:"
    echo "  - klines: K线数据 (需要指定intervals)"
    echo "  - trades: 交易数据"
    echo "  - aggTrades: 聚合交易数据"
    echo "  - markPriceKlines: 标记价格K线 (仅期货)"
    echo "  - indexPriceKlines: 指数价格K线 (仅期货)"
    echo "  - premiumIndexKlines: 溢价指数K线 (仅期货)"
}

# 检查参数
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# 验证交易类型
case $TRADING_TYPE in
    "spot"|"um"|"cm")
        ;;
    *)
        echo -e "${RED}错误: 无效的交易类型 '$TRADING_TYPE'${NC}"
        echo "支持的交易类型: spot, um, cm"
        exit 1
        ;;
esac

# 验证数据类型
case $DATA_TYPE in
    "klines"|"trades"|"aggTrades"|"markPriceKlines"|"indexPriceKlines"|"premiumIndexKlines")
        ;;
    *)
        echo -e "${RED}错误: 无效的数据类型 '$DATA_TYPE'${NC}"
        echo "支持的数据类型: klines, trades, aggTrades, markPriceKlines, indexPriceKlines, premiumIndexKlines"
        exit 1
        ;;
esac

# 验证日期格式
if ! date -d "$START_DATE" >/dev/null 2>&1; then
    echo -e "${RED}错误: 无效的开始日期格式 '$START_DATE'${NC}"
    echo "请使用 YYYY-MM-DD 格式"
    exit 1
fi

if ! date -d "$END_DATE" >/dev/null 2>&1; then
    echo -e "${RED}错误: 无效的结束日期格式 '$END_DATE'${NC}"
    echo "请使用 YYYY-MM-DD 格式"
    exit 1
fi

# 检查bn命令是否可用
if ! command -v bn &> /dev/null; then
    echo -e "${RED}错误: 未找到 'bn' 命令${NC}"
    echo "请先安装bn包: pip install -e ."
    exit 1
fi

# 显示下载配置
echo -e "${BLUE}下载配置:${NC}"
echo "  交易类型: $TRADING_TYPE"
echo "  数据类型: $DATA_TYPE"
echo "  开始日期: $START_DATE"
echo "  结束日期: $END_DATE"
echo "  输出目录: $OUTPUT_DIR"
if [[ -n "$PROXY" ]]; then
    echo "  代理地址: $PROXY"
fi
echo ""

# 确认下载
read -p "确认开始下载? (y/n): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}下载已取消。${NC}"
    exit 0
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 构建bn命令
BN_CMD="bn download"
BN_CMD="$BN_CMD --trading-type $TRADING_TYPE"
BN_CMD="$BN_CMD --data-type $DATA_TYPE"
BN_CMD="$BN_CMD --start-date $START_DATE"
BN_CMD="$BN_CMD --end-date $END_DATE"
BN_CMD="$BN_CMD --output-dir $OUTPUT_DIR"

# 如果是K线数据，需要指定intervals
if [[ "$DATA_TYPE" == "klines" ]]; then
    BN_CMD="$BN_CMD --intervals 1m,3m,5m,15m,1h,4h,1d"
fi

# 如果是期货数据，需要指定symbols
if [[ "$TRADING_TYPE" != "spot" ]]; then
    BN_CMD="$BN_CMD --symbols BTCUSDT"
fi

# 添加代理配置
if [[ -n "$PROXY" ]]; then
    BN_CMD="$BN_CMD --proxy $PROXY"
fi

# 添加其他选项
BN_CMD="$BN_CMD --resume --max-retries 5 --timeout 60"

echo -e "${GREEN}开始下载...${NC}"
echo "执行命令: $BN_CMD"
echo ""

# 执行下载
if eval $BN_CMD; then
    echo ""
    echo -e "${GREEN}✅ 下载完成！${NC}"
    echo -e "数据已保存到: ${BLUE}$OUTPUT_DIR${NC}"
    echo ""
    echo -e "${BLUE}下载的文件:${NC}"
    ls -la "$OUTPUT_DIR"
else
    echo ""
    echo -e "${RED}❌ 下载失败！${NC}"
    echo "请检查错误信息并重试"
    exit 1
fi
