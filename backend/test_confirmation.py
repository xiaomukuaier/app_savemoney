#!/usr/bin/env python3
"""
测试确认功能
模拟前端确认记账信息并保存到飞书
"""

import requests
import json

def test_confirmation():
    """测试确认功能"""

    print("=== 确认功能测试 ===")

    # 模拟一个记账数据
    expense_data = {
        "amount": 29.9,
        "category": "购物",
        "subcategory": "日用品",
        "description": "买衣架",
        "date": "2025-10-13",
        "type": "expense",
        "payment_method": "银行卡",
        "confidence": 0.8,
        "raw_text": "今天花了¥29.9买衣架，用银行卡支付的"
    }

    print(f"测试数据: {json.dumps(expense_data, indent=2, ensure_ascii=False)}")

    try:
        # 发送确认请求
        response = requests.post(
            "http://localhost:8000/api/v1/expenses",
            json=expense_data
        )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ 确认请求成功!")
            print(f"响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if result.get("success"):
                print("✅ 记账数据保存成功")
                if "模拟模式" in result.get("message", ""):
                    print("⚠️  使用模拟模式保存（飞书API未配置）")
                else:
                    print("✅ 使用真实飞书API保存")
            else:
                print("❌ 记账数据保存失败")

        else:
            print(f"❌ 确认请求失败: {response.text}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_confirmation()