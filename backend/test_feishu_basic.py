#!/usr/bin/env python3
"""
飞书基础API测试脚本
测试最基本的API调用能力
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
import lark_oapi.api.contact.v3 as contact_v3


def test_feishu_basic():
    """测试飞书基础API调用"""
    print("=== 飞书基础API测试 ===")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")

    print(f"App ID: {app_id}")

    if not all([app_id, app_secret]):
        print("❌ 环境变量配置不完整")
        return

    # 初始化客户端
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 测试1: 获取用户列表（基础权限测试）
    print("\n1. 测试获取用户列表...")
    try:
        request = contact_v3.ListUserRequest.builder() \
            .page_size(10) \
            .build()

        response = client.contact.v3.user.list(request)

        if response.success():
            users = response.data.items
            print(f"   ✅ 获取到 {len(users)} 个用户")
            for user in users[:3]:  # 只显示前3个
                print(f"     - {user.name} ({user.user_id})")
        else:
            print(f"   ❌ 获取用户列表失败: {response.msg}")
            print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
            print(f"     错误详情: {response}")
    except Exception as e:
        print(f"   ❌ 获取用户列表异常: {e}")

    # 测试2: 获取部门列表
    print("\n2. 测试获取部门列表...")
    try:
        request = contact_v3.ListDepartmentRequest.builder() \
            .page_size(10) \
            .build()

        response = client.contact.v3.department.list(request)

        if response.success():
            departments = response.data.items
            print(f"   ✅ 获取到 {len(departments)} 个部门")
            for dept in departments[:3]:  # 只显示前3个
                print(f"     - {dept.name} ({dept.department_id})")
        else:
            print(f"   ❌ 获取部门列表失败: {response.msg}")
            print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ 获取部门列表异常: {e}")

    print("\n=== 飞书基础API测试完成 ===")


if __name__ == "__main__":
    test_feishu_basic()