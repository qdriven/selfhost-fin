# 查询TimescaleDB中的数据
crytata timescaledb query \
  --symbol BTCUSDT \
  --interval 1h \
  --start-time "2024-06-01 00:00:00" \
  --end-time "2024-07-31 23:59:59" \
  --limit 10

# 检查CSV文件
ls -la data/btc_historical/