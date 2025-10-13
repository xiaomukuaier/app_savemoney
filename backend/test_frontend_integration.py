#!/usr/bin/env python3
"""
测试前端与后端集成
模拟前端发送音频文件到后端API
"""

import requests
import json

def test_frontend_integration():
    """测试前端与后端集成"""

    # 使用我们之前创建的测试音频文件
    audio_file_path = "test_audio.wav"

    print("=== 前端集成测试 ===")
    print(f"使用音频文件: {audio_file_path}")

    try:
        # 模拟前端发送请求
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': ('audio.wav', audio_file, 'audio/wav')}

            response = requests.post(
                "http://localhost:8000/api/v1/audio/transcribe",
                files=files
            )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功!")
            print(f"转录文本: {result.get('transcription', 'N/A')}")
            print(f"解析数据: {json.dumps(result.get('data', {}), indent=2, ensure_ascii=False)}")

            # 检查是否使用了真实API
            if result.get('transcription') and result.get('transcription') != "买了一杯咖啡十八元":
                print("✅ 使用了真实OpenAI API进行语音识别")
            else:
                print("⚠️  可能使用了模拟模式")

            if result.get('data', {}).get('confidence', 0) > 0.5:
                print("✅ 使用了真实OpenAI GPT API进行解析")
            else:
                print("⚠️  可能使用了模拟模式")

        else:
            print(f"❌ 请求失败: {response.text}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_frontend_integration()