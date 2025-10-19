"""
飞书API服务
使用官方lark-oapi SDK将记账数据保存到飞书多维表格
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from lark_oapi import Client
import lark_oapi.api.bitable.v1 as bitable_v1
import lark_oapi.api.auth.v3 as auth_v3
import lark_oapi.api.wiki.v2 as wiki_v2

# 加载环境变量
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)


class FeishuAPIService:
    """飞书API服务"""

    def __init__(self):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        self.table_id = os.getenv("FEISHU_TABLE_ID")
        self.node_token = os.getenv("FEISHU_NODE_TOKEN")  # 知识空间节点token
        self.app_token = os.getenv("FEISHU_APP_TOKEN")  # 多维表格的app_token
        self.space_id = os.getenv("FEISHU_SPACE_ID")  # 知识空间ID（可选）

        # 检查配置是否完整
        self.is_configured = all([self.app_id, self.app_secret, self.app_token])

        if not self.is_configured:
            print("警告: 飞书API配置不完整，使用模拟模式")
            return

        # 初始化飞书客户端
        self.client = Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .build()

        # 缓存从知识空间节点获取的app_token
        self._app_token_cache = None

    def _get_tenant_access_token(self) -> Optional[str]:
        """获取租户访问令牌"""
        if not self.is_configured:
            return None

        try:
            # 使用Client的token管理功能
            # Client会自动处理token的获取和刷新
            # 这里我们直接让Client处理，不需要手动获取
            return "client_managed"
        except Exception as e:
            print(f"获取租户访问令牌异常: {e}")
            return None

    def _get_app_token(self) -> Optional[str]:
        """获取多维表格的app_token"""
        # 直接使用配置的app_token
        if self.app_token:
            print(f"使用配置的app_token: {self.app_token}")
            return self.app_token

        # 如果没有配置app_token，尝试使用节点token
        if self.node_token:
            print(f"使用节点token作为app_token: {self.node_token}")
            return self.node_token

        # 最后尝试使用table_id
        print(f"使用table_id作为app_token: {self.table_id}")
        return self.table_id

    def save_expense_to_table(self, expense_data: Dict[str, Any]) -> bool:
        """
        将记账数据保存到飞书多维表格

        Args:
            expense_data: 记账数据字典

        Returns:
            保存是否成功
        """
        if not self.is_configured:
            print("飞书API未配置，使用模拟保存模式")
            print(f"模拟保存记账数据: {expense_data}")
            return True

        try:
            # 获取正确的app_token（考虑知识空间节点）
            app_token = self._get_app_token()
            if not app_token:
                print("无法获取有效的app_token")
                return False

            # 构建飞书表格记录
            record_data = self._build_record_data(expense_data)

            # 使用官方SDK批量创建记录（即使只有一条记录）
            request = (bitable_v1.BatchCreateAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(self.table_id)  # 使用配置的table_id作为表格ID
                .request_body(bitable_v1.BatchCreateAppTableRecordRequestBody.builder()
                    .records([{"fields": record_data}])
                    .build())
                .build())

            response = self.client.bitable.v1.app_table_record.batch_create(request)

            if response.success():
                print(f"记账数据已保存到飞书表格: {expense_data}")
                return True
            else:
                print(f"保存到飞书表格失败: {response.msg}")
                print(f"错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
                return False

        except Exception as e:
            print(f"保存到飞书表格异常: {e}")
            return False

    def _build_record_data(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建飞书表格记录数据

        根据新的表格字段结构，将记账数据转换为对应的格式
        新表格字段：
        - ID: 每条开支的唯一整数ID（自动生成）
        - 金额: 消费金额，数字类型
        - 日期: 消费发生的日期，日期类型
        - 分类: 文本类型
        - 子分类: 文本类型
        - 描述: 文本类型
        - 是否日常: 单选（是、否、待定）
        - 支付方式: 文本类型
        - 是否为必须开支: 单选（是、否、待定）
        - 原始文本: 文本类型
        """
        # 生成唯一ID（使用时间戳+随机数）
        import random
        record_id = int(time.time() * 1000) + random.randint(1000, 9999)

        # 使用用户的选择，如果没有提供则基于分类判断
        category = expense_data.get("category", "其他")

        # 是否日常 - 优先使用用户选择
        is_daily = expense_data.get("is_daily", "待定")
        if is_daily == "待定":
            # 如果没有用户选择，基于分类判断
            if category in ["餐饮", "交通", "日常用品"]:
                is_daily = "是"
            elif category in ["娱乐", "购物", "旅游"]:
                is_daily = "否"

        # 是否为必须开支 - 优先使用用户选择
        is_necessary = expense_data.get("is_necessary", "待定")
        if is_necessary == "待定":
            # 如果没有用户选择，基于分类判断
            if category in ["餐饮", "交通", "医疗"]:
                is_necessary = "是"
            elif category in ["娱乐", "购物", "旅游"]:
                is_necessary = "否"

        # 处理日期格式 - 飞书多维表格日期字段需要毫秒时间戳
        date_str = expense_data.get("date", "")
        if date_str:
            try:
                # 将日期字符串转换为毫秒时间戳
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_timestamp = int(date_obj.timestamp() * 1000)
            except:
                # 如果日期格式不正确，使用当前时间
                date_timestamp = int(time.time() * 1000)
        else:
            date_timestamp = int(time.time() * 1000)

        return {
            "ID": record_id,
            "金额": float(expense_data.get("amount", 0)),
            "日期": date_timestamp,
            "分类": category,
            "子分类": expense_data.get("subcategory", "其他"),
            "描述": expense_data.get("description", ""),
            "是否日常": is_daily,
            "支付方式": expense_data.get("payment_method", "微信支付"),
            "是否为必须开支": is_necessary,
            "原始文本": expense_data.get("raw_text", "")
        }

    def get_expense_records(self, limit: int = 100) -> Optional[list]:
        """
        从飞书表格获取记账记录

        Args:
            limit: 获取记录数量限制

        Returns:
            记账记录列表
        """
        if not self.is_configured:
            print("飞书API未配置，无法获取记录")
            return None

        try:
            # 获取正确的app_token
            app_token = self._get_app_token()
            if not app_token:
                print("无法获取有效的app_token")
                return None

            # 使用官方SDK获取记录列表
            request = (bitable_v1.ListAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(self.table_id)
                .page_size(limit)
                .build())

            response = self.client.bitable.v1.app_table_record.list(request)

            if response.success():
                records = response.data.items
                print(f"从飞书表格获取了 {len(records)} 条记录")
                return records
            else:
                print(f"从飞书表格获取记录失败: {response.msg}")
                print(f"错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
                return None

        except Exception as e:
            print(f"从飞书表格获取记录异常: {e}")
            return None

    def test_connection(self) -> bool:
        """测试飞书API连接"""
        if not self.is_configured:
            print("飞书API未配置")
            return False

        try:
            # 尝试获取租户访问令牌
            token = self._get_tenant_access_token()
            if not token:
                print("飞书API连接测试失败: 无法获取租户访问令牌")
                return False

            # 获取正确的app_token
            app_token = self._get_app_token()
            if not app_token:
                print("飞书API连接测试失败: 无法获取有效的app_token")
                return False

            # 尝试获取表格列表
            request = (bitable_v1.ListAppTableRequest.builder()
                .app_token(app_token)
                .build())

            response = self.client.bitable.v1.app_table.list(request)

            if response.success():
                tables = response.data.items
                print(f"飞书API连接测试成功，获取到 {len(tables)} 个表格")
                for table in tables:
                    print(f"  - {table.name} (ID: {table.table_id})")
                return True
            else:
                print(f"飞书API连接测试失败: {response.msg}")
                print(f"错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
                return False

        except Exception as e:
            print(f"飞书API连接测试异常: {e}")
            return False


# 全局飞书API服务实例
feishu_service = None

def get_feishu_service():
    """获取飞书API服务实例（延迟初始化）"""
    global feishu_service
    if feishu_service is None:
        feishu_service = FeishuAPIService()
    return feishu_service