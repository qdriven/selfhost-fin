#!/usr/bin/env python3

import binascii
import hashlib
import os

def create_password_verification_file(password="hummingbot2024"):
    """创建 Hummingbot 密码验证文件"""
    
    # 创建配置目录
    conf_dir = "./conf"
    os.makedirs(conf_dir, exist_ok=True)
    
    # 生成验证字符串（通常是一个简单的已知字符串）
    verification_word = "hummingbot"
    
    # 使用密码创建密钥（简化版本，实际 hummingbot 可能使用更复杂的方法）
    # 这里我们使用一个简单的方法来创建一个十六进制字符串
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # 创建一个简单的"加密"验证字符串
    # 实际上这是一个简化的实现，真正的实现可能更复杂
    verification_hash = hashlib.sha256((verification_word + password_hash).encode()).hexdigest()
    
    # 写入密码验证文件
    password_file_path = os.path.join(conf_dir, ".password_verification")
    with open(password_file_path, "w") as f:
        f.write(verification_hash)
    
    print(f"✅ 密码验证文件已创建: {password_file_path}")
    print(f"使用的密码: {password}")
    
    return password_file_path

if __name__ == "__main__":
    create_password_verification_file() 