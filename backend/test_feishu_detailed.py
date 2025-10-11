#!/usr/bin/env python3
"""
飞书API详细诊断测试脚本
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

from app.services.feishu_api import feishu_service
import lark_oapi.api.bitable.v1 as bitable_v1


async def test_feishu_detailed():
    """详细测试飞书API集成"""
    print("=== 飞书API详细诊断测试 ===")

    # 检查配置
    print(f"飞书API配置状态: {feishu_service.is_configured}")
    print(f"App ID: {feishu_service.app_id}")
    print(f"Table ID: {feishu_service.table_id}")

    if not feishu_service.is_configured:
        print("飞书API未配置，无法继续测试")
        return

    # 测试1: 获取表格列表
    print("\n1. 测试获取表格列表...")
    try:
        request = (bitable_v1.ListAppTableRequest.builder()
            .app_token(feishu_service.table_id)
            .build())

        response = feishu_service.client.bitable.v1.app_table.list(request)

        if response.success():
            tables = response.data.items
            print(f"   获取到 {len(tables)} 个表格")
            for table in tables:
                print(f"     - {table.name} (ID: {table.table_id})")
        else:
            print(f"   获取表格列表失败: {response.msg}")
            print(f"   错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")

    except Exception as e:
        print(f"   获取表格列表异常: {e}")

    # 测试2: 获取记录列表
    print("\n2. 测试获取记录列表...")
    try:
        request = (bitable_v1.ListAppTableRecordRequest.builder()
            .app_token(feishu_service.table_id)
            .table_id("tblExpenses")  # 假设的表格名
            .page_size(5)
            .build())

        response = feishu_service.client.bitable.v1.app_table_record.list(request)

        if response.success():
            records = response.data.items
            print(f"   获取到 {len(records)} 条记录")
        else:
            print(f"   获取记录列表失败: {response.msg}")
            print(f"   错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")

    except Exception as e:
        print(f"   获取记录列表异常: {e}")

    # 测试3: 测试保存数据
    print("\n3. 测试保存记账数据...")
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

    try:
        save_success = feishu_service.save_expense_to_table(test_expense_data)
        print(f"   保存状态: {'✅ 成功' if save_success else '❌ 失败'}")
    except Exception as e:
        print(f"   保存数据异常: {e}")

    print("\n=== 飞书API详细诊断测试完成 ===")


if __name__ == "__main__":
    asyncio.run(test_feishu_detailed())