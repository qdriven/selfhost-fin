# 下载BTC现货交易数据
crytata historical download-trades \
  --trading-type spot \
  --symbols "BTCUSDT" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --save-csv

# 下载BTC期货交易数据  
crytata historical download-trades \
  --trading-type um \
  --symbols "BTCUSDT" \
  --start-date "2024-06-01" \
  --end-date "2024-07-31" \
  --save-csv