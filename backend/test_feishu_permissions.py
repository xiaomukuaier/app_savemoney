#!/usr/bin/env python3
"""
飞书权限详细测试脚本
检查应用权限和表格访问
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
import lark_oapi.api.application.v6 as application_v6
import lark_oapi.api.auth.v3 as auth_v3


def test_feishu_permissions():
    """测试飞书应用权限"""
    print("=== 飞书应用权限详细测试 ===")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    table_id = os.getenv("FEISHU_TABLE_ID")
    node_token = os.getenv("FEISHU_NODE_TOKEN")

    print(f"App ID: {app_id}")
    print(f"Table ID: {table_id}")
    print(f"Node Token: {node_token}")

    if not all([app_id, app_secret]):
        print("❌ 环境变量配置不完整")
        return

    # 初始化客户端
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 测试1: 获取租户访问令牌
    print("\n1. 测试获取租户访问令牌...")
    try:
        request = auth_v3.InternalTenantAccessTokenRequest.builder() \
            .request_body(auth_v3.InternalTenantAccessTokenRequestBody.builder()
                .app_id(app_id)
                .app_secret(app_secret)
                .build()) \
            .build()

        response = client.auth.v3.tenant_access_token.internal(request)

        if response.success():
            print(f"   ✅ 租户访问令牌获取成功")
            print(f"     令牌: {response.data.tenant_access_token[:20]}...")
            print(f"     过期时间: {response.data.expire}秒")
        else:
            print(f"   ❌ 租户访问令牌获取失败: {response.msg}")
            print(f"     错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 租户访问令牌获取异常: {e}")

    # 测试2: 测试应用权限
    print("\n2. 测试应用权限...")
    try:
        # 尝试获取应用信息
        request = application_v6.GetApplicationRequest.builder().build()
        response = client.application.v6.application.get(request)

        if response.success():
            app_info = response.data.app
            print(f"   ✅ 应用信息获取成功")
            print(f"     应用名称: {app_info.name}")
            print(f"     应用描述: {app_info.description}")
            print(f"     应用状态: {app_info.status}")
        else:
            print(f"   ❌ 应用信息获取失败: {response.msg}")
            print(f"     错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 应用信息获取异常: {e}")

    # 测试3: 测试多维表格访问
    print("\n3. 测试多维表格访问...")

    # 测试不同的app_token
    app_tokens = [
        ("table_id", table_id),
        ("node_token", node_token),
    ]

    for token_name, app_token in app_tokens:
        if not app_token:
            continue

        print(f"\n   使用 {token_name} 作为app_token: {app_token}")

        # 测试获取表格基本信息
        try:
            request = (bitable_v1.GetAppRequest.builder()
                .app_token(app_token)
                .build())

            response = client.bitable.v1.app.get(request)

            if response.success():
                app_info = response.data.app
                print(f"      ✅ 多维表格信息获取成功")
                print(f"        表格名称: {app_info.name}")
                print(f"        表格修订版本: {app_info.revision}")
                break
            else:
                print(f"      ❌ 多维表格信息获取失败: {response.msg}")
                print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
        except Exception as e:
            print(f"      ❌ 多维表格信息获取异常: {e}")

        # 测试获取表格列表
        try:
            request = (bitable_v1.ListAppTableRequest.builder()
                .app_token(app_token)
                .build())

            response = client.bitable.v1.app_table.list(request)

            if response.success():
                tables = response.data.items
                print(f"      ✅ 获取到 {len(tables)} 个表格")
                for table in tables:
                    print(f"        - {table.name} (ID: {table.table_id})")
                break
            else:
                print(f"      ❌ 获取表格列表失败: {response.msg}")
                print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
        except Exception as e:
            print(f"      ❌ 获取表格列表异常: {e}")

    # 测试4: 测试记录操作
    print("\n4. 测试记录操作...")

    # 使用有效的app_token测试保存记录
    for token_name, app_token in app_tokens:
        if not app_token:
            continue

        print(f"\n   使用 {token_name} 作为app_token测试记录操作")

        # 测试获取记录列表
        try:
            request = (bitable_v1.ListAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .page_size(5)
                .build())

            response = client.bitable.v1.app_table_record.list(request)

            if response.success():
                records = response.data.items
                print(f"      ✅ 获取到 {len(records)} 条记录")
                break
            else:
                print(f"      ❌ 获取记录列表失败: {response.msg}")
                print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
        except Exception as e:
            print(f"      ❌ 获取记录列表异常: {e}")

    print("\n=== 飞书应用权限详细测试完成 ===")


if __name__ == "__main__":
    test_feishu_permissions()