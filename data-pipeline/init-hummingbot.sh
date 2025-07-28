#!/bin/bash

echo "=== Hummingbot 初始化脚本 ==="
echo ""

# 检查是否已经有密码验证文件
if [ ! -f "./conf/.password_verification" ]; then
    echo "首次运行 Hummingbot，需要设置密码..."
    echo ""
    echo "🔧 启动 Hummingbot 进行初始设置..."
    echo "请按照提示设置密码（建议使用: hummingbot2024）"
    echo ""
    
    # 启动 hummingbot 容器进行初始设置
    docker-compose run --rm hummingbot /bin/bash -c "
        echo 'hummingbot2024' | python ./bin/hummingbot_quickstart.py --config-password hummingbot2024 || 
        python ./bin/hummingbot_quickstart.py --config-password hummingbot2024
    "
else
    echo "✅ 密码验证文件已存在"
fi

echo ""
echo "🚀 启动完整的 Hummingbot 环境..."
docker-compose up -d

echo ""
echo "✅ 初始化完成！"
echo ""
echo "📋 后续操作："
echo "1. 查看日志: docker-compose logs -f hummingbot-main"
echo "2. 进入容器: docker exec -it hummingbot-main bash"
echo "3. 运行 Hummingbot: ./bin/hummingbot_quickstart.py"
echo "" 