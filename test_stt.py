#!/usr/bin/env python3
"""
测试OpenAI STT服务
使用测试音频文件验证语音转文本功能
"""

import asyncio
import os
import sys

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.stt import SpeechToTextService


async def test_stt_with_audio_file():
    """测试STT服务与音频文件"""

    # 初始化STT服务
    stt_service = SpeechToTextService()

    # 打印配置信息
    print(f"OpenAI API Key: {'已配置' if os.getenv('OPENAI_API_KEY') else '未配置'}")
    print(f"OpenAI Base URL: {os.getenv('OPENAI_BASE_URL', '默认')}")
    print(f"STT Client: {'已初始化' if stt_service.client else '未初始化'}")

    # 检查音频文件
    audio_file_path = "data/test.m4a"
    if not os.path.exists(audio_file_path):
        print(f"错误: 音频文件不存在: {audio_file_path}")
        return

    print(f"找到音频文件: {audio_file_path}")
    print(f"文件大小: {os.path.getsize(audio_file_path)} bytes")

    # 读取音频文件
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    print(f"读取音频数据: {len(audio_data)} bytes")

    # 测试STT转换
    print("\n开始语音转文本...")

    try:
        transcription = await stt_service.transcribe_audio(audio_data, "test.m4a")

        print(f"\n语音识别结果:")
        print(f"  - 文本: {transcription}")
        print(f"  - 长度: {len(transcription)} 字符")

        # 检查是否使用了模拟模式
        if stt_service.client is None:
            print("\n⚠️  警告: 使用模拟模式 (OpenAI API密钥未配置)")
            print("请设置 OPENAI_API_KEY 环境变量以使用真实的语音识别")
        else:
            print("\n✅ 成功调用OpenAI Whisper API")

        # 验证结果
        expected_phrases = ["25.3", "毛钱", "午饭", "中午"]
        found_phrases = []
        for phrase in expected_phrases:
            if phrase in transcription:
                found_phrases.append(phrase)

        if found_phrases:
            print(f"✅ 识别结果包含预期关键词: {', '.join(found_phrases)}")
        else:
            print("⚠️  识别结果未包含预期关键词")

    except Exception as e:
        print(f"❌ STT测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=== OpenAI STT 服务测试 ===")
    print("测试音频: '今天中午花了25.3毛钱吃午饭。'")
    print()

    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key":
        print("✅ OPENAI_API_KEY 已配置")
    else:
        print("⚠️  OPENAI_API_KEY 未配置，将使用模拟模式")

    print()

    # 运行测试
    asyncio.run(test_stt_with_audio_file())