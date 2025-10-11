#!/usr/bin/env python3
"""
测试完整的工作流程
测试语音识别 + LangGraph处理
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.stt import SpeechToTextService
from app.services.langgraph_workflow import LangGraphWorkflowService


async def test_full_workflow():
    """测试完整的工作流程"""

    print("=== 完整工作流程测试 ===")
    print("测试音频: '今天中午花了25.3毛钱吃午饭。'")
    print()

    # 初始化服务
    stt_service = SpeechToTextService()
    langgraph_service = LangGraphWorkflowService()

    # 检查音频文件
    audio_file_path = "../data/test.m4a"
    if not os.path.exists(audio_file_path):
        print(f"错误: 音频文件不存在: {audio_file_path}")
        return

    print(f"找到音频文件: {audio_file_path}")
    print(f"文件大小: {os.path.getsize(audio_file_path)} bytes")

    # 读取音频文件
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    print(f"读取音频数据: {len(audio_data)} bytes")

    # 步骤1: 语音转文本
    print("\n--- 步骤1: 语音转文本 ---")

    try:
        transcription = await stt_service.transcribe_audio(audio_data, "test.m4a")
        print(f"语音识别结果: {transcription}")

        # 检查是否使用了模拟模式
        if stt_service.client is None:
            print("⚠️  使用模拟模式 (OpenAI客户端未初始化)")
        else:
            print("✅ 成功调用OpenAI Whisper API")

    except Exception as e:
        print(f"❌ 语音识别失败: {e}")
        return

    # 步骤2: LangGraph处理
    print("\n--- 步骤2: LangGraph处理 ---")

    try:
        expense_data = await langgraph_service.process_expense(transcription)
        print("✅ LangGraph处理成功")

        # 显示处理结果
        print(f"\n处理结果:")
        print(f"  金额: {expense_data.get('amount', 'N/A')}")
        print(f"  分类: {expense_data.get('category', 'N/A')}")
        print(f"  子分类: {expense_data.get('subcategory', 'N/A')}")
        print(f"  描述: {expense_data.get('description', 'N/A')}")
        print(f"  日期: {expense_data.get('date', 'N/A')}")
        print(f"  类型: {expense_data.get('type', 'N/A')}")
        print(f"  支付方式: {expense_data.get('payment_method', 'N/A')}")
        print(f"  置信度: {expense_data.get('confidence', 'N/A')}")

        # 检查是否有分类建议
        if expense_data.get("category_suggestions"):
            print(f"\n分类建议:")
            for suggestion in expense_data.get("category_suggestions", []):
                print(f"  - {suggestion}")

        # 检查是否需要确认
        if expense_data.get("needs_confirmation"):
            print(f"\n需要确认的问题:")
            for question in expense_data.get("confirmation_questions", []):
                print(f"  - {question}")

        # 验证结果
        expected_amount = 25.3
        actual_amount = expense_data.get('amount')

        if actual_amount == expected_amount:
            print(f"\n✅ 金额识别正确: {actual_amount}")
        else:
            print(f"\n⚠️  金额识别有误: 期望 {expected_amount}, 实际 {actual_amount}")

        expected_category = "餐饮"
        actual_category = expense_data.get('category')

        if actual_category == expected_category:
            print(f"✅ 分类识别正确: {actual_category}")
        else:
            print(f"⚠️  分类识别有误: 期望 {expected_category}, 实际 {actual_category}")

    except Exception as e:
        print(f"❌ LangGraph处理失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_workflow())