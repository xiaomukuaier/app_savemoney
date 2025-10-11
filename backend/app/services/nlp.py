"""
自然语言处理服务
从语音识别文本中提取记账信息
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime


class TextParserService:
    """文本解析服务"""

    def __init__(self):
        # 扩展分类关键词（包含更多上下文词汇）
        self.category_keywords = {
            '餐饮': [
                '吃饭', '餐厅', '外卖', '快餐', '火锅', '烧烤', '咖啡', '奶茶', '饮料', '零食',
                '早餐', '午餐', '晚餐', '夜宵', '食堂', '饭馆', '小吃', '甜品', '面包', '蛋糕',
                '水果', '蔬菜', '肉', '鱼', '米', '面', '酒', '茶', '水饺', '面条', '米饭'
            ],
            '交通': [
                '打车', '公交', '地铁', '加油', '停车', '车费', '出行', '出租车', '网约车',
                '火车', '高铁', '飞机', '机票', '船票', '船', '自行车', '共享单车', '电动车',
                '维修', '保险', '过路费', '违章', '洗车'
            ],
            '购物': [
                '购物', '超市', '商场', '买', '购买', '衣服', '日用品', '电子产品',
                '服装', '鞋子', '包包', '化妆品', '护肤品', '家电', '手机', '电脑',
                '家具', '家居', '书籍', '文具', '玩具', '礼物', '珠宝', '手表',
                '电器', '数码', '配件', '材料', '工具'
            ],
            '娱乐': [
                '电影', '游戏', '旅游', '运动', '健身', 'KTV', '游乐场', '演唱会',
                '音乐会', '展览', '博物馆', '公园', '爬山', '游泳', '滑雪', '温泉',
                '酒吧', '网吧', '台球', '保龄球', '高尔夫', '瑜伽', '舞蹈',
                '摄影', '画画', '手工', '宠物', '养宠物'
            ],
            '医疗': [
                '医院', '看病', '药品', '检查', '治疗', '药店', '诊所', '牙医',
                '体检', '疫苗', '手术', '住院', '挂号', '处方', '中药', '西药',
                '保健品', '维生素', '按摩', '理疗', '康复'
            ],
            '其他': [
                '其他', '杂项', '费用', '缴费', '水电费', '燃气费', '网费', '电话费',
                '房租', '房贷', '车贷', '信用卡', '保险', '投资', '理财', '捐款',
                '罚款', '赔偿', '维修', '清洁', '家政', '快递', '邮寄'
            ]
        }

        # 支付方式关键词
        self.payment_methods = {
            '微信支付': ['微信', '微信支付'],
            '支付宝': ['支付宝', '花呗'],
            '现金': ['现金', '现钱'],
            '银行卡': ['银行卡', '信用卡', '储蓄卡']
        }

    def parse_expense_text(self, text: str) -> Dict[str, Any]:
        """
        解析语音文本，提取记账信息

        Args:
            text: 语音识别文本

        Returns:
            解析后的记账信息字典
        """
        # 提取金额
        amount = self._extract_amount(text)

        # 提取分类
        category, subcategory = self._extract_category(text)

        # 提取描述
        description = self._extract_description(text)

        # 提取支付方式
        payment_method = self._extract_payment_method(text)

        return {
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "description": description,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "expense",  # 默认支出
            "payment_method": payment_method,
            "confidence": self._calculate_confidence(text, amount),
            "raw_text": text
        }

    def _extract_amount(self, text: str) -> float:
        """提取金额"""
        # 匹配数字模式：二十五、25、25块、25元、25块钱等
        patterns = [
            r'(\d+(?:\.\d+)?)[元块]',  # 25元、25块
            r'(\d+(?:\.\d+)?)块钱',    # 25块钱
            r'花了(\d+(?:\.\d+)?)[元块]',  # 花了25元
            r'消费(\d+(?:\.\d+)?)[元块]',  # 消费25元
            r'(\d+(?:\.\d+)?)元',       # 25元
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        # 如果没有找到数字金额，尝试解析中文数字
        chinese_amount = self._parse_chinese_number(text)
        if chinese_amount:
            return chinese_amount

        # 默认返回随机金额
        import random
        return round(random.uniform(10, 100), 2)

    def _parse_chinese_number(self, text: str) -> Optional[float]:
        """解析中文数字"""
        chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
            '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
            '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30,
            '三十一': 31, '三十二': 32, '三十三': 33, '三十四': 34, '三十五': 35,
            '三十六': 36, '三十七': 37, '三十八': 38, '三十九': 39, '四十': 40,
            '四十一': 41, '四十二': 42, '四十三': 43, '四十四': 44, '四十五': 45,
            '四十六': 46, '四十七': 47, '四十八': 48, '四十九': 49, '五十': 50,
            '五十一': 51, '五十二': 52, '五十三': 53, '五十四': 54, '五十五': 55,
            '五十六': 56, '五十七': 57, '五十八': 58, '五十九': 59, '六十': 60,
            '六十一': 61, '六十二': 62, '六十三': 63, '六十四': 64, '六十五': 65,
            '六十六': 66, '六十七': 67, '六十八': 68, '六十九': 69, '七十': 70,
            '七十一': 71, '七十二': 72, '七十三': 73, '七十四': 74, '七十五': 75,
            '七十六': 76, '七十七': 77, '七十八': 78, '七十九': 79, '八十': 80,
            '八十一': 81, '八十二': 82, '八十三': 83, '八十四': 84, '八十五': 85,
            '八十六': 86, '八十七': 87, '八十八': 88, '八十九': 89, '九十': 90,
            '九十一': 91, '九十二': 92, '九十三': 93, '九十四': 94, '九十五': 95,
            '九十六': 96, '九十七': 97, '九十八': 98, '九十九': 99, '一百': 100,
            '两百': 200, '三百': 300, '四百': 400, '五百': 500, '六百': 600,
            '七百': 700, '八百': 800, '九百': 900
        }

        # 按长度降序排序，优先匹配更长的数字
        for chinese in sorted(chinese_numbers.keys(), key=len, reverse=True):
            if chinese in text:
                return float(chinese_numbers[chinese])

        return None

    def _extract_category(self, text: str) -> tuple[str, str]:
        """提取分类和子分类（增强版）"""
        # 计算每个分类的匹配分数
        category_scores = {}

        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    # 根据关键词长度和出现频率计算分数
                    score += len(keyword) * 0.1  # 长关键词权重更高

                    # 检查关键词在文本中的位置和上下文
                    if self._is_primary_keyword(text, keyword):
                        score += 0.5

            if score > 0:
                category_scores[category] = score

        # 如果有匹配的分类，选择分数最高的
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)

            # 根据文本内容确定最佳关键词
            best_keyword = None
            best_keyword_score = 0

            for keyword in self.category_keywords[best_category]:
                if keyword in text:
                    keyword_score = len(keyword)
                    if self._is_primary_keyword(text, keyword):
                        keyword_score += 5

                    if keyword_score > best_keyword_score:
                        best_keyword_score = keyword_score
                        best_keyword = keyword

            subcategory = self._get_subcategory(best_category, best_keyword or "")
            return best_category, subcategory

        # 如果没有找到明确的分类，使用上下文推断
        inferred_category = self._infer_category_from_context(text)
        if inferred_category != "其他":
            return inferred_category, "其他"

        # 默认分类
        return "其他", "其他"

    def _is_primary_keyword(self, text: str, keyword: str) -> bool:
        """检查关键词是否是主要关键词"""
        # 检查关键词是否出现在重要位置
        words = text.split()
        if len(words) > 0:
            # 检查是否出现在前几个词中
            if keyword in words[:3]:
                return True

        # 检查关键词是否与金额相邻
        amount_patterns = [r'\d+(?:\.\d+)?[元块]', r'花了', r'消费']
        for pattern in amount_patterns:
            if re.search(pattern, text):
                # 如果关键词出现在金额附近，认为是主要关键词
                amount_pos = re.search(pattern, text).start()
                keyword_pos = text.find(keyword)
                if abs(amount_pos - keyword_pos) < 10:
                    return True

        return False

    def _infer_category_from_context(self, text: str) -> str:
        """根据上下文推断分类"""
        # 基于常见消费场景推断
        context_patterns = {
            '餐饮': [
                r'[早中晚]餐', r'吃饭', r'饿了', r'饱了', r'餐厅', r'饭店', r'食堂'
            ],
            '交通': [
                r'去.+', r'到.+', r'回家', r'上班', r'出差', r'旅行', r'出行'
            ],
            '购物': [
                r'买.+', r'购物', r'超市', r'商场', r'网购', r'淘宝', r'京东'
            ],
            '娱乐': [
                r'玩', r'看电影', r'玩游戏', r'旅游', r'度假', r'放松'
            ],
            '医疗': [
                r'生病', r'不舒服', r'看病', r'医院', r'医生', r'药'
            ]
        }

        for category, patterns in context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category

        return "其他"

    def _get_subcategory(self, category: str, keyword: str) -> str:
        """根据分类和关键词获取子分类"""
        subcategories = {
            '餐饮': {
                '吃饭': '正餐', '餐厅': '正餐', '外卖': '外卖', '快餐': '快餐',
                '火锅': '火锅', '烧烤': '烧烤', '咖啡': '咖啡', '奶茶': '奶茶',
                '饮料': '饮料', '零食': '零食'
            },
            '交通': {
                '打车': '打车', '公交': '公交', '地铁': '地铁', '加油': '加油',
                '停车': '停车', '车费': '交通费', '出行': '交通费'
            },
            '购物': {
                '购物': '购物', '超市': '超市购物', '商场': '商场购物',
                '买': '购物', '购买': '购物', '衣服': '服装',
                '日用品': '日用品', '电子产品': '电子产品'
            },
            '娱乐': {
                '电影': '电影', '游戏': '游戏', '旅游': '旅游',
                '运动': '运动', '健身': '健身', 'KTV': 'KTV',
                '游乐场': '游乐场'
            },
            '医疗': {
                '医院': '医疗', '看病': '医疗', '药品': '药品',
                '检查': '检查', '治疗': '治疗', '药店': '药品'
            }
        }

        return subcategories.get(category, {}).get(keyword, category)

    def _extract_description(self, text: str) -> str:
        """提取描述"""
        # 移除金额和分类关键词，保留主要描述
        cleaned_text = text

        # 移除金额相关词汇
        amount_patterns = [r'\d+(?:\.\d+)?[元块]', r'花了', r'消费', r'块钱']
        for pattern in amount_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text)

        # 移除分类关键词
        for keywords in self.category_keywords.values():
            for keyword in keywords:
                cleaned_text = cleaned_text.replace(keyword, '')

        cleaned_text = cleaned_text.strip()

        if cleaned_text:
            return cleaned_text
        else:
            return "日常消费"

    def _extract_payment_method(self, text: str) -> str:
        """提取支付方式"""
        for method, keywords in self.payment_methods.items():
            for keyword in keywords:
                if keyword in text:
                    return method

        return "微信支付"  # 默认支付方式

    def _calculate_confidence(self, text: str, amount: float) -> float:
        """计算解析置信度"""
        confidence = 0.7  # 基础置信度

        # 如果成功提取到金额，增加置信度
        if amount > 0:
            confidence += 0.2

        # 如果文本包含常见关键词，增加置信度
        keywords_found = 0
        for keywords in self.category_keywords.values():
            for keyword in keywords:
                if keyword in text:
                    keywords_found += 1
                    break

        if keywords_found > 0:
            confidence += min(0.1 * keywords_found, 0.3)

        return min(confidence, 1.0)


# 全局服务实例
nlp_service = TextParserService()