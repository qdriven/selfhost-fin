#!/usr/bin/env python3
"""
简单的BTC数据下载脚本，确保CSV文件包含header信息
"""

import os
import sys
import zipfile
import pandas as pd
from datetime import datetime
import urllib.request
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def download_and_extract_csv(base_url, file_path, output_dir):
    """下载ZIP文件并提取CSV"""
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 下载文件
        print(f"下载: {base_url}")
        response = urllib.request.urlopen(base_url)
        
        # 保存ZIP文件
        zip_path = os.path.join(output_dir, os.path.basename(file_path))
        with open(zip_path, 'wb') as f:
            f.write(response.read())
        
        # 提取CSV文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if csv_files:
                csv_filename = csv_files[0]
                zip_ref.extract(csv_filename, output_dir)
                csv_path = os.path.join(output_dir, csv_filename)
                
                # 读取CSV并添加header
                df = pd.read_csv(csv_path, header=None)
                
                # 添加列名
                if 'klines' in file_path:
                    # K线数据格式: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
                    df.columns = [
                        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
                        'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
                        'taker_buy_quote', 'ignore'
                    ]
                elif 'trades' in file_path:
                    # 交易数据格式: [id, price, qty, quoteQty, time, isBuyerMaker, isBestMatch]
                    df.columns = [
                        'id', 'price', 'qty', 'quoteQty', 'time', 
                        'isBuyerMaker', 'isBestMatch'
                    ]
                
                # 保存带header的CSV
                output_csv = os.path.join(output_dir, f"processed_{os.path.basename(csv_filename)}")
                df.to_csv(output_csv, index=False)
                print(f"已处理: {output_csv}")
                
                # 清理临时文件
                os.remove(csv_path)
                os.remove(zip_path)
                
                return output_csv
        
        return None
        
    except Exception as e:
        print(f"下载失败 {base_url}: {e}")
        return None

def download_btc_data():
    """下载BTC 6-7月数据"""
    base_url = "https://data.binance.vision/"
    
    # 创建输出目录
    output_base = "data/btc_csv_with_headers"
    os.makedirs(output_base, exist_ok=True)
    
    # 定义要下载的数据
    data_configs = [
        # 现货K线数据
        {
            'type': 'spot',
            'data_type': 'klines',
            'symbol': 'BTCUSDT',
            'intervals': ['1m', '3m', '5m', '15m', '1h', '4h', '1d'],
            'months': ['06', '07'],
            'year': '2024'
        },
        # 期货K线数据
        {
            'type': 'um',
            'data_type': 'klines',
            'symbol': 'BTCUSDT',
            'intervals': ['1m', '3m', '5m', '15m', '1h', '4h', '1d'],
            'months': ['06', '07'],
            'year': '2024'
        },
        # 现货交易数据
        {
            'type': 'spot',
            'data_type': 'trades',
            'symbol': 'BTCUSDT',
            'intervals': None,
            'months': ['06', '07'],
            'year': '2024'
        },
        # 期货交易数据
        {
            'type': 'um',
            'data_type': 'trades',
            'symbol': 'BTCUSDT',
            'intervals': None,
            'months': ['06', '07'],
            'year': '2024'
        }
    ]
    
    downloaded_files = []
    
    for config in data_configs:
        trading_type = config['type']
        data_type = config['data_type']
        symbol = config['symbol']
        intervals = config['intervals']
        months = config['months']
        year = config['year']
        
        # 设置路径
        if trading_type == 'spot':
            path_prefix = f"data/spot/monthly/{data_type}/{symbol}"
        else:
            path_prefix = f"data/futures/{trading_type}/monthly/{data_type}/{symbol}"
        
        if intervals:
            # K线数据
            for interval in intervals:
                for month in months:
                    file_path = f"{path_prefix}/{interval}/{symbol}-{interval}-{year}-{month}.zip"
                    output_dir = os.path.join(output_base, trading_type, data_type, interval)
                    
                    full_url = base_url + file_path
                    result = download_and_extract_csv(full_url, file_path, output_dir)
                    if result:
                        downloaded_files.append(result)
        else:
            # 交易数据
            for month in months:
                file_path = f"{path_prefix}/{symbol}-trades-{year}-{month}.zip"
                output_dir = os.path.join(output_base, trading_type, data_type)
                
                full_url = base_url + file_path
                result = download_and_extract_csv(full_url, file_path, output_dir)
                if result:
                    downloaded_files.append(result)
    
    print(f"\n✅ 下载完成！共下载了 {len(downloaded_files)} 个文件")
    print(f"📁 文件保存在: {output_base}")
    
    # 显示文件结构
    print("\n📋 文件结构:")
    for root, dirs, files in os.walk(output_base):
        level = root.replace(output_base, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.csv'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    print("🚀 开始下载BTC 6-7月数据（带header的CSV）...")
    download_btc_data() 