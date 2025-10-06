"""
测试交易对异常处理功能
"""

import unittest
from tickbutcher.brokers.trading_pair import TradingPair
from tickbutcher.products import common as common_financial


class TestTradingPairExceptions(unittest.TestCase):
    """测试交易对的异常处理和特殊符号支持"""
    
    def setUp(self):
        """设置测试环境"""
        # 无需清理实例字典，因为每个测试类都会重新加载模块
        
        # 创建测试用的交易对
        self.test_pair = TradingPair(
            base=common_financial.BTC,
            quote=common_financial.USDT,
            symbol="BTC/USDT",
            id="BTCUSDT",
            base_precision=8,
            quote_precision=8
        )
        
        # 创建永续合约交易对
        self.perp_pair = TradingPair(
            base=common_financial.BTCUSDT_P,
            quote=common_financial.USDT,
            symbol="BTC/USDT@P",
            id="BTCUSDTP",
            base_precision=8,
            quote_precision=8
        )
    
    def test_get_trading_pair_basic(self):
        """测试基本的获取交易对功能"""
        pair = TradingPair.get_trading_pair("BTCUSDT")
        self.assertEqual(pair.id, "BTCUSDT")
        self.assertEqual(pair.symbol, "BTC/USDT")
    
    def test_get_trading_pair_with_special_symbols(self):
        """测试特殊符号的处理"""
        # 测试各种格式的输入
        test_cases = [
            "BTC/USDT",      # 斜杠分隔
            "BTC-USDT",      # 连字符分隔
            "BTC_USDT",      # 下划线分隔  
            "BTC USDT",      # 空格分隔
            "btcusdt",       # 小写
            "BtcUsdt",       # 混合大小写
        ]
        
        for test_id in test_cases:
            with self.subTest(test_id=test_id):
                pair = TradingPair.get_trading_pair(test_id)
                self.assertEqual(pair.id, "BTCUSDT")
    
    def test_get_trading_pair_perpetual_symbols(self):
        """测试永续合约符号的处理"""
        test_cases = [
            "BTC/USDT@P",      # @P后缀
            "BTCUSDT-PERP",    # -PERP后缀
            "BTCUSDT_PERP",    # _PERP后缀
            "btcusdt-perpetual", # -PERPETUAL后缀（小写）
        ]
        
        for test_id in test_cases:
            with self.subTest(test_id=test_id):
                pair = TradingPair.get_trading_pair(test_id)
                self.assertEqual(pair.id, "BTCUSDTP")
    
    def test_get_trading_pair_type_error(self):
        """测试类型错误处理"""
        with self.assertRaises(TypeError) as cm:
            TradingPair.get_trading_pair(123)  # type: ignore
        
        self.assertIn("字符串类型", str(cm.exception))
    
    def test_get_trading_pair_empty_id(self):
        """测试空ID错误处理"""
        test_cases = ["", "   ", "\t", "\n"]
        
        for empty_id in test_cases:
            with self.subTest(empty_id=repr(empty_id)):
                with self.assertRaises(ValueError) as cm:
                    TradingPair.get_trading_pair(empty_id)
                
                self.assertIn("不能为空", str(cm.exception))
    
    def test_get_trading_pair_not_exist(self):
        """测试交易对不存在的错误处理"""
        with self.assertRaises(ValueError) as cm:
            TradingPair.get_trading_pair("INVALID_PAIR")
        
        exception_msg = str(cm.exception)
        self.assertIn("不存在", exception_msg)
        self.assertIn("可用的交易对", exception_msg)
    
    def test_get_trading_pair_no_normalize(self):
        """测试禁用标准化功能"""
        # 当normalize=False时，必须使用精确的ID
        pair = TradingPair.get_trading_pair("BTCUSDT", normalize=False)
        self.assertEqual(pair.id, "BTCUSDT")
        
        # 使用特殊符号时应该失败
        with self.assertRaises(ValueError):
            TradingPair.get_trading_pair("BTC/USDT", normalize=False)
    
    def test_normalize_trading_pair_id(self):
        """测试ID标准化函数"""
        test_cases = [
            ("BTC/USDT", "BTCUSDT"),
            ("btc-usdt", "BTCUSDT"),
            ("BTC_USDT", "BTCUSDT"),
            ("BTC USDT", "BTCUSDT"),
            ("BTC/USDT@P", "BTCUSDTP"),
            ("BTCUSDT-PERP", "BTCUSDTP"),
            ("btcusdt_perpetual", "BTCUSDTP"),
        ]
        
        for input_id, expected in test_cases:
            with self.subTest(input_id=input_id):
                # 通过get_trading_pair方法间接测试标准化功能
                pair = TradingPair.get_trading_pair(input_id)
                result = pair.id
                self.assertEqual(result, expected)
    
    def test_exists_method(self):
        """测试exists方法"""
        # 存在的交易对
        self.assertTrue(TradingPair.exists("BTCUSDT"))
        self.assertTrue(TradingPair.exists("BTC/USDT"))
        self.assertTrue(TradingPair.exists("btc-usdt"))
        
        # 不存在的交易对
        self.assertFalse(TradingPair.exists("INVALID"))
        self.assertFalse(TradingPair.exists("XYZ123"))
    
    def test_get_all_trading_pairs(self):
        """测试获取所有交易对"""
        all_pairs = TradingPair.get_all_trading_pairs()
        
        self.assertIsInstance(all_pairs, dict)
        self.assertIn("BTCUSDT", all_pairs)
        self.assertIn("BTCUSDTP", all_pairs)
        self.assertEqual(len(all_pairs), 2)
    
    def test_get_trading_pair_ids(self):
        """测试获取所有交易对ID"""
        ids = TradingPair.get_trading_pair_ids()
        
        self.assertIsInstance(ids, list)
        self.assertIn("BTCUSDT", ids)
        self.assertIn("BTCUSDTP", ids)
        self.assertEqual(len(ids), 2)
    
    def test_normalize_with_invalid_characters(self):
        """测试包含无效字符的ID标准化"""
        # 这些应该在移除分隔符后仍然有效
        valid_cases = ["BTC/USDT", "BTC-USDT", "BTC_USDT"]
        for case in valid_cases:
            try:
                # 通过get_trading_pair方法间接测试标准化功能
                TradingPair.get_trading_pair(case)
            except ValueError:
                self.fail(f"不应该抛出异常: {case}")
    
    def test_whitespace_handling(self):
        """测试空白符处理"""
        test_cases = [
            "  BTCUSDT  ",
            "\tBTCUSDT\t",
            "BTC USDT",
            " BTC / USDT ",
        ]
        
        for test_id in test_cases:
            with self.subTest(test_id=repr(test_id)):
                pair = TradingPair.get_trading_pair(test_id)
                self.assertEqual(pair.id, "BTCUSDT")


if __name__ == "__main__":
    unittest.main()