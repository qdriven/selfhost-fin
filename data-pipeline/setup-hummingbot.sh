#!/bin/bash

# OKX 连接器设置脚本
# 此脚本帮助用户配置OKX API密钥

set -e

echo "=== Hummingbot OKX 连接器设置 ==="
echo ""

# 检查是否提供了环境变量
if [[ -n "$OKX_API_KEY" && -n "$OKX_SECRET_KEY" && -n "$OKX_PASSPHRASE" ]]; then
    echo "检测到环境变量中的OKX配置，使用环境变量设置..."
    API_KEY="$OKX_API_KEY"
    SECRET_KEY="$OKX_SECRET_KEY"
    PASSPHRASE="$OKX_PASSPHRASE"
    SUBDOMAIN="${OKX_SUBDOMAIN:-www}"
else
    echo "请输入您的OKX API信息："
    echo ""
    
    read -p "OKX API Key: " API_KEY
    read -s -p "OKX Secret Key: " SECRET_KEY
    echo ""
    read -s -p "OKX Passphrase: " PASSPHRASE
    echo ""
    
    echo "请选择您注册API密钥的子域名："
    echo "1) www (默认，大多数用户)"
    echo "2) app (美国用户)"
    echo "3) my (欧洲经济区用户)"
    read -p "请选择 [1-3]: " subdomain_choice
    
    case $subdomain_choice in
        1) SUBDOMAIN="www" ;;
        2) SUBDOMAIN="app" ;;
        3) SUBDOMAIN="my" ;;
        *) SUBDOMAIN="www" ;;
    esac
fi

echo ""
echo "配置信息："
echo "API Key: ${API_KEY:0:8}..."
echo "Subdomain: $SUBDOMAIN"
echo ""

# 创建配置目录
mkdir -p ./conf/connectors

# 创建OKX配置文件
cat > ./conf/connectors/okx.yml << EOF
connector: okx
okx_api_key: "${API_KEY}"
okx_secret_key: "${SECRET_KEY}"
okx_passphrase: "${PASSPHRASE}"
okx_registration_sub_domain: "${SUBDOMAIN}"
EOF

# 创建OKX永续合约配置文件
cat > ./conf/connectors/okx_perpetual.yml << EOF
connector: okx_perpetual
okx_perpetual_api_key: "${API_KEY}"
okx_perpetual_secret_key: "${SECRET_KEY}"
okx_perpetual_passphrase: "${PASSPHRASE}"
EOF

echo "✅ OKX配置文件已创建:"
echo "   - ./conf/connectors/okx.yml (现货交易)"
echo "   - ./conf/connectors/okx_perpetual.yml (永续合约)"
echo ""

echo "🔐 安全提示:"
echo "   - 配置文件包含敏感信息，请妥善保管"
echo "   - 建议为API密钥设置适当的权限（只读或交易权限）"
echo "   - 定期轮换API密钥以提高安全性"
echo ""

echo "🚀 下一步:"
echo "   1. 启动Docker Compose: docker-compose -f docker-compose-multi-db.yml up -d"
echo "   2. 连接到Hummingbot容器: docker exec -it hummingbot-postgresql-instance bash"
echo "   3. 运行Hummingbot: ./bin/hummingbot_quickstart.py"
echo "   4. 在Hummingbot中连接OKX: connect okx"
echo ""

echo "✅ OKX设置完成！" 