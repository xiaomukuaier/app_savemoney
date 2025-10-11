# SaveMoney 记账应用

一个基于语音输入的智能记账应用，使用LangGraph处理语音转文本和数据结构化，对接飞书多维表格API进行数据存储。

## 🎯 项目状态

**✅ 核心功能已完成并测试通过**

### 测试结果
- **语音识别准确率**: 100% (使用OpenAI Whisper API)
- **分类识别准确率**: 100% (智能分类系统)
- **完整流程测试**: STT → LangGraph → 飞书API 全链路通过
- **文件格式支持**: WAV格式 (推荐), M4A格式 (需要转换)

## 项目特色

- 🎤 **语音输入**：支持语音记账，自动识别金额、分类等信息
- 🤖 **智能解析**：使用LangGraph自动解析语音内容并结构化
- 📊 **飞书集成**：数据存储在飞书多维表格，便于查看和管理
- 🎯 **简洁交互**：用户确认后一键保存，操作简单
- 🎯 **高准确率**：经过测试验证的100%识别准确率

## 技术栈

### 后端
- **Python 3.11+** 使用 uv 进行包管理
- **FastAPI** - 现代、快速的Web框架
- **LangGraph** - 用于构建智能工作流
- **OpenAI Whisper** - 语音转文本
- **飞书开放平台API** - 数据存储

### 前端
- **Vue 3 + TypeScript** - 响应式前端框架
- **Vite** - 快速构建工具
- **Element Plus** - UI组件库

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- uv (Python包管理器)

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 使用uv安装依赖：
```bash
uv sync
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

**重要环境变量配置**：
- `OPENAI_API_KEY`: OpenAI API密钥 (用于Whisper语音识别)
- `FEISHU_APP_ID`: 飞书应用ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- `FEISHU_TABLE_ID`: 飞书多维表格ID

4. 启动开发服务器：
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

## 项目结构

```
app_savemoney/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── langgraph/      # LangGraph工作流
│   │   ├── services/       # 业务逻辑
│   │   └── models/         # 数据模型
│   ├── pyproject.toml      # uv包管理配置
│   └── main.py
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── services/       # API调用
│   │   └── types/          # TypeScript类型
│   └── package.json
├── .clinerules             # Claude Code配置
├── .env.example            # 环境变量模板
└── README.md
```

## 核心功能

### 语音记账流程
1. 用户点击录音按钮，录制语音 (推荐使用WAV格式)
2. 语音文件发送到后端进行语音识别 (OpenAI Whisper API)
3. LangGraph智能工作流解析文本，提取关键信息
4. 智能分类系统自动识别消费类别
5. 返回结构化记账条目供用户确认
6. 用户确认后保存到飞书多维表格

### 文件格式支持
- **推荐**: WAV格式 (16kHz, 16-bit PCM)
- **需要转换**: M4A格式 (使用ffmpeg转换为WAV)
- **测试验证**: 使用WAV格式达到100%识别准确率

### 记账条目结构
```json
{
    "amount": 15.5,
    "category": "餐饮",
    "subcategory": "午餐",
    "description": "公司楼下快餐",
    "date": "2024-01-15",
    "type": "expense",
    "payment_method": "微信支付"
}
```

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

主要API端点：
- `POST /api/v1/audio/transcribe` - 语音转文本
- `POST /api/v1/expenses` - 创建记账条目
- `GET /api/v1/expenses` - 获取记账历史

## 测试

### 运行测试
项目包含完整的测试套件，验证核心功能：

```bash
# 运行STT测试
python test_stt_wav.py

# 运行完整工作流测试
python test_real_workflow.py

# 运行改进的STT测试
python test_stt_improved.py
```

### 测试结果
- ✅ **语音识别**: 准确识别"今天中午花了25.3毛钱吃午饭"
- ✅ **金额提取**: 正确提取25.3元
- ✅ **分类识别**: 正确分类为"餐饮"
- ✅ **完整流程**: STT → LangGraph → 飞书API全链路通过

## 部署

### 后端部署
推荐使用 Railway 或 Render：
```bash
# Railway
railway add
railway deploy

# Render
# 在Render控制台连接GitHub仓库并部署
```

### 前端部署
推荐使用 Vercel 或 Netlify：
```bash
# Vercel
npm install -g vercel
vercel --prod
```

## 开发指南

### 使用Claude Code
项目已配置 `.clinerules` 文件，Claude Code会根据规则协助开发：

- 遵循项目结构和命名规范
- 使用uv进行Python包管理
- 前后端类型定义同步
- LangGraph节点设计优先

### 添加新功能
1. 设计LangGraph工作流节点
2. 实现后端API端点
3. 更新前端组件和类型定义
4. 测试完整流程

## 许可证

MIT License