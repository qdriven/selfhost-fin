# 检查Docker是否安装
docker --version
docker-compose --version

# 检查关键端口是否被占用
lsof -i :5432  # TimescaleDB
lsof -i :6379  # Redis  
lsof -i :3000  # Grafana
lsof -i :8002  # Analytics API

# 如果有占用，请先停止相关服务

