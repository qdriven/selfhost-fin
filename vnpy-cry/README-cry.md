# VNPY 加密货币交易系统

基于 VNPY 框架构建的加密货币交易系统，集成 TimescaleDB 时序数据库和 OKX 交易所接口。使用现代 Python 包管理工具 `uv` 进行依赖管理。

## 🚀 特性

- **VNPY 框架**: 基于业界领先的 VNPY 量化交易框架
- **TimescaleDB**: 时序数据库，专为交易数据优化
- **OKX 集成**: 原生支持 OKX 交易所 API
- **容器化部署**: 完整的 Docker Compose 部署方案
- **现代化工具**: 使用 uv 进行 Python 包管理
- **多服务架构**: 主应用、数据采集器、Web 界面分离
- **监控面板**: 集成 Grafana 监控和可视化

## 📋 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VNPY Trader   │    │ Data Collector  │    │   Web Trader    │
│   (主交易应用)    │    │   (数据采集)      │    │   (Web界面)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┬─────┴─────┬─────────────────┐
         │                 │           │                 │
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   TimescaleDB   │ │    Redis    │ │   OKX Gateway   │ │     Grafana     │
│   (时序数据库)    │ │   (缓存)     │ │   (交易接口)     │ │    (监控面板)    │
└─────────────────┘ └─────────────┘ └─────────────────┘ └─────────────────┘
```

## 🛠️ 环境要求

- Python 3.11+
- Docker & Docker Compose
- uv (Python 包管理器)
- 4GB+ RAM
- 20GB+ 磁盘空间

## 📦 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd vnpy-crypto-trader
```

### 2. 安装 uv (如果尚未安装)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 配置环境变量

```bash
cp config.env.template .env
# 编辑 .env 文件，配置你的 OKX API 密钥
vim .env
```

### 4. 使用 uv 安装依赖

```bash
# 安装主要依赖
uv sync

# 安装开发依赖
uv sync --group dev

# 安装 Jupyter 支持
uv sync --group jupyter
```

### 5. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 6. 访问服务

- **主应用**: 在容器中运行
- **Web 交易界面**: http://localhost:8080
- **Jupyter Lab**: http://localhost:8888
- **Grafana 监控**: http://localhost:3000 (admin/admin2024)

## 🔧 开发环境

### 本地开发

```bash
# 激活虚拟环境
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
uv sync --group dev --group jupyter

# 运行主应用
uv run vnpy-crypto

# 运行数据采集器
uv run vnpy-collector

# 运行 Web 界面
uv run vnpy-web

# 或者使用 scripts（兼容性）
uv run python scripts/main.py
uv run python scripts/data_collector.py
uv run python scripts/start_webtrader.py
```

### 代码质量工具

```bash
# 代码格式化
uv run black .

# 导入排序
uv run isort .

# 代码检查
uv run flake8 .

# 类型检查
uv run mypy .

# 运行测试
uv run pytest
```

## 🗄️ 数据库配置

### TimescaleDB 表结构

- `bar_data`: K线数据 (超表)
- `tick_data`: 逐笔数据 (超表)
- `orders`: 订单数据
- `trades`: 成交数据
- `positions`: 持仓数据
- `accounts`: 账户数据
- `strategies`: 策略配置
- `strategy_logs`: 策略日志 (超表)

### 数据保留策略

- Tick 数据: 3个月
- 分钟级 Bar 数据: 1年
- 策略日志: 6个月

## 🔑 OKX API 配置

1. 登录 OKX 账户
2. 进入 API 管理页面
3. 创建新的 API 密钥
4. 设置权限: 读取、交易
5. 将密钥信息填入 `.env` 文件

### API 权限说明

- **读取权限**: 获取账户信息、市场数据
- **交易权限**: 下单、撤单、查询订单
- **提现权限**: 不建议开启

## 📊 监控和日志

### 日志文件

- `logs/vnpy_main.log`: 主应用日志
- `logs/data_collector.log`: 数据采集日志
- `logs/webtrader.log`: Web 界面日志

### Grafana 仪表板

系统提供预配置的 Grafana 仪表板，监控:

- 交易数据统计
- 系统性能指标
- API 调用频率
- 错误率统计

## 🎯 策略开发

### 创建新策略

```python
from vnpy_ctastrategy import CtaTemplate, CtaEngine
from vnpy.trader.object import TickData, BarData

class MyStrategy(CtaTemplate):
    """示例策略"""
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    def __init__(self, cta_engine: CtaEngine, strategy_name: str, vt_symbol: str, setting: dict):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def on_tick(self, tick: TickData):
        """Tick数据推送"""
        pass
    
    def on_bar(self, bar: BarData):
        """Bar数据推送"""
        pass
```

### 策略模板

- CTA策略: 适用于趋势跟踪
- 套利策略: 适用于跨品种套利
- 做市策略: 适用于提供流动性

## 🔧 常用命令

```bash
# uv 包管理
uv add package_name          # 添加依赖
uv remove package_name       # 移除依赖
uv sync                      # 同步依赖
uv run command              # 运行命令

# 应用启动
uv run vnpy-crypto          # 启动主应用
uv run vnpy-collector       # 启动数据采集器
uv run vnpy-web             # 启动 Web 界面

# Docker 操作
docker-compose up -d         # 启动服务
docker-compose down          # 停止服务
docker-compose logs -f       # 查看日志
docker-compose restart      # 重启服务

# 数据库操作
docker exec -it vnpy-timescaledb psql -U vnpy -d vnpy_crypto
```

## 📝 配置说明

### 主要配置文件

- `pyproject.toml`: Python 项目配置和依赖管理
- `docker-compose.yml`: 容器编排配置
- `src/vnpy_cry/config/settings.py`: VNPY 主配置
- `config/database/postgresql.conf`: 数据库配置

### 项目结构

```
vnpy-cry/
├── src/
│   └── vnpy_cry/              # 主要应用包
│       ├── __init__.py
│       ├── core/              # 核心模块
│       │   ├── main.py        # 主应用
│       │   ├── data_collector.py  # 数据采集器
│       │   └── web_trader.py  # Web 交易界面
│       ├── config/            # 配置模块
│       │   └── settings.py    # 系统配置
│       ├── strategies/        # 交易策略
│       ├── utils/             # 工具函数
│       └── data/              # 数据处理
├── scripts/                   # 启动脚本（兼容性）
├── config/                    # 外部配置文件
├── database/                  # 数据库相关
├── logs/                      # 日志文件
└── docker-compose.yml
```

### 环境变量

所有敏感配置通过环境变量管理，支持:

- 数据库连接信息
- API 密钥
- 日志级别
- 服务端口

## 🚨 注意事项

1. **API 密钥安全**: 不要将真实 API 密钥提交到版本控制
2. **资金管理**: 建议先在模拟环境测试
3. **风险控制**: 设置合理的止损和仓位管理
4. **系统监控**: 关注系统资源使用情况
5. **数据备份**: 定期备份重要的策略和配置数据

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [VNPY 官方文档](https://vnpy.com)
- [TimescaleDB 文档](https://docs.timescale.com)
- [OKX API 文档](https://www.okx.com/docs-v5/)
- [uv 文档](https://docs.astral.sh/uv/)

---

**免责声明**: 本项目仅供学习和研究使用，使用者需自行承担交易风险。 