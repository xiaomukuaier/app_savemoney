#!/usr/bin/env python3
"""
测试前端UI确认功能
模拟完整的前端确认流程
"""

import requests
import json

def test_frontend_ui_flow():
    """测试前端UI确认流程"""

    print("=== 前端UI确认流程测试 ===")

    # 模拟语音识别返回的数据（包含新字段）
    expense_data = {
        "amount": 29.9,
        "category": "购物",
        "subcategory": "日用品",
        "description": "买衣架",
        "date": "2025-10-13",
        "type": "expense",
        "payment_method": "银行卡",
        "confidence": 0.8,
        "is_daily": "待定",
        "is_necessary": "待定",
        "raw_text": "今天花了¥29.9买衣架，用银行卡支付的"
    }

    print(f"前端显示的数据结构:")
    print(json.dumps(expense_data, indent=2, ensure_ascii=False))

    print("\n✅ 前端应该显示以下字段:")
    print("  - 金额: ¥29.9")
    print("  - 分类: 购物")
    print("  - 子分类: 日用品")
    print("  - 描述: 买衣架")
    print("  - 日期: 2025-10-13")
    print("  - 支付方式: 银行卡")
    print("  - 是否日常: 待定")
    print("  - 是否为必须开支: 待定")
    print("  - 置信度: 80%")

    print("\n✅ 前端应该有以下按钮:")
    print("  - 取消按钮")
    print("  - 确认记账按钮 (主要按钮)")

    # 测试确认请求
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/expenses",
            json=expense_data
        )

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 确认请求成功!")
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"\n❌ 确认请求失败: {response.text}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    test_frontend_ui_flow()