#!/usr/bin/env python3
"""
检查飞书多维表格的字段结构
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

from lark_oapi import Client
import lark_oapi.api.bitable.v1 as bitable_v1


def test_table_structure():
    """检查表格字段结构"""
    print("=== 飞书多维表格字段结构检查 ===")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    app_token = os.getenv("FEISHU_APP_TOKEN")
    table_id = os.getenv("FEISHU_TABLE_ID")

    print(f"App Token: {app_token}")
    print(f"Table ID: {table_id}")

    if not all([app_id, app_secret, app_token, table_id]):
        print("❌ 环境变量配置不完整")
        return

    # 初始化客户端
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 获取表格字段列表
    print("\n1. 获取表格字段列表...")
    try:
        request = (bitable_v1.ListAppTableFieldRequest.builder()
            .app_token(app_token)
            .table_id(table_id)
            .build())

        response = client.bitable.v1.app_table_field.list(request)

        if response.success():
            fields = response.data.items
            print(f"   ✅ 获取到 {len(fields)} 个字段")
            for field in fields:
                print(f"     - 字段名: '{field.field_name}'")
                print(f"       类型: {field.type}")
                print(f"       字段ID: {field.field_id}")
                if hasattr(field, 'property'):
                    print(f"       属性: {field.property}")
                print()
        else:
            print(f"   ❌ 获取字段列表失败: {response.msg}")
            print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ 获取字段列表异常: {e}")

    # 获取现有记录（如果有）
    print("\n2. 获取现有记录...")
    try:
        request = (bitable_v1.ListAppTableRecordRequest.builder()
            .app_token(app_token)
            .table_id(table_id)
            .page_size(5)
            .build())

        response = client.bitable.v1.app_table_record.list(request)

        if response.success():
            records = response.data.items
            print(f"   ✅ 获取到 {len(records)} 条记录")
            for i, record in enumerate(records, 1):
                print(f"     记录 {i}:")
                if hasattr(record, 'fields'):
                    for field_name, field_value in record.fields.items():
                        print(f"       {field_name}: {field_value}")
                print()
        else:
            print(f"   ❌ 获取记录失败: {response.msg}")
            print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ 获取记录异常: {e}")

    print("\n=== 飞书多维表格字段结构检查完成 ===")


if __name__ == "__main__":
    test_table_structure()