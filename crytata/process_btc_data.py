#!/usr/bin/env python3
"""
处理下载的BTC数据，为CSV文件添加header
"""

import os
import zipfile
import pandas as pd
import glob
from pathlib import Path

def process_csv_with_header(zip_file_path, output_dir):
    """处理ZIP文件中的CSV，添加header并保存"""
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 提取ZIP文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                print(f"ZIP文件中没有CSV文件: {zip_file_path}")
                return None
            
            csv_filename = csv_files[0]
            zip_ref.extract(csv_filename, output_dir)
            csv_path = os.path.join(output_dir, csv_filename)
            
            # 读取CSV数据
            df = pd.read_csv(csv_path, header=None)
            
            # 根据文件类型添加header
            if 'klines' in zip_file_path:
                # K线数据格式: [timestamp, open, high, low, close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore]
                df.columns = [
                    'timestamp', 'open', 'high', 'low', 'close', 'volume', 
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
                    'taker_buy_quote', 'ignore'
                ]
            elif 'trades' in zip_file_path:
                # 交易数据格式: [id, price, qty, quoteQty, time, isBuyerMaker, isBestMatch]
                df.columns = [
                    'id', 'price', 'qty', 'quoteQty', 'time', 
                    'isBuyerMaker', 'isBestMatch'
                ]
            elif 'aggTrades' in zip_file_path:
                # 聚合交易数据格式: [a, p, q, f, l, T, m, M]
                df.columns = [
                    'agg_trade_id', 'price', 'quantity', 'first_trade_id', 
                    'last_trade_id', 'timestamp', 'is_buyer_maker', 'is_best_match'
                ]
            
            # 保存带header的CSV
            output_filename = f"processed_{os.path.basename(csv_filename)}"
            output_path = os.path.join(output_dir, output_filename)
            df.to_csv(output_path, index=False)
            
            # 清理临时文件
            os.remove(csv_path)
            
            print(f"✅ 已处理: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"❌ 处理失败 {zip_file_path}: {e}")
        return None

def process_btc_data(data_dir):
    """处理BTC数据目录中的所有ZIP文件"""
    print("🔄 开始处理BTC数据...")
    
    # 查找所有ZIP文件
    zip_files = glob.glob(os.path.join(data_dir, "**/*.zip"), recursive=True)
    
    if not zip_files:
        print(f"❌ 在目录 {data_dir} 中没有找到ZIP文件")
        return
    
    print(f"📁 找到 {len(zip_files)} 个ZIP文件")
    
    processed_files = []
    
    for zip_file in zip_files:
        # 确定输出目录
        relative_path = os.path.relpath(zip_file, data_dir)
        output_dir = os.path.join(data_dir, "processed", os.path.dirname(relative_path))
        
        # 处理文件
        result = process_csv_with_header(zip_file, output_dir)
        if result:
            processed_files.append(result)
    
    print(f"\n✅ 处理完成！共处理了 {len(processed_files)} 个文件")
    print(f"📁 处理后的文件保存在: {os.path.join(data_dir, 'processed')}")
    
    # 显示文件结构
    print("\n📋 处理后的文件结构:")
    processed_dir = os.path.join(data_dir, "processed")
    if os.path.exists(processed_dir):
        for root, dirs, files in os.walk(processed_dir):
            level = root.replace(processed_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.csv'):
                    print(f"{subindent}{file}")

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # 默认数据目录
        data_dir = "data/btc_2024_06_07"
    
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        print("请先运行下载脚本获取数据")
        return
    
    process_btc_data(data_dir)

if __name__ == "__main__":
    main() 