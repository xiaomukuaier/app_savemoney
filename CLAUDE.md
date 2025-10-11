# SaveMoney 记账应用 - Claude Code 规则

## 项目概述
这是一个基于语音输入的智能记账应用，使用LangGraph处理语音转文本和数据结构化，对接飞书多维表格API进行数据存储。

## 技术栈

### 后端
- **语言**: Python 3.11+
- **核心框架**: LangGraph (用于处理语音输入和数据流)
- **Web框架**: FastAPI
- **数据库**: 飞书多维表格API
- **语音识别**: OpenAI Whisper API / 其他STT服务
- **部署**: Railway / Render / Vercel

### 前端
- **框架**: Vue 3 + TypeScript (或 React + TypeScript)
- **构建工具**: Vite
- **UI组件**: Element Plus / Ant Design Vue
- **状态管理**: Pinia (Vue) / Zustand (React)
- **部署**: Vercel / Netlify / Cloudflare Pages

## 项目结构
```
app_savemoney/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── langgraph/      # LangGraph工作流
│   │   ├── services/       # 业务逻辑
│   │   │   ├── stt.py      # 语音转文本
│   │   │   ├── feishu.py   # 飞书API集成
│   │   │   └── nlp.py      # 自然语言处理
│   │   └── models/         # 数据模型
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── stores/        # 状态管理
│   │   ├── services/      # API调用
│   │   └── types/         # TypeScript类型
│   ├── public/
│   └── package.json
├── .env.example           # 环境变量模板
├── .gitignore
└── README.md
```

## 开发规范

### 代码风格
- **Python**: 遵循PEP 8，使用black格式化，类型提示使用typing
- **TypeScript/JavaScript**: 使用ESLint + Prettier，严格模式
- **命名约定**:
  - Python: snake_case (函数/变量), PascalCase (类)
  - TypeScript: camelCase (函数/变量), PascalCase (组件/类/接口)

### Git提交规范
- feat: 新功能
- fix: 修复bug
- refactor: 重构
- docs: 文档更新
- style: 代码格式调整
- test: 测试相关

### API设计原则
- RESTful API设计
- 统一的响应格式: `{"success": boolean, "data": any, "message": string}`
- 使用HTTP状态码表示请求结果
- API路径前缀: `/api/v1/`

### 环境变量
所有敏感信息（API密钥、数据库凭证等）必须通过环境变量配置：
- `FEISHU_APP_ID`: 飞书应用ID
- `FEISHU_APP_SECRET`: 飞书应用密钥
- `FEISHU_TABLE_ID`: 飞书多维表格ID
- `OPENAI_API_KEY`: OpenAI API密钥（用于Whisper）
- `LANGCHAIN_API_KEY`: LangChain API密钥（如需要）

## 核心功能流程

### 1. 语音输入处理
```
用户语音输入 → STT转文本 → LangGraph解析 → 提取关键信息 → 生成记账条目草稿
```

### 2. 记账条目结构
```python
{
    "amount": float,           # 金额
    "category": str,           # 分类（大类）
    "subcategory": str,        # 子分类
    "description": str,        # 描述
    "date": str,              # 日期 (YYYY-MM-DD)
    "type": "expense|income",  # 支出/收入
    "payment_method": str,     # 支付方式（可选）
}
```

### 3. 用户交互流程
1. 用户点击录音按钮，录制语音
2. 后端处理语音并返回结构化条目
3. 前端展示条目，允许用户：
   - 确认金额和描述
   - 从下拉列表选择或语音补充分类信息
4. 用户确认后提交到飞书表格

## LangGraph工作流设计

### 主要节点
1. **AudioInput**: 接收音频输入
2. **STTNode**: 语音转文本
3. **ParseNode**: 解析文本提取信息
4. **ValidateNode**: 验证数据完整性
5. **ConfirmNode**: 等待用户确认
6. **SaveNode**: 保存到飞书

### 状态管理
- 使用LangGraph的状态机跟踪每个记账流程
- 支持部分信息缺失时的循环补充

## 飞书API集成要点

### 多维表格操作
- 使用飞书开放平台的多维表格API
- 主要操作：
  - 新增记录 (POST)
  - 查询记录 (GET) - 用于统计和历史查询
  - 更新记录 (PATCH) - 用于修改错误条目
  - 获取字段列表 - 用于动态生成分类选项

### 认证方式
- 使用tenant_access_token (企业自建应用)
- 实现token自动刷新机制

## 测试策略
- 后端单元测试：pytest
- API测试：使用FastAPI的TestClient
- 前端测试：Vitest + Vue Test Utils
- E2E测试：Playwright（如需要）

## 部署注意事项
- 使用Docker容器化（可选）
- 环境变量通过平台提供的secrets管理
- 配置CORS允许前端域名访问
- 使用HTTPS确保语音数据传输安全

## 性能优化
- 语音文件压缩后再上传
- 使用流式传输减少等待时间
- LangGraph节点使用异步处理
- 飞书API调用添加重试机制

## 安全考虑
- API密钥不提交到版本控制
- 实现基础的请求限流
- 飞书webhook验证签名
- 输入数据验证和清理

## Claude Code使用提示
- 添加新功能时，先设计LangGraph节点和数据流
- 修改API时，同步更新前后端的类型定义
- 集成第三方服务前，先在独立文件中测试
- 遵循项目结构，不要创建不必要的嵌套目录
- 优先使用现有的工具库，避免重复造轮子
