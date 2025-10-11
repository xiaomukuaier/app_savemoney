#!/usr/bin/env python3
"""
改进的OpenAI STT测试
尝试不同的文件处理方式
"""

import asyncio
import os
import sys
import tempfile
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.stt import SpeechToTextService


async def test_stt_direct_file():
    """测试直接使用文件路径"""

    stt_service = SpeechToTextService()
    audio_file_path = "data/test.m4a"

    print("方法1: 直接读取文件并传输")

    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    try:
        transcription = await stt_service.transcribe_audio(audio_data, "test.m4a")
        print(f"结果: {transcription}")
        return True
    except Exception as e:
        print(f"失败: {e}")
        return False


async def test_stt_with_conversion():
    """测试文件格式转换"""

    stt_service = SpeechToTextService()
    audio_file_path = "data/test.m4a"

    print("\n方法2: 尝试转换为WAV格式")

    try:
        # 使用ffmpeg转换格式
        import subprocess

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        # 转换为WAV格式
        cmd = [
            "ffmpeg", "-i", audio_file_path,
            "-ac", "1", "-ar", "16000", "-sample_fmt", "s16",
            temp_path, "-y"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("格式转换成功")

            with open(temp_path, "rb") as f:
                audio_data = f.read()

            transcription = await stt_service.transcribe_audio(audio_data, "test.wav")
            print(f"结果: {transcription}")

            # 清理临时文件
            os.unlink(temp_path)
            return True
        else:
            print(f"格式转换失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"转换失败: {e}")
        # 清理临时文件
        try:
            os.unlink(temp_path)
        except:
            pass
        return False


async def test_stt_with_different_params():
    """测试不同的API参数"""

    stt_service = SpeechToTextService()
    audio_file_path = "data/test.m4a"

    print("\n方法3: 直接使用OpenAI客户端测试")

    if not stt_service.client:
        print("OpenAI客户端未初始化")
        return False

    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    try:
        # 直接使用OpenAI客户端调用
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        with open(temp_path, "rb") as audio_file:
            response = stt_service.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="zh",
                response_format="text"
            )

        transcription = str(response).strip()
        print(f"直接调用结果: {transcription}")

        # 验证结果
        expected_phrases = ["25.3", "毛钱", "午饭", "中午", "25", "3", "吃饭"]
        found_phrases = []
        for phrase in expected_phrases:
            if phrase in transcription:
                found_phrases.append(phrase)

        if found_phrases:
            print(f"✅ 识别结果包含预期关键词: {', '.join(found_phrases)}")
        else:
            print("⚠️  识别结果未包含预期关键词")
            print(f"完整结果: {transcription}")

        os.unlink(temp_path)
        return True

    except Exception as e:
        print(f"直接调用失败: {e}")
        try:
            os.unlink(temp_path)
        except:
            pass
        return False


async def main():
    print("=== 改进的OpenAI STT测试 ===")
    print("测试音频: '今天中午花了25.3毛钱吃午饭。'")
    print()

    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"OpenAI API Key: {'已配置' if api_key and api_key != 'your_openai_api_key' else '未配置'}")

    success = False

    # 方法1: 直接文件传输
    if not await test_stt_direct_file():
        print("方法1失败，尝试方法2...")

        # 方法2: 格式转换
        if not await test_stt_with_conversion():
            print("方法2失败，尝试方法3...")

            # 方法3: 直接API调用
            success = await test_stt_with_different_params()
        else:
            success = True
    else:
        success = True

    if success:
        print("\n✅ STT测试成功完成")
    else:
        print("\n❌ STT测试失败")


if __name__ == "__main__":
    asyncio.run(main())