#!/usr/bin/env python3
"""
测试时间解析功能
验证GPT解析服务对相对时间描述的处理
"""

import os
import asyncio
from dotenv import load_dotenv
from app.services.gpt_parser import GPTParserService

# 加载环境变量
load_dotenv()


def test_time_parsing():
    """测试时间解析功能"""

    parser_service = GPTParserService()
    print(f"GPT Parser Client initialized: {parser_service.client is not None}")

    # 测试不同的时间描述
    test_cases = [
        "今天中午花了25块钱吃午饭",
        "昨天打车花了38块钱",
        "前天买水果花了28块",
        "上周三看电影花了45元",
        "上个礼拜天充话费100元",
        "买了一杯咖啡18块钱",  # 没有明确时间，应该使用今天
    ]

    print("\n=== 时间解析测试 ===")

    for test_text in test_cases:
        print(f"\n测试文本: {test_text}")

        try:
            result = parser_service.parse_expense_text_sync(test_text)

            print(f"  解析结果:")
            print(f"    金额: {result.get('amount')}")
            print(f"    分类: {result.get('category')}")
            print(f"    日期: {result.get('date')}")
            print(f"    置信度: {result.get('confidence')}")

            # 验证日期格式
            date = result.get('date', '')
            if date and len(date) == 10 and date[4] == '-' and date[7] == '-':
                print("    ✅ 日期格式正确")
            else:
                print("    ⚠️  日期格式可能有问题")

        except Exception as e:
            print(f"    ❌ 解析失败: {e}")


if __name__ == "__main__":
    test_time_parsing()