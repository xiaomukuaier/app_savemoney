#!/usr/bin/env python3
"""
测试OpenAI STT服务 - WAV文件专用测试
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


async def test_stt_with_wav():
    """测试STT服务与WAV文件"""

    # 初始化STT服务
    stt_service = SpeechToTextService()

    # 检查WAV音频文件
    audio_file_path = "../data/test.wav"
    if not os.path.exists(audio_file_path):
        print(f"错误: WAV音频文件不存在: {audio_file_path}")
        return

    print(f"找到WAV音频文件: {audio_file_path}")
    print(f"文件大小: {os.path.getsize(audio_file_path)} bytes")

    # 读取音频文件
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    print(f"读取音频数据: {len(audio_data)} bytes")

    # 测试STT转换
    print("\n开始语音转文本...")

    try:
        transcription = await stt_service.transcribe_audio(audio_data, "test.wav")

        print(f"\n语音识别结果:")
        print(f"  - 文本: {transcription}")
        print(f"  - 长度: {len(transcription)} 字符")

        # 检查是否使用了模拟模式
        if stt_service.client is None:
            print("\n⚠️  警告: 使用模拟模式 (OpenAI客户端未初始化)")
        else:
            print("\n✅ 成功调用OpenAI Whisper API")

        # 验证结果
        expected_phrases = ["25.3", "毛钱", "午饭", "中午", "25", "3", "吃饭", "午餐"]
        found_phrases = []
        for phrase in expected_phrases:
            if phrase in transcription:
                found_phrases.append(phrase)

        if found_phrases:
            print(f"✅ 识别结果包含预期关键词: {', '.join(found_phrases)}")
        else:
            print("⚠️  识别结果未包含预期关键词")
            print(f"完整结果: {transcription}")

        # 检查是否为真实识别结果（不是模拟结果）
        mock_results = [
            "今天中午吃饭花了二十五块钱",
            "买了一杯咖啡十八元",
            "打车回家花了三十八块五",
            "超市购物消费六十七元",
            "看电影花了四十五块钱",
            "充话费一百元",
            "买书花了三十六元",
            "理发消费三十五元",
            "买水果花了二十八块",
            "外卖点餐四十二元"
        ]

        if transcription in mock_results:
            print("\n⚠️  使用模拟结果，真实STT可能未工作")
        else:
            print("\n🎉 成功获取真实语音识别结果！")

    except Exception as e:
        print(f"❌ STT测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=== OpenAI STT WAV文件测试 ===")
    print("测试音频: '今天中午花了25.3毛钱吃午饭。'")
    print()

    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API Key: {'已配置' if api_key and api_key != 'your_openai_api_key' else '未配置'}")

    # 运行测试
    asyncio.run(test_stt_with_wav())