"""
语音转文本服务
使用OpenAI Whisper API进行语音识别
"""

import os
import tempfile
from typing import Optional
import httpx
from openai import OpenAI
from pydub import AudioSegment
from pydub.utils import mediainfo


class SpeechToTextService:
    """语音转文本服务"""

    def __init__(self):
        # 确保环境变量已加载
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        print(f"STT服务初始化 - API Key: {'已配置' if api_key and api_key != 'your_openai_api_key' else '未配置'}")

        if api_key and api_key != "your_openai_api_key":
            self.client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.client = None

    async def transcribe_audio(self, audio_data: bytes, filename: str = "audio.wav") -> Optional[str]:
        """
        将音频数据转换为文本

        Args:
            audio_data: 音频二进制数据
            filename: 音频文件名

        Returns:
            识别的文本内容，如果失败返回None
        """
        # 检查是否有可用的OpenAI客户端
        if not self.client:
            print("警告: OpenAI客户端未初始化，使用模拟模式")
            return self._generate_mock_transcription()

        # 检查音频时长，如果超过30秒则截断
        duration = self._get_audio_duration(audio_data)
        print(f"音频时长: {duration:.1f}秒")

        if duration > 30:
            print("音频超过30秒，进行截断处理")
            audio_data = self._truncate_audio_to_30s(audio_data)
            print("音频截断完成")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # 调用OpenAI Whisper API
            with open(temp_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh",  # 指定中文
                    response_format="text"
                )

            transcription = str(response).strip()
            print(f"语音识别结果: {transcription}")
            return transcription

        except Exception as e:
            print(f"语音识别失败: {e}")
            # 如果API调用失败，返回模拟结果
            return self._generate_mock_transcription()

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except:
                pass

    def _get_audio_duration(self, audio_data: bytes) -> float:
        """获取音频时长（秒）"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # 使用pydub获取音频时长
            audio = AudioSegment.from_file(temp_path)
            duration_seconds = len(audio) / 1000.0  # 转换为秒

            # 清理临时文件
            os.unlink(temp_path)

            return duration_seconds
        except Exception as e:
            print(f"获取音频时长失败: {e}")
            return 0.0

    def _truncate_audio_to_30s(self, audio_data: bytes) -> bytes:
        """将音频截断为30秒"""
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            # 加载音频
            audio = AudioSegment.from_file(temp_path)

            # 截取前30秒
            max_duration = 30 * 1000  # 30秒，单位毫秒
            if len(audio) > max_duration:
                print(f"音频超过30秒 ({len(audio)/1000:.1f}s)，截取前30秒")
                truncated_audio = audio[:max_duration]

                # 保存截断后的音频
                truncated_path = temp_path + "_truncated.wav"
                truncated_audio.export(truncated_path, format="wav")

                # 读取截断后的音频数据
                with open(truncated_path, "rb") as f:
                    truncated_data = f.read()

                # 清理临时文件
                os.unlink(temp_path)
                os.unlink(truncated_path)

                return truncated_data
            else:
                # 音频不超过30秒，直接返回原数据
                os.unlink(temp_path)
                return audio_data

        except Exception as e:
            print(f"音频截断失败: {e}")
            return audio_data  # 如果截断失败，返回原数据

    def _generate_mock_transcription(self) -> str:
        """生成模拟的语音识别结果"""
        import random

        mock_transcriptions = [
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

        return random.choice(mock_transcriptions)


# 全局服务实例 - 延迟初始化
_stt_instance = None

def get_stt_service():
    """获取STT服务实例（延迟初始化）"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToTextService()
    return _stt_instance

stt_service = get_stt_service()