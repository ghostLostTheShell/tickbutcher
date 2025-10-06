#!/usr/bin/env python3
"""
演示交易对异常处理功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tickbutcher.brokers.trading_pair import TradingPair


def demo_basic_functionality():
    """演示基本功能"""
    print("=== 基本功能演示 ===")
    
    # 基本获取
    pair = TradingPair.get_trading_pair("BTCUSDT")
    print(f"获取交易对: {pair.symbol} (ID: {pair.id})")
    
    # 检查存在性
    exists = TradingPair.exists("BTCUSDT")
    print(f"BTCUSDT 存在: {exists}")
    
    exists = TradingPair.exists("INVALID")
    print(f"INVALID 存在: {exists}")


def demo_special_symbols():
    """演示特殊符号处理"""
    print("\n=== 特殊符号处理演示 ===")
    
    test_cases = [
        "BTC/USDT",      # 斜杠分隔
        "BTC-USDT",      # 连字符分隔
        "BTC_USDT",      # 下划线分隔
        "BTC USDT",      # 空格分隔
        "btcusdt",       # 小写
        "  BTCUSDT  ",   # 带空格
    ]
    
    for test_input in test_cases:
        try:
            pair = TradingPair.get_trading_pair(test_input)
            print(f"输入: '{test_input}' -> 交易对: {pair.id}")
        except Exception as e:
            print(f"输入: '{test_input}' -> 错误: {e}")


def demo_perpetual_contracts():
    """演示永续合约符号处理"""
    print("\n=== 永续合约符号处理演示 ===")
    
    perp_cases = [
        "BTC/USDT@P",
        "BTCUSDT-PERP", 
        "BTCUSDT_PERP",
        "btcusdt-perpetual",
    ]
    
    for test_input in perp_cases:
        try:
            pair = TradingPair.get_trading_pair(test_input)
            print(f"输入: '{test_input}' -> 交易对: {pair.id}")
        except Exception as e:
            print(f"输入: '{test_input}' -> 错误: {e}")


def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理演示 ===")
    
    error_cases = [
        ("", "空字符串"),
        ("   ", "空白字符串"),
        ("INVALID_PAIR", "不存在的交易对"),
        ("XYZ123", "无效交易对"),
    ]
    
    for test_input, description in error_cases:
        try:
            pair = TradingPair.get_trading_pair(test_input)
            print(f"{description}: {pair.id}")
        except Exception as e:
            print(f"{description} -> 错误: {type(e).__name__}: {e}")


def demo_utility_methods():
    """演示工具方法"""
    print("\n=== 工具方法演示 ===")
    
    # 获取所有交易对
    all_pairs = TradingPair.get_all_trading_pairs()
    print(f"所有交易对数量: {len(all_pairs)}")
    
    # 获取所有ID
    all_ids = TradingPair.get_trading_pair_ids()
    print(f"所有交易对ID: {', '.join(all_ids)}")
    
    # 测试normalize参数
    print("\n使用normalize=False:")
    try:
        pair = TradingPair.get_trading_pair("BTCUSDT", normalize=False)
        print(f"精确匹配成功: {pair.id}")
    except Exception as e:
        print(f"精确匹配失败: {e}")
    
    try:
        pair = TradingPair.get_trading_pair("BTC/USDT", normalize=False)
        print(f"特殊符号匹配成功: {pair.id}")
    except Exception as e:
        print(f"特殊符号匹配失败: {e}")


if __name__ == "__main__":
    print("交易对异常处理功能演示")
    print("=" * 50)
    
    demo_basic_functionality()
    demo_special_symbols()
    demo_perpetual_contracts()
    demo_error_handling()
    demo_utility_methods()
    
    print("\n演示完成!")