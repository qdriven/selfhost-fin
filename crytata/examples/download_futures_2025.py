#!/usr/bin/env python3
"""
示例：下载2025年期货交易数据
演示如何使用bn包下载期货数据
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to Python path to import crytata modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crytata.bn.downloader import BinanceDataDownloader
from crytata.bn.models import DownloadConfig, TradingType, DataType, Interval

def download_futures_data(trading_type, data_type, symbols, start_date, end_date, 
                         output_dir, intervals=None, verbose=True):
    """下载期货数据"""
    print(f"📊 开始下载 {trading_type} {data_type} 数据")
    print(f"   交易对: {symbols}")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print(f"   输出目录: {output_dir}")
    if intervals:
        print(f"   K线间隔: {intervals}")
    print("-" * 40)
    
    try:
        # 创建下载配置
        config = DownloadConfig(
            trading_type=trading_type,
            data_type=data_type,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            intervals=intervals,
            verbose=verbose,
            resume=True,
            max_retries=5,
            timeout=60
        )
        
        # 创建下载器实例
        downloader = BinanceDataDownloader(config)
        
        # 开始下载
        result = downloader.download()
        
        if result.success:
            print(f"✅ {trading_type} {data_type} 数据下载成功!")
            print(f"   下载文件数: {result.files_downloaded}")
            print(f"   总大小: {result.total_size_mb:.2f} MB")
            print(f"   耗时: {result.duration_seconds:.2f} 秒")
        else:
            print(f"❌ {trading_type} {data_type} 数据下载失败!")
            if result.error:
                print(f"   错误信息: {result.error}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ 下载过程中发生错误: {e}")
        return False

def batch_download_futures(trading_type, symbols, start_date, end_date, output_dir, verbose=True):
    """批量下载期货数据"""
    print(f"📊 开始批量下载 {trading_type} 期货数据")
    print(f"   交易对: {symbols}")
    print(f"   时间范围: {start_date} 到 {end_date}")
    print(f"   输出目录: {output_dir}")
    print("-" * 40)
    
    try:
        # 创建下载配置
        config = DownloadConfig(
            trading_type=trading_type,
            data_type=DataType.KLINES,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            intervals=[Interval.ONE_MINUTE, Interval.THREE_MINUTES, Interval.FIVE_MINUTES, 
                     Interval.FIFTEEN_MINUTES, Interval.ONE_HOUR, Interval.FOUR_HOURS, Interval.ONE_DAY],
            verbose=verbose,
            resume=True,
            max_retries=5,
            timeout=60
        )
        
        # 创建下载器实例
        downloader = BinanceDataDownloader(config)
        
        # 开始下载
        result = downloader.download()
        
        if result.success:
            print(f"✅ {trading_type} 批量数据下载成功!")
            print(f"   下载文件数: {result.files_downloaded}")
            print(f"   总大小: {result.total_size_mb:.2f} MB")
            print(f"   耗时: {result.duration_seconds:.2f} 秒")
        else:
            print(f"❌ {trading_type} 批量数据下载失败!")
            if result.error:
                print(f"   错误信息: {result.error}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ 批量下载过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 2025年期货数据下载示例")
    print("=" * 50)
    
    # 示例1: 下载2025年U本位期货交易数据
    print("\n📊 示例1: 下载2025年U本位期货(um)交易数据")
    success = download_futures_data(
        trading_type=TradingType.UM,
        data_type=DataType.TRADES,
        symbols=["BTCUSDT"],
        start_date="2025-01-01",
        end_date="2025-06-30",
        output_dir="data/futures_2025_trades_um",
        verbose=True
    )
    
    if not success:
        print("❌ 示例1失败，跳过后续示例")
        return
    
    # 示例2: 下载2025年U本位期货K线数据
    print("\n📊 示例2: 下载2025年U本位期货(um)K线数据")
    success = download_futures_data(
        trading_type=TradingType.UM,
        data_type=DataType.KLINES,
        symbols=["BTCUSDT"],
        start_date="2025-01-01",
        end_date="2025-06-30",
        output_dir="data/futures_2025_klines_um",
        intervals=[Interval.ONE_MINUTE, Interval.ONE_HOUR, Interval.ONE_DAY],
        verbose=True
    )
    
    if not success:
        print("❌ 示例2失败，跳过后续示例")
        return
    
    # 示例3: 下载2025年币本位期货交易数据
    print("\n📊 示例3: 下载2025年币本位期货(cm)交易数据")
    success = download_futures_data(
        trading_type=TradingType.CM,
        data_type=DataType.TRADES,
        symbols=["BTCUSD"],
        start_date="2025-01-01",
        end_date="2025-06-30",
        output_dir="data/futures_2025_trades_cm",
        verbose=True
    )
    
    if not success:
        print("❌ 示例3失败")
        return
    
    # 示例4: 批量下载
    print("\n📊 示例4: 批量下载2025年期货数据")
    success = batch_download_futures(
        trading_type=TradingType.UM,
        symbols=["BTCUSDT"],
        start_date="2025-01-01",
        end_date="2025-06-30",
        output_dir="data/futures_2025_batch",
        verbose=True
    )
    
    if not success:
        print("❌ 示例4失败")
        return
    
    print("\n🎉 所有示例执行完成！")
    print("\n📁 下载的数据文件位置:")
    print("  - U本位期货交易数据: data/futures_2025_trades_um/")
    print("  - U本位期货K线数据: data/futures_2025_klines_um/")
    print("  - 币本位期货交易数据: data/futures_2025_trades_cm/")
    print("  - 批量下载数据: data/futures_2025_batch/")
    
    print("\n🔍 查看下载状态:")
    print("  # 在Python中检查下载进度")
    print("  from crytata.bn.downloader import BinanceDataDownloader")
    print("  downloader = BinanceDataDownloader()")
    print("  progress = downloader.load_progress()")
    
    print("\n📚 更多帮助:")
    print("  # 查看模型定义")
    print("  from crytata.bn.models import TradingType, DataType, Interval")
    print("  print(list(TradingType))")
    print("  print(list(DataType))")
    print("  print(list(Interval))")

if __name__ == "__main__":
    main()
