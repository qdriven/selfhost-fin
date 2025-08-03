# 下载BTC现货6-7月K线数据
crytata historical download-klines \
  --trading-type spot \
  --symbols "BTCUSDT" \
  --intervals "1m,3m,5m,15m,1h,4h,1d" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --save-csv --save-timescaledb