#!/usr/bin/env python3
"""
端到端测试脚本
模拟完整的用户使用流程
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.stt import stt_service
from app.services.langgraph_workflow import langgraph_service


async def test_end_to_end():
    """测试端到端流程"""
    print("=== 端到端测试 ===")

    # 模拟语音识别文本
    test_transcriptions = [
        "今天中午吃饭花了二十五块钱",
        "打车回家花了三十八块五",
        "买了一杯咖啡十八元",
        "超市购物消费六十七元",
        "看电影花了四十五块钱"
    ]

    for i, transcription in enumerate(test_transcriptions, 1):
        print(f"\n测试用例 {i}: {transcription}")

        try:
            # 1. 语音识别（模拟）
            print("  1. 语音识别...")
            # 这里我们直接使用模拟的转录文本

            # 2. LangGraph工作流处理
            print("  2. LangGraph工作流处理...")
            expense_data = await langgraph_service.process_expense(transcription)

            # 3. 验证结果
            print("  3. 验证结果...")
            print(f"     金额: {expense_data.get('amount')}")
            print(f"     分类: {expense_data.get('category')}")
            print(f"     描述: {expense_data.get('description')}")
            print(f"     支付方式: {expense_data.get('payment_method')}")
            print(f"     置信度: {expense_data.get('confidence')}")

            # 4. 验证必要字段
            required_fields = ['amount', 'category', 'description', 'payment_method', 'confidence']
            all_present = all(field in expense_data for field in required_fields)

            if all_present:
                print("  ✅ 所有必要字段都存在")
            else:
                print("  ❌ 缺少必要字段")

            # 5. 验证金额合理性
            amount = expense_data.get('amount', 0)
            if 0 < amount < 1000:
                print("  ✅ 金额在合理范围内")
            else:
                print("  ⚠️  金额可能不合理")

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

    print("\n=== 端到端测试完成 ===")


async def test_stt_service():
    """测试语音识别服务"""
    print("\n=== 语音识别服务测试 ===")

    # 测试空音频数据
    empty_audio = b""
    try:
        result = await stt_service.transcribe_audio(empty_audio)
        print(f"空音频处理结果: {result}")
    except Exception as e:
        print(f"空音频处理失败: {e}")

    # 测试模拟模式
    test_audio = b"fake_audio_data"
    try:
        result = await stt_service.transcribe_audio(test_audio)
        print(f"模拟音频处理结果: {result}")
        print("  ✅ 语音识别服务在模拟模式下正常工作")
    except Exception as e:
        print(f"模拟音频处理失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_end_to_end())
    asyncio.run(test_stt_service())