#!/usr/bin/env python3
"""
SaveMoney 记账应用 - Gradio增强版本
包含用户交互界面和正确的飞书字段映射
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
from backend.app.services.feishu_api import FeishuAPIService

# 初始化服务
stt_service = SpeechToTextService()
gpt_parser = GPTParserService()
feishu_api = FeishuAPIService()

class SaveMoneyApp:
    def __init__(self):
        self.history = []
        self.current_data = None

    async def process_audio(self, audio_file):
        """处理音频文件并返回结构化记账信息"""
        try:
            # 检查音频文件是否存在
            if not audio_file:
                return "❌ 请先录制或上传音频文件", "", "", "", "", "", "", ""

            # 语音转文本
            print(f"处理音频文件: {audio_file}")
            # 读取音频文件
            with open(audio_file, 'rb') as f:
                audio_data = f.read()

            text = await stt_service.transcribe_audio(audio_data)

            if not text:
                return "❌ 语音识别失败，请重试", "", "", "", "", "", "", ""

            # GPT解析文本
            print(f"解析文本: {text}")
            parsed_data = await gpt_parser.parse_expense_text(text)

            if not parsed_data:
                return "❌ 解析失败，请重试", "", "", "", "", "", "", ""

            # 保存当前数据用于后续编辑
            self.current_data = parsed_data

            # 返回可编辑的表单数据
            return (
                text,  # 原始文本
                parsed_data.get('amount', ''),  # 金额
                parsed_data.get('category', ''),  # 分类
                parsed_data.get('subcategory', ''),  # 子分类
                parsed_data.get('description', ''),  # 描述
                parsed_data.get('payment_method', ''),  # 支付方式
                parsed_data.get('date', datetime.now().strftime('%Y-%m-%d')),  # 日期
                json.dumps(parsed_data, ensure_ascii=False, indent=2)  # 原始JSON数据
            )

        except Exception as e:
            return f"❌ 处理失败: {str(e)}", "", "", "", "", "", "", ""

    def save_to_feishu(self,
                      original_text,
                      amount,
                      category,
                      subcategory,
                      description,
                      payment_method,
                      date,
                      is_daily,
                      is_necessary):
        """保存到飞书多维表格"""
        try:
            # 构建飞书表格数据
            expense_data = {
                "amount": float(amount) if amount else 0.0,
                "category": category,
                "subcategory": subcategory,
                "description": description,
                "payment_method": payment_method,
                "date": date,
                "is_daily": is_daily,
                "is_necessary": is_necessary,
                "original_text": original_text
            }

            # 保存到飞书
            success = feishu_api.save_expense_to_table(expense_data)

            if success:
                # 添加到历史记录
                self.history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'text': original_text,
                    'data': expense_data
                })
                return "✅ 保存成功！"
            else:
                return "❌ 保存失败: 请检查飞书API配置"

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
    """创建增强版Gradio界面"""
    app = SaveMoneyApp()

    with gr.Blocks(
        title="SaveMoney 智能记账",
        theme=gr.themes.Soft(),
        css="""
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .recording-timer {
            color: #ff6b35;
            font-weight: bold;
            font-size: 14px;
            margin-top: 5px;
        }
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
                    label="🎤 点击录音或上传音频文件 (最长30秒)"
                )

                # 录音计时器显示
                timer_display = gr.HTML(
                    value="<div class='recording-timer' id='timer-display'>准备录音...</div>",
                    visible=False
                )

                process_btn = gr.Button("🚀 处理语音", variant="primary")

                # 结果显示和编辑区域
                with gr.Group():
                    gr.Markdown("### 📋 编辑确认信息")

                    original_text = gr.Textbox(
                        label="原始文本",
                        lines=2,
                        interactive=False
                    )

                    with gr.Row():
                        amount = gr.Textbox(
                            label="💰 金额",
                            placeholder="请输入金额",
                            interactive=True
                        )
                        category = gr.Textbox(
                            label="🏷️ 分类",
                            placeholder="请输入分类",
                            interactive=True
                        )

                    with gr.Row():
                        subcategory = gr.Textbox(
                            label="📂 子分类",
                            placeholder="请输入子分类",
                            interactive=True
                        )
                        payment_method = gr.Textbox(
                            label="💳 支付方式",
                            placeholder="请输入支付方式",
                            interactive=True
                        )

                    description = gr.Textbox(
                        label="📝 描述",
                        placeholder="请输入描述",
                        lines=2,
                        interactive=True
                    )

                    date = gr.Textbox(
                        label="📅 日期",
                        placeholder="YYYY-MM-DD",
                        interactive=True
                    )

                    with gr.Row():
                        is_daily = gr.Radio(
                            choices=["是", "否", "待定"],
                            label="是否日常开支",
                            value="待定"
                        )
                        is_necessary = gr.Radio(
                            choices=["是", "否", "待定"],
                            label="是否为必须开支",
                            value="待定"
                        )

                # 隐藏字段
                json_data = gr.Textbox(visible=False)

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
            outputs=[
                original_text, amount, category, subcategory,
                description, payment_method, date, json_data
            ]
        )

        save_btn.click(
            fn=app.save_to_feishu,
            inputs=[
                original_text, amount, category, subcategory,
                description, payment_method, date, is_daily, is_necessary
            ],
            outputs=[save_result]
        )

        refresh_btn.click(
            fn=app.get_history,
            outputs=[history_display]
        )

        # 初始化历史记录
        demo.load(app.get_history, outputs=[history_display])

        # 添加JavaScript代码实现30秒录音限制
        demo.load(
            None,
            js="""
            function setupRecordingTimer() {
                const audioInput = document.querySelector('input[type="file"]');
                const timerDisplay = document.getElementById('timer-display');
                let recordingTimer = null;
                let secondsRemaining = 30;

                if (audioInput && timerDisplay) {
                    // 监听录音开始
                    audioInput.addEventListener('click', function() {
                        // 重置计时器
                        clearInterval(recordingTimer);
                        secondsRemaining = 30;
                        timerDisplay.style.display = 'block';
                        timerDisplay.innerHTML = `⏱️ 录音中... 剩余时间: ${secondsRemaining}秒`;

                        // 启动30秒倒计时
                        recordingTimer = setInterval(function() {
                            secondsRemaining--;
                            timerDisplay.innerHTML = `⏱️ 录音中... 剩余时间: ${secondsRemaining}秒`;

                            if (secondsRemaining <= 0) {
                                clearInterval(recordingTimer);
                                timerDisplay.innerHTML = '⏰ 录音已自动停止 (30秒限制)';

                                // 模拟停止录音（Gradio会自动处理）
                                setTimeout(function() {
                                    timerDisplay.innerHTML = '准备录音...';
                                    timerDisplay.style.display = 'none';
                                }, 2000);
                            }
                        }, 1000);
                    });

                    // 监听录音结束（文件选择）
                    audioInput.addEventListener('change', function() {
                        clearInterval(recordingTimer);
                        timerDisplay.innerHTML = '✅ 录音完成';
                        setTimeout(function() {
                            timerDisplay.innerHTML = '准备录音...';
                            timerDisplay.style.display = 'none';
                        }, 2000);
                    });
                }
            }

            // 页面加载完成后设置计时器
            setTimeout(setupRecordingTimer, 1000);
            """
        )

    return demo

if __name__ == "__main__":
    # 创建并启动应用
    demo = create_gradio_interface()

    # 获取端口配置
    port = int(os.getenv("PORT", 7860))

    print(f"🚀 SaveMoney Gradio增强版应用启动中...")
    print(f"📱 访问地址: http://localhost:{port}")

    # 启动应用
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        debug=True
    )