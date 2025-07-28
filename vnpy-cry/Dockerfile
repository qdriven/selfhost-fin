FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libc6-dev \
    libpq-dev \
    build-essential \
    curl \
    wget \
    git \
    cmake \
    pkg-config \
    libhdf5-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制项目文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen --no-cache

# 复制应用代码
COPY . .

# 设置环境变量 - 将 src 目录添加到 PYTHONPATH
ENV PYTHONPATH=/app/src:/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8080 8888

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动 Jupyter Notebook\n\
nohup uv run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=/app/notebooks &\n\
\n\
# 启动 VNPY Web Trader\n\
nohup uv run vnpy-web &\n\
\n\
# 启动主应用\n\
uv run vnpy-crypto\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"] 