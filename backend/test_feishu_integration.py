#!/usr/bin/env python3
"""
飞书API集成测试脚本
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.feishu_api import get_feishu_service


async def test_feishu_integration():
    """测试飞书API集成"""
    print("=== 飞书API集成测试 ===")

    # 获取飞书服务实例
    feishu_service = get_feishu_service()

    # 测试配置状态
    print(f"飞书API配置状态: {feishu_service.is_configured}")
    if not feishu_service.is_configured:
        print("飞书API未配置，将在模拟模式下运行")

    # 测试连接
    print("\n1. 测试飞书API连接...")
    is_connected = feishu_service.test_connection()
    print(f"   连接状态: {'✅ 成功' if is_connected else '❌ 失败'}")

    # 测试保存记账数据
    print("\n2. 测试保存记账数据...")
    test_expense_data = {
        "amount": 25.0,
        "category": "餐饮",
        "subcategory": "午餐",
        "description": "今天中午吃饭",
        "date": "2024-01-15",
        "type": "expense",
        "payment_method": "微信支付",
        "confidence": 0.9,
        "raw_text": "今天中午吃饭花了二十五块钱"
    }

    save_success = feishu_service.save_expense_to_table(test_expense_data)
    print(f"   保存状态: {'✅ 成功' if save_success else '❌ 失败'}")

    # 测试获取记录（如果配置了飞书API）
    if feishu_service.is_configured and is_connected:
        print("\n3. 测试获取记账记录...")
        records = feishu_service.get_expense_records(limit=5)
        if records:
            print(f"   获取到 {len(records)} 条记录")
            for i, record in enumerate(records[:3], 1):
                print(f"     记录 {i}: {record.get('fields', {})}")
        else:
            print("   获取记录失败")

    print("\n=== 飞书API集成测试完成 ===")


if __name__ == "__main__":
    asyncio.run(test_feishu_integration())