"""
LangGraph工作流服务
使用LangGraph构建智能记账处理工作流
"""

from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os


class ExpenseState(TypedDict):
    """工作流状态定义"""
    raw_text: str
    extracted_data: Dict[str, Any]
    confidence: float
    needs_confirmation: bool
    confirmation_questions: List[str]
    final_expense: Dict[str, Any]


class LangGraphWorkflowService:
    """LangGraph工作流服务"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key":
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.llm = None

        # 构建工作流
        self.workflow = self._build_workflow()

    def _generate_suggestions(self, state: ExpenseState) -> ExpenseState:
        """生成分类建议节点"""
        extracted_data = state["extracted_data"]
        raw_text = state["raw_text"]

        # 生成分类建议
        category_suggestions = self._get_category_suggestions(raw_text, extracted_data)

        state["category_suggestions"] = category_suggestions
        state["has_suggestions"] = len(category_suggestions) > 0

        return state

    def _should_suggest(self, state: ExpenseState) -> str:
        """判断是否需要生成分类建议"""
        extracted_data = state["extracted_data"]

        # 如果置信度较低或分类为"其他"，需要建议
        confidence = extracted_data.get("confidence", 0)
        category = extracted_data.get("category", "其他")

        if confidence < 0.6 or category == "其他":
            return "suggest"
        else:
            return "continue"

    def _should_confirm(self, state: ExpenseState) -> str:
        """判断是否需要确认"""
        confidence = state["extracted_data"].get("confidence", 0)

        if confidence < 0.8:
            return "confirm"
        else:
            return "finalize"

    def _build_workflow(self):
        """构建LangGraph工作流"""
        workflow = StateGraph(ExpenseState)

        # 添加节点
        workflow.add_node("extract_basic_info", self._extract_basic_info)
        workflow.add_node("enhance_categorization", self._enhance_categorization)
        workflow.add_node("generate_suggestions", self._generate_suggestions)
        workflow.add_node("generate_confirmation", self._generate_confirmation)
        workflow.add_node("finalize_expense", self._finalize_expense)

        # 设置入口点
        workflow.set_entry_point("extract_basic_info")

        # 添加边
        workflow.add_edge("extract_basic_info", "enhance_categorization")
        workflow.add_conditional_edges(
            "enhance_categorization",
            self._should_suggest,
            {
                "suggest": "generate_suggestions",
                "continue": "generate_confirmation"
            }
        )
        workflow.add_conditional_edges(
            "generate_suggestions",
            self._should_confirm,
            {
                "confirm": "generate_confirmation",
                "finalize": "finalize_expense"
            }
        )
        workflow.add_edge("generate_confirmation", "finalize_expense")
        workflow.add_edge("finalize_expense", END)

        return workflow.compile()

    def _extract_basic_info(self, state: ExpenseState) -> ExpenseState:
        """提取基础信息节点"""
        raw_text = state["raw_text"]

        if self.llm:
            # 使用LLM提取基础信息
            prompt = f"""
            请从以下中文文本中提取记账信息：

            文本："{raw_text}"

            请提取以下信息：
            1. 金额（数字）
            2. 分类（餐饮、交通、购物、娱乐、医疗、其他）
            3. 描述（简洁描述消费内容）
            4. 支付方式（微信支付、支付宝、现金、银行卡）

            请以JSON格式返回，包含以下字段：
            - amount: 金额
            - category: 分类
            - description: 描述
            - payment_method: 支付方式
            - confidence: 置信度（0-1之间）
            """

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                # 这里简化处理，实际应该解析LLM的JSON响应
                extracted_data = self._parse_llm_response(response.content)
            except Exception as e:
                print(f"LLM提取失败，使用基础解析: {e}")
                extracted_data = self._fallback_extraction(raw_text)
        else:
            # 没有LLM时使用基础解析
            extracted_data = self._fallback_extraction(raw_text)

        state["extracted_data"] = extracted_data
        return state

    def _enhance_categorization(self, state: ExpenseState) -> ExpenseState:
        """增强分类节点"""
        extracted_data = state["extracted_data"]

        if self.llm and extracted_data.get("confidence", 0) < 0.8:
            # 当置信度较低时，使用LLM增强分类
            prompt = f"""
            请帮助确认以下记账信息的分类是否准确：

            原始文本："{state['raw_text']}"
            当前提取：{extracted_data}

            请评估分类准确性并提供改进建议。
            """

            try:
                response = self.llm.invoke([HumanMessage(content=prompt)])
                # 这里可以解析LLM的响应来调整分类
                enhanced_data = self._enhance_with_llm(extracted_data, response.content)
                state["extracted_data"] = enhanced_data
            except Exception as e:
                print(f"LLM增强分类失败: {e}")

        return state

    def _generate_confirmation(self, state: ExpenseState) -> ExpenseState:
        """生成确认问题节点"""
        extracted_data = state["extracted_data"]

        # 生成需要确认的问题
        questions = []

        if extracted_data.get("confidence", 0) < 0.7:
            questions.append("金额是否正确？")

        if extracted_data.get("category") == "其他":
            questions.append("请确认消费分类")

        if len(extracted_data.get("description", "")) < 3:
            questions.append("请提供更详细的消费描述")

        state["confirmation_questions"] = questions
        state["needs_confirmation"] = len(questions) > 0

        return state

    def _finalize_expense(self, state: ExpenseState) -> ExpenseState:
        """最终确定记账信息节点"""
        from datetime import datetime

        extracted_data = state["extracted_data"]

        # 构建最终的记账信息
        final_expense = {
            "amount": extracted_data.get("amount", 0),
            "category": extracted_data.get("category", "其他"),
            "subcategory": self._get_subcategory(extracted_data.get("category")),
            "description": extracted_data.get("description", "日常消费"),
            "date": extracted_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "type": extracted_data.get("type", "expense"),
            "payment_method": extracted_data.get("payment_method", "微信支付"),
            "confidence": extracted_data.get("confidence", 0.5),
            "needs_confirmation": state.get("needs_confirmation", False),
            "confirmation_questions": state.get("confirmation_questions", []),
            "raw_text": state["raw_text"]
        }

        # 如果有分类建议，添加到最终结果中
        if "category_suggestions" in state and state.get("category_suggestions"):
            final_expense["category_suggestions"] = state["category_suggestions"]
            final_expense["has_suggestions"] = state.get("has_suggestions", False)

        state["final_expense"] = final_expense
        return state

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        import json
        import re

        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)

                # 验证必需字段
                required_fields = ['amount', 'category', 'description', 'payment_method', 'confidence']
                if all(field in parsed_data for field in required_fields):
                    return parsed_data

            # 如果JSON解析失败，使用正则表达式提取
            amount_match = re.search(r'"amount"\s*:\s*(\d+(?:\.\d+)?)', response)
            category_match = re.search(r'"category"\s*:\s*"([^"]+)"', response)
            description_match = re.search(r'"description"\s*:\s*"([^"]+)"', response)
            payment_match = re.search(r'"payment_method"\s*:\s*"([^"]+)"', response)
            confidence_match = re.search(r'"confidence"\s*:\s*(\d+(?:\.\d+)?)', response)

            extracted_data = {
                "amount": float(amount_match.group(1)) if amount_match else 0.0,
                "category": category_match.group(1) if category_match else "其他",
                "description": description_match.group(1) if description_match else "日常消费",
                "payment_method": payment_match.group(1) if payment_match else "微信支付",
                "confidence": float(confidence_match.group(1)) if confidence_match else 0.5
            }

            return extracted_data

        except Exception as e:
            print(f"LLM响应解析失败: {e}")
            # 解析失败时使用基础解析
            return self._fallback_extraction("")

    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """基础解析回退"""
        from app.services.nlp import nlp_service
        from datetime import datetime

        # 使用现有的NLP服务进行解析
        expense_data = nlp_service.parse_expense_text(text)

        return {
            "amount": expense_data.get("amount", 0),
            "category": expense_data.get("category", "其他"),
            "subcategory": expense_data.get("subcategory", "其他"),
            "description": expense_data.get("description", "日常消费"),
            "date": expense_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "type": expense_data.get("type", "expense"),
            "payment_method": expense_data.get("payment_method", "微信支付"),
            "confidence": expense_data.get("confidence", 0.5),
            "needs_confirmation": False,
            "confirmation_questions": [],
            "raw_text": text
        }

    def _enhance_with_llm(self, data: Dict[str, Any], llm_response: str) -> Dict[str, Any]:
        """使用LLM响应增强数据"""
        import re

        try:
            # 从LLM响应中提取改进建议
            if "分类" in llm_response or "category" in llm_response.lower():
                # 提取建议的分类
                category_suggestions = []

                # 查找可能的分类建议
                categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '其他']
                for category in categories:
                    if category in llm_response:
                        category_suggestions.append(category)

                # 如果有明确的分类建议，更新数据
                if len(category_suggestions) == 1:
                    data["category"] = category_suggestions[0]
                    data["confidence"] = min(data.get("confidence", 0.5) + 0.2, 1.0)
                    print(f"LLM建议分类: {category_suggestions[0]}")

            # 检查是否有金额修正
            amount_matches = re.findall(r'(\d+(?:\.\d+)?)[元块]', llm_response)
            if amount_matches:
                try:
                    suggested_amount = float(amount_matches[0])
                    if abs(suggested_amount - data.get("amount", 0)) > 5:
                        data["amount"] = suggested_amount
                        data["confidence"] = min(data.get("confidence", 0.5) + 0.1, 1.0)
                        print(f"LLM建议金额: {suggested_amount}")
                except ValueError:
                    pass

            return data

        except Exception as e:
            print(f"LLM增强处理失败: {e}")
            return data

    def _get_category_suggestions(self, text: str, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成分类建议"""
        suggestions = []

        # 使用LLM生成智能建议
        if self.llm:
            try:
                prompt = f"""
                请分析以下消费文本，提供可能的分类建议：

                文本："{text}"
                当前分类：{current_data.get('category', '其他')}
                当前置信度：{current_data.get('confidence', 0)}

                请提供2-3个最可能的分类建议，按可能性从高到低排序。
                每个建议包含：
                - category: 分类名称
                - confidence: 置信度（0-1）
                - reason: 建议理由

                请以JSON数组格式返回。
                """

                response = self.llm.invoke([HumanMessage(content=prompt)])
                suggestions = self._parse_suggestion_response(response.content)
            except Exception as e:
                print(f"LLM分类建议生成失败: {e}")

        # 如果没有LLM建议，使用基于关键词的建议
        if not suggestions:
            suggestions = self._get_keyword_based_suggestions(text)

        return suggestions

    def _parse_suggestion_response(self, response: str) -> List[Dict[str, Any]]:
        """解析LLM的分类建议响应"""
        import json
        import re

        try:
            # 尝试提取JSON数组
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                suggestions = json.loads(json_str)

                # 验证建议格式
                valid_suggestions = []
                for suggestion in suggestions:
                    if all(key in suggestion for key in ['category', 'confidence', 'reason']):
                        valid_suggestions.append(suggestion)

                return valid_suggestions
        except Exception as e:
            print(f"LLM建议解析失败: {e}")

        return []

    def _get_keyword_based_suggestions(self, text: str) -> List[Dict[str, Any]]:
        """基于关键词的分类建议"""
        from app.services.nlp import nlp_service

        # 使用NLP服务的关键词匹配
        categories = ['餐饮', '交通', '购物', '娱乐', '医疗']
        suggestions = []

        for category in categories:
            # 计算该分类的匹配分数
            score = 0
            for keyword in nlp_service.category_keywords[category]:
                if keyword in text:
                    score += len(keyword) * 0.1

            if score > 0:
                suggestions.append({
                    "category": category,
                    "confidence": min(score / 10, 0.9),  # 归一化到0-0.9
                    "reason": f"文本中包含'{category}'相关关键词"
                })

        # 按置信度排序
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        return suggestions[:3]  # 返回前3个建议

    def _get_subcategory(self, category: str) -> str:
        """根据分类获取子分类"""
        subcategories = {
            "餐饮": "正餐",
            "交通": "交通费",
            "购物": "购物",
            "娱乐": "娱乐",
            "医疗": "医疗",
            "其他": "其他"
        }
        return subcategories.get(category, "其他")

    async def process_expense(self, text: str) -> Dict[str, Any]:
        """
        使用LangGraph工作流处理记账文本

        Args:
            text: 语音识别文本

        Returns:
            处理后的记账信息
        """
        # 初始化状态
        initial_state: ExpenseState = {
            "raw_text": text,
            "extracted_data": {},
            "confidence": 0.0,
            "needs_confirmation": False,
            "confirmation_questions": [],
            "final_expense": {}
        }

        try:
            # 执行工作流
            if self.llm:
                final_state = self.workflow.invoke(initial_state)
                return final_state["final_expense"]
            else:
                # 没有LLM时使用基础处理
                return self._fallback_extraction(text)
        except Exception as e:
            print(f"LangGraph工作流执行失败: {e}")
            # 工作流失败时回退到基础解析
            return self._fallback_extraction(text)


# 全局工作流服务实例
langgraph_service = LangGraphWorkflowService()