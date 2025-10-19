#!/usr/bin/env python3
"""
SaveMoney 记账应用 - Gradio版本
基于语音输入的智能记账应用
"""

import os
import gradio as gr
import tempfile
import json
from pathlib import Path
from datetime import datetime

# 导入现有服务
from backend.app.services.stt import SpeechToTextService
from backend.app.services.gpt_parser import GPTParserService
from backend.app.services.feishu_api import FeishuAPI

# 初始化服务
stt_service = SpeechToTextService()
gpt_parser = GPTParserService()
feishu_api = FeishuAPI()

class SaveMoneyApp:
    def __init__(self):
        self.history = []

    def process_audio(self, audio_file):
        """处理音频文件并返回结构化记账信息"""
        try:
            # 语音转文本
            print(f"处理音频文件: {audio_file}")
            text = stt_service.transcribe_audio(audio_file)

            if not text:
                return "❌ 语音识别失败，请重试", "", ""

            # GPT解析文本
            print(f"解析文本: {text}")
            parsed_data = gpt_parser.parse_expense_text(text)

            if not parsed_data:
                return "❌ 解析失败，请重试", "", ""

            # 格式化显示
            display_text = f"""
🎤 识别文本: {text}

💰 解析结果:
- 金额: {parsed_data.get('amount', '未知')}
- 分类: {parsed_data.get('category', '未知')}
- 描述: {parsed_data.get('description', '无')}
- 类型: {parsed_data.get('type', '支出')}
- 日期: {parsed_data.get('date', '今天')}
"""

            return display_text, json.dumps(parsed_data, ensure_ascii=False, indent=2), text

        except Exception as e:
            return f"❌ 处理失败: {str(e)}", "", ""

    def save_to_feishu(self, parsed_json, original_text):
        """保存到飞书多维表格"""
        try:
            if not parsed_json:
                return "❌ 没有可保存的数据"

            data = json.loads(parsed_json)

            # 保存到飞书
            result = feishu_api.create_record(data)

            if result.get('success'):
                # 添加到历史记录
                self.history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'text': original_text,
                    'data': data
                })
                return "✅ 保存成功！"
            else:
                return f"❌ 保存失败: {result.get('message', '未知错误')}"

        except Exception as e:
            return f"❌ 保存失败: {str(e)}"

    def get_history(self):
        """获取历史记录"""
        if not self.history:
            return "暂无历史记录"

        history_text = ""
        for i, record in enumerate(self.history[-10:], 1):  # 显示最近10条
            history_text += f"\n{i}. [{record['timestamp']}]\n"
            history_text += f"   文本: {record['text']}\n"
            history_text += f"   金额: {record['data'].get('amount', '未知')}\n"
            history_text += f"   分类: {record['data'].get('category', '未知')}\n"

        return history_text

def create_gradio_interface():
    """创建Gradio界面"""
    app = SaveMoneyApp()

    with gr.Blocks(
        title="SaveMoney 智能记账",
        theme=gr.themes.Soft(),
        css="""
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        """
    ) as demo:
        gr.Markdown("""
        # 💰 SaveMoney 智能记账

        基于语音输入的智能记账应用，自动识别消费信息并保存到飞书表格。
        """)

        with gr.Row():
            with gr.Column():
                # 语音输入
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 点击录音或上传音频文件"
                )

                process_btn = gr.Button("🚀 处理语音", variant="primary")

                # 结果显示
                result_display = gr.Textbox(
                    label="📋 识别结果",
                    lines=8,
                    max_lines=12,
                    interactive=False
                )

                # 原始JSON数据（隐藏）
                json_data = gr.Textbox(visible=False)
                original_text = gr.Textbox(visible=False)

                # 保存按钮
                save_btn = gr.Button("💾 保存到飞书", variant="secondary")
                save_result = gr.Textbox(
                    label="保存状态",
                    lines=2,
                    interactive=False
                )

            with gr.Column():
                # 历史记录
                history_display = gr.Textbox(
                    label="📜 最近记录",
                    lines=15,
                    max_lines=20,
                    interactive=False
                )

                refresh_btn = gr.Button("🔄 刷新历史")

        # 事件处理
        process_btn.click(
            fn=app.process_audio,
            inputs=[audio_input],
            outputs=[result_display, json_data, original_text]
        )

        save_btn.click(
            fn=app.save_to_feishu,
            inputs=[json_data, original_text],
            outputs=[save_result]
        )

        refresh_btn.click(
            fn=app.get_history,
            outputs=[history_display]
        )

        # 初始化历史记录
        demo.load(app.get_history, outputs=[history_display])

    return demo

if __name__ == "__main__":
    # 创建并启动应用
    demo = create_gradio_interface()

    # 获取端口配置
    port = int(os.getenv("PORT", 7860))

    print(f"🚀 SaveMoney Gradio应用启动中...")
    print(f"📱 访问地址: http://localhost:{port}")

    # 启动应用
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        debug=True
    )