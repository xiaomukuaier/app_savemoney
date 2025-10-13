"""
OpenAI GPT-4o mini 智能解析服务
使用GPT-4o mini进行文本解析和结构化数据提取
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI


class GPTParserService:
    """GPT智能解析服务"""

    def __init__(self):
        # 确保环境变量已加载
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        print(f"GPT解析器初始化 - API Key: {'已配置' if api_key and api_key != 'your_openai_api_key' else '未配置'}")

        if api_key and api_key != "your_openai_api_key":
            self.client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.client = None

    async def parse_expense_text(self, text: str) -> Dict[str, Any]:
        """
        使用GPT解析支出文本，提取结构化信息

        Args:
            text: 原始文本，如"今天中午花了25.3毛钱吃午饭"

        Returns:
            结构化支出数据
        """
        if not self.client:
            print("警告: OpenAI客户端未初始化，使用模拟解析")
            return self._generate_mock_parsing(text)

        try:
            from datetime import datetime
            today_date = datetime.now().strftime("%Y-%m-%d")

            # 构建GPT提示词
            system_prompt = f"""你是一个智能记账助手，专门从用户的口语化描述中提取支出信息。

今天是 {today_date}。

请从用户输入中提取以下信息：
- 金额 (amount): 数值，如25.3
- 分类 (category): 主要支出类别，如"餐饮"、"交通"、"购物"、"娱乐"、"医疗"、"其他"
- 子分类 (subcategory): 更具体的分类，如"午餐"、"晚餐"、"打车"、"超市购物"等
- 描述 (description): 简短的描述
- 类型 (type): "expense" 或 "income"
- 支付方式 (payment_method): 如"微信支付"、"支付宝"、"现金"、"银行卡"等
- 日期 (date): 如果用户提到相对时间（如"今天"、"昨天"、"前天"、"上周三"等），请根据今天是 {today_date} 计算出具体日期，格式为YYYY-MM-DD。如果用户没有明确提到日期，请使用今天日期。

请以JSON格式返回，包含以下字段：
{{
    "amount": 金额,
    "category": "分类",
    "subcategory": "子分类",
    "description": "描述",
    "type": "expense",
    "payment_method": "支付方式",
    "date": "日期",
    "confidence": 置信度(0-1),
    "raw_text": "原始文本"
}}

如果信息不完整，请根据上下文合理推断。"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            print(f"GPT解析结果: {result_text}")

            # 解析JSON响应
            parsed_data = self._parse_gpt_response(result_text)

            # 添加原始文本
            parsed_data["raw_text"] = text

            return parsed_data

        except Exception as e:
            print(f"GPT解析失败: {e}")
            return self._generate_mock_parsing(text)

    def parse_expense_text_sync(self, text: str) -> Dict[str, Any]:
        """
        同步版本的GPT解析支出文本

        Args:
            text: 原始文本，如"今天中午花了25.3毛钱吃午饭"

        Returns:
            结构化支出数据
        """
        if not self.client:
            print("警告: OpenAI客户端未初始化，使用模拟解析")
            return self._generate_mock_parsing(text)

        try:
            from datetime import datetime
            today_date = datetime.now().strftime("%Y-%m-%d")

            # 构建GPT提示词
            system_prompt = f"""你是一个智能记账助手，专门从用户的口语化描述中提取支出信息。

今天是 {today_date}。

请从用户输入中提取以下信息：
- 金额 (amount): 数值，如25.3
- 分类 (category): 主要支出类别，如"餐饮"、"交通"、"购物"、"娱乐"、"医疗"、"其他"
- 子分类 (subcategory): 更具体的分类，如"午餐"、"晚餐"、"打车"、"超市购物"等
- 描述 (description): 简短的描述
- 类型 (type): "expense" 或 "income"
- 支付方式 (payment_method): 如"微信支付"、"支付宝"、"现金"、"银行卡"等
- 日期 (date): 如果用户提到相对时间（如"今天"、"昨天"、"前天"、"上周三"等），请根据今天是 {today_date} 计算出具体日期，格式为YYYY-MM-DD。如果用户没有明确提到日期，请使用今天日期。

请以JSON格式返回，包含以下字段：
{{
    "amount": 金额,
    "category": "分类",
    "subcategory": "子分类",
    "description": "描述",
    "type": "expense",
    "payment_method": "支付方式",
    "date": "日期",
    "confidence": 置信度(0-1),
    "raw_text": "原始文本"
}}

如果信息不完整，请根据上下文合理推断。"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()
            print(f"GPT解析结果: {result_text}")

            # 解析JSON响应
            parsed_data = self._parse_gpt_response(result_text)

            # 添加原始文本
            parsed_data["raw_text"] = text

            return parsed_data

        except Exception as e:
            print(f"GPT解析失败: {e}")
            return self._generate_mock_parsing(text)

    def _parse_gpt_response(self, response: str) -> Dict[str, Any]:
        """解析GPT响应为结构化数据"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)

                # 验证必需字段
                required_fields = ["amount", "category", "description", "type", "date"]
                for field in required_fields:
                    if field not in parsed_data:
                        parsed_data[field] = self._get_default_value(field)

                # 确保金额是数字
                if isinstance(parsed_data.get("amount"), str):
                    try:
                        parsed_data["amount"] = float(parsed_data["amount"])
                    except (ValueError, TypeError):
                        parsed_data["amount"] = 0.0

                return parsed_data
            else:
                print("警告: 无法从GPT响应中提取JSON")
                return self._generate_fallback_parsing(response)

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return self._generate_fallback_parsing(response)

    def _generate_mock_parsing(self, text: str) -> Dict[str, Any]:
        """生成模拟解析结果"""
        import random
        from datetime import datetime

        # 简单的关键词匹配
        amount_match = re.search(r'(\d+(?:\.\d+)?)', text)
        amount = float(amount_match.group(1)) if amount_match else 25.0

        categories = {
            "餐饮": ["吃", "饭", "餐", "午餐", "晚餐", "早饭", "午饭"],
            "交通": ["打车", "公交", "地铁", "交通", "出行"],
            "购物": ["买", "购物", "超市", "商场"],
            "娱乐": ["电影", "娱乐", "游戏", "KTV"],
            "生活": ["水电", "房租", "话费", "生活"]
        }

        category = "其他"
        subcategory = "其他"

        for cat, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    category = cat
                    subcategory = keyword
                    break
            if category != "其他":
                break

        return {
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "description": text,
            "type": "expense",
            "payment_method": "微信支付",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "confidence": 0.7,
            "raw_text": text
        }

    def _generate_fallback_parsing(self, text: str) -> Dict[str, Any]:
        """生成备用解析结果"""
        from datetime import datetime

        return {
            "amount": 0.0,
            "category": "其他",
            "subcategory": "其他",
            "description": text,
            "type": "expense",
            "payment_method": "未知",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "confidence": 0.3,
            "raw_text": text
        }

    def _get_default_value(self, field: str) -> Any:
        """获取字段的默认值"""
        from datetime import datetime

        defaults = {
            "amount": 0.0,
            "category": "其他",
            "subcategory": "其他",
            "description": "",
            "type": "expense",
            "payment_method": "未知",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "confidence": 0.5
        }

        return defaults.get(field, "")


# 全局服务实例 - 延迟初始化
_gpt_parser_instance = None

def get_gpt_parser_service():
    """获取GPT解析服务实例（延迟初始化）"""
    global _gpt_parser_instance
    if _gpt_parser_instance is None:
        _gpt_parser_instance = GPTParserService()
    return _gpt_parser_instance

gpt_parser_service = get_gpt_parser_service()