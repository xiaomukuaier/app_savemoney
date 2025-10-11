#!/usr/bin/env python3
"""
LangGraph工作流测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.langgraph_workflow import langgraph_service


async def test_langgraph_workflow():
    """测试LangGraph工作流"""
    print("=== LangGraph工作流测试 ===")

    # 测试用例
    test_cases = [
        "今天中午吃饭花了二十五块钱",
        "打车回家花了三十八块五",
        "买了一杯咖啡十八元",
        "超市购物消费六十七元",
        "看电影花了四十五块钱"
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")

        try:
            result = await langgraph_service.process_expense(text)
            print(f"  结果: {result}")

            # 验证必要字段
            required_fields = ['amount', 'category', 'description', 'payment_method', 'confidence']
            for field in required_fields:
                if field not in result:
                    print(f"  ❌ 缺少字段: {field}")
                else:
                    print(f"  ✅ {field}: {result[field]}")

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(test_langgraph_workflow())