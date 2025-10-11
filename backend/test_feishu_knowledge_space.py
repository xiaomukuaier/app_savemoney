#!/usr/bin/env python3
"""
飞书知识空间节点API测试脚本
测试从知识空间节点访问多维表格
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.feishu_api import feishu_service
import lark_oapi.api.bitable.v1 as bitable_v1
import lark_oapi.api.wiki.v2 as wiki_v2


def test_knowledge_space_access():
    """测试知识空间节点访问"""
    print("=== 飞书知识空间节点访问测试 ===")

    # 检查配置
    print(f"飞书API配置状态: {feishu_service.is_configured}")
    print(f"App ID: {feishu_service.app_id}")
    print(f"Table ID: {feishu_service.table_id}")
    print(f"Node Token: {feishu_service.node_token}")
    print(f"Space ID: {feishu_service.space_id}")

    if not feishu_service.is_configured:
        print("飞书API未配置，无法继续测试")
        return

    # 测试1: 检查知识空间节点配置
    print("\n1. 检查知识空间节点配置...")
    if feishu_service.node_token:
        print(f"   ✅ 已配置节点token: {feishu_service.node_token}")
    else:
        print("   ℹ️ 未配置节点token，将使用table_id作为app_token")

    # 测试2: 获取app_token
    print("\n2. 测试获取app_token...")
    try:
        app_token = feishu_service._get_app_token()
        if app_token:
            print(f"   ✅ 获取到app_token: {app_token}")
        else:
            print("   ❌ 无法获取app_token")
    except Exception as e:
        print(f"   ❌ 获取app_token异常: {e}")

    # 测试3: 测试连接
    print("\n3. 测试飞书API连接...")
    is_connected = feishu_service.test_connection()
    print(f"   连接状态: {'✅ 成功' if is_connected else '❌ 失败'}")

    # 测试4: 获取表格列表
    print("\n4. 测试获取表格列表...")
    try:
        app_token = feishu_service._get_app_token()
        if app_token:
            request = (bitable_v1.ListAppTableRequest.builder()
                .app_token(app_token)
                .build())

            response = feishu_service.client.bitable.v1.app_table.list(request)

            if response.success():
                tables = response.data.items
                print(f"   ✅ 获取到 {len(tables)} 个表格")
                for table in tables:
                    print(f"     - {table.name} (ID: {table.table_id})")
            else:
                print(f"   ❌ 获取表格列表失败: {response.msg}")
                print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
        else:
            print("   ❌ 无法获取app_token，跳过表格列表测试")
    except Exception as e:
        print(f"   ❌ 获取表格列表异常: {e}")

    # 测试5: 测试保存数据
    print("\n5. 测试保存记账数据...")
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

    print("\n=== 飞书知识空间节点访问测试完成 ===")


if __name__ == "__main__":
    test_knowledge_space_access()