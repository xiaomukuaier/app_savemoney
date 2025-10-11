"""
API路由定义
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import random
import time
from app.services.stt import stt_service
from app.services.nlp import nlp_service
from app.services.langgraph_workflow import langgraph_service
from app.services.feishu_api import get_feishu_service

router = APIRouter(prefix="/api/v1", tags=["api"])


# 模拟数据生成器
def generate_mock_expense() -> Dict[str, Any]:
    """生成模拟的记账数据"""
    categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '其他']
    subcategories = {
        '餐饮': ['早餐', '午餐', '晚餐', '零食', '饮料'],
        '交通': ['地铁', '公交', '打车', '加油', '停车'],
        '购物': ['服装', '日用品', '电子产品', '书籍'],
        '娱乐': ['电影', '游戏', '旅游', '运动'],
        '医疗': ['药品', '检查', '治疗'],
        '其他': ['其他']
    }

    descriptions = {
        '餐饮': ['公司楼下快餐', '外卖点餐', '餐厅用餐', '便利店购物'],
        '交通': ['地铁通勤', '打车回家', '加油费', '停车费'],
        '购物': ['购买衣服', '日用品采购', '电子产品', '书籍购买'],
        '娱乐': ['看电影', '玩游戏', '旅游消费', '运动健身'],
        '医疗': ['购买药品', '医院检查', '治疗费用'],
        '其他': ['其他消费']
    }

    category = random.choice(categories)
    subcategory_list = subcategories[category]
    subcategory = random.choice(subcategory_list)

    description_list = descriptions[category]
    description = random.choice(description_list)

    return {
        "amount": round(random.uniform(5, 200), 2),
        "category": category,
        "subcategory": subcategory,
        "description": description,
        "date": "2024-01-15",  # 固定日期用于测试
        "type": "expense",
        "payment_method": random.choice(['微信支付', '支付宝', '现金', '银行卡']),
        "confidence": round(random.uniform(0.7, 1.0), 2)
    }


@router.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    语音转文本API
    接收音频文件，返回解析后的记账信息
    """
    # 验证文件类型
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="请上传音频文件")

    try:
        # 读取音频文件
        audio_data = await file.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="音频文件为空")

        # 语音转文本
        transcription = await stt_service.transcribe_audio(audio_data, file.filename)

        if not transcription:
            raise HTTPException(status_code=500, detail="语音识别失败")

        # 使用LangGraph工作流解析文本，提取记账信息
        expense_data = await langgraph_service.process_expense(transcription)

        # 构建响应数据，包含分类建议和确认问题
        response_data = {
            "success": True,
            "data": expense_data,
            "message": "语音处理成功",
            "transcription": transcription,  # 返回原始识别文本用于调试
        }

        # 如果有分类建议，添加到响应中
        if expense_data.get("category_suggestions"):
            response_data["category_suggestions"] = expense_data.get("category_suggestions")
            response_data["has_suggestions"] = True

        # 如果需要确认，添加确认问题到响应中
        if expense_data.get("needs_confirmation"):
            response_data["needs_confirmation"] = True
            response_data["confirmation_questions"] = expense_data.get("confirmation_questions", [])

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"语音处理异常: {e}")
        # 如果处理失败，返回模拟数据
        expense_data = generate_mock_expense()
        return {
            "success": True,
            "data": expense_data,
            "message": "语音处理完成（模拟模式）"
        }


@router.post("/expenses")
async def create_expense(expense_data: Dict[str, Any]):
    """
    创建记账条目
    """
    # 验证必要字段
    required_fields = ['amount', 'category', 'description', 'date', 'type']
    for field in required_fields:
        if field not in expense_data:
            raise HTTPException(status_code=400, detail=f"缺少必要字段: {field}")

    try:
        # 保存到飞书表格
        feishu_service = get_feishu_service()
        save_success = feishu_service.save_expense_to_table(expense_data)

        if save_success:
            message = "记账成功"
            if not feishu_service.is_configured:
                message += "（模拟模式）"
        else:
            message = "记账保存失败"

        return {
            "success": save_success,
            "data": None,
            "message": message
        }

    except Exception as e:
        print(f"保存记账数据异常: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"记账保存异常: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "SaveMoney API",
        "version": "0.1.0"
    }


@router.get("/feishu/test")
async def test_feishu_connection():
    """测试飞书API连接"""
    try:
        feishu_service = get_feishu_service()
        is_connected = feishu_service.test_connection()

        return {
            "success": True,
            "data": {
                "is_configured": feishu_service.is_configured,
                "is_connected": is_connected
            },
            "message": "飞书API连接测试完成"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": f"飞书API连接测试异常: {str(e)}"
        }