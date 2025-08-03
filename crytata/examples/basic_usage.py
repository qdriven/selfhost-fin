#!/usr/bin/env python3
"""
Crytata 基本使用示例

这个脚本演示了如何使用 Crytata 进行基本的数据收集和处理操作。
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.crytata import (
    BinanceDataCollector,
    DataProcessor,
    DataStorage,
    BinanceHistoricalDownloader,
    TimescaleDBConfig,
    TimescaleDBStorage
)


def example_real_time_data_collection():
    """示例：实时数据收集"""
    print("=== 实时数据收集示例 ===")
    
    # 初始化数据收集器
    collector = BinanceDataCollector()
    
    # 收集 BTCUSDT 的 1小时 K线数据
    print("收集 BTCUSDT 1小时 K线数据...")
    klines = collector.get_klines('BTCUSDT', '1h', limit=100)
    
    if klines:
        print(f"收集到 {len(klines)} 条 K线数据")
        
        # 显示最新的几条数据
        for kline in klines[:3]:
            print(f"  {kline.open_time}: O={kline.open_price:.2f}, H={kline.high_price:.2f}, "
                  f"L={kline.low_price:.2f}, C={kline.close_price:.2f}, V={kline.volume:.2f}")
        
        # 保存到 CSV
        storage = DataStorage(csv_dir='data')
        csv_file = storage.save_klines_csv(klines)
        print(f"数据已保存到: {csv_file}")
    
    # 收集交易数据
    print("\n收集 BTCUSDT 交易数据...")
    trades = collector.get_recent_trades('BTCUSDT', limit=50)
    
    if trades:
        print(f"收集到 {len(trades)} 条交易数据")
        
        # 显示最新的几条交易
        for trade in trades[:3]:
            print(f"  {trade.time}: 价格={trade.price:.2f}, 数量={trade.quantity:.6f}, "
                  f"买方挂单={trade.is_buyer_maker}")
    
    # 收集行情数据
    print("\n收集 BTCUSDT 行情数据...")
    ticker = collector.get_24hr_ticker('BTCUSDT')
    
    if ticker:
        print(f"最新价格: {ticker.last_price:.2f}")
        print(f"24小时涨跌: {ticker.price_change_percent:.2f}%")
        print(f"24小时成交量: {ticker.volume:.2f}")
        print(f"24小时最高: {ticker.high_price:.2f}")
        print(f"24小时最低: {ticker.low_price:.2f}")


def example_historical_data_download():
    """示例：历史数据下载"""
    print("\n=== 历史数据下载示例 ===")
    
    # 初始化历史数据下载器
    downloader = BinanceHistoricalDownloader(download_dir='downloads')
    
    # 下载 BTCUSDT 最近 7 天的 1小时数据
    print("下载 BTCUSDT 最近 7 天的 1小时数据...")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    all_klines = downloader.download_and_process_klines(
        trading_type='spot',
        symbols=['BTCUSDT'],
        intervals=['1h'],
        start_date=start_date,
        end_date=end_date
    )
    
    if all_klines:
        for symbol, klines in all_klines.items():
            print(f"{symbol}: 下载了 {len(klines)} 条 K线数据")
            
            # 保存到 CSV
            storage = DataStorage(csv_dir='data')
            csv_file = storage.save_klines_csv(klines)
            print(f"数据已保存到: {csv_file}")


def example_data_processing():
    """示例：数据处理和技术指标计算"""
    print("\n=== 数据处理示例 ===")
    
    # 收集一些数据
    collector = BinanceDataCollector()
    klines = collector.get_klines('BTCUSDT', '1h', limit=200)
    
    if klines:
        # 转换为 DataFrame
        df = DataProcessor.klines_to_dataframe(klines)
        print(f"原始数据形状: {df.shape}")
        
        # 计算技术指标
        df_with_indicators = DataProcessor.calculate_technical_indicators(df)
        print(f"添加技术指标后数据形状: {df_with_indicators.shape}")
        
        # 显示技术指标列
        indicator_columns = [col for col in df_with_indicators.columns if col not in df.columns]
        print(f"添加的技术指标: {indicator_columns}")
        
        # 显示最新的技术指标值
        latest = df_with_indicators.iloc[-1]
        print(f"\n最新技术指标值:")
        print(f"  SMA(20): {latest.get('sma_20', 'N/A'):.2f}")
        print(f"  EMA(12): {latest.get('ema_12', 'N/A'):.2f}")
        print(f"  RSI: {latest.get('rsi', 'N/A'):.2f}")
        print(f"  MACD: {latest.get('macd', 'N/A'):.2f}")
        
        # 保存处理后的数据
        storage = DataStorage(csv_dir='data')
        processed_file = os.path.join('data', 'BTCUSDT_1h_with_indicators.csv')
        df_with_indicators.to_csv(processed_file)
        print(f"处理后的数据已保存到: {processed_file}")


def example_timescaledb_storage():
    """示例：TimescaleDB 存储"""
    print("\n=== TimescaleDB 存储示例 ===")
    
    try:
        # 初始化 TimescaleDB 配置
        config = TimescaleDBConfig(
            host='localhost',
            port=5432,
            database='crytata',
            username='crytata',
            password='crytata_password'
        )
        
        # 创建存储管理器
        storage = TimescaleDBStorage(config)
        
        if storage.connected:
            print("成功连接到 TimescaleDB")
            
            # 收集一些数据
            collector = BinanceDataCollector()
            klines = collector.get_klines('BTCUSDT', '1h', limit=100)
            
            if klines:
                # 保存到 TimescaleDB
                if storage.save_klines(klines):
                    print(f"成功保存 {len(klines)} 条 K线数据到 TimescaleDB")
                
                # 查询数据
                queried_klines = storage.query_klines('BTCUSDT', '1h', limit=10)
                print(f"从 TimescaleDB 查询到 {len(queried_klines)} 条数据")
                
                # 显示查询结果
                for kline in queried_klines[:3]:
                    print(f"  {kline.open_time}: C={kline.close_price:.2f}, V={kline.volume:.2f}")
        else:
            print("无法连接到 TimescaleDB，请确保服务正在运行")
            
    except Exception as e:
        print(f"TimescaleDB 操作失败: {e}")
        print("请确保 TimescaleDB 服务正在运行，可以使用以下命令启动:")
        print("  docker-compose up -d")


def example_symbol_discovery():
    """示例：发现可用的交易对"""
    print("\n=== 交易对发现示例 ===")
    
    # 初始化下载器
    downloader = BinanceHistoricalDownloader()
    
    # 获取所有现货交易对
    print("获取所有现货交易对...")
    spot_symbols = downloader.get_all_symbols('spot')
    
    if spot_symbols:
        print(f"找到 {len(spot_symbols)} 个现货交易对")
        
        # 显示前 10 个交易对
        print("前 10 个交易对:")
        for symbol in spot_symbols[:10]:
            print(f"  {symbol}")
        
        # 过滤 USDT 交易对
        usdt_symbols = [s for s in spot_symbols if s.endswith('USDT')]
        print(f"\nUSDT 交易对数量: {len(usdt_symbols)}")
        
        # 显示前 5 个 USDT 交易对
        print("前 5 个 USDT 交易对:")
        for symbol in usdt_symbols[:5]:
            print(f"  {symbol}")


def main():
    """主函数"""
    print("Crytata 基本使用示例")
    print("=" * 50)
    
    # 创建数据目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    
    try:
        # 运行各个示例
        example_real_time_data_collection()
        example_historical_data_download()
        example_data_processing()
        example_timescaledb_storage()
        example_symbol_discovery()
        
        print("\n" + "=" * 50)
        print("所有示例执行完成！")
        print("\n生成的文件:")
        print("  - data/: 处理后的 CSV 文件")
        print("  - downloads/: 下载的原始数据")
        
    except KeyboardInterrupt:
        print("\n用户中断执行")
    except Exception as e:
        print(f"\n执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main() 